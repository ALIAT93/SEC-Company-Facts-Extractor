from PySide6.QtWidgets import  QToolTip, QSplitter, QScrollArea, QWidget, QListWidget, QTableWidgetItem,QTableWidget,QSpacerItem, QProgressBar, QSizePolicy, QAbstractItemView, QSizePolicy, QComboBox, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, QLineEdit, QFileDialog, QLabel, QPushButton, QMessageBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries,QValueAxis,QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime, QPointF
from PySide6.QtGui import QPainter
from SEC_API_Filling_Class.Filling_Links import Filling_Links, Filling_Links_Intial

import sys
import threading
import requests
import json
import configparser
import sqlite3

# Create a class for the main platform UI
class Platform(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # Define these attributes before using them
        self.selected_companies_var = QTextEdit()
        self.selected_cik_str_var = QTextEdit()
        self.selected_ticker_str_var = QTextEdit()
        
        # Create the terminal widget
        self.terminal_widget = QTextEdit()
        self.terminal_widget.setReadOnly(True)  # Set read-only property

        self.Intialize_all_Layouts()
        self.Intialize_Side_Bar_Column_1()
        self.phase1_init_company_selection()
        self.phase1_init_user_input()
        self.phase1_init_tab_view()
        self.phase1_Intialize_Debugger_Column()
        
        self.frames_visible = True

        self.phase2_init_column2()
        self.phase2_init_column3()

        self.file_Format_var.setCurrentText("Excel")
        
        # Add a progress bar to the UI
        self.progress_bar = QProgressBar()
        self.selectedCompanies_Column_3.addWidget(self.progress_bar)
        self.progress_bar.setVisible(False)  # Initially hidden
        
        self.List_Box_Company_Selection.currentItemChanged.connect(self.on_select_company)
        self.List_Box_Company_Selection.itemSelectionChanged.connect(self.on_select_company)
        self.Search_Entry_Company_Letter_Word.textChanged.connect(self.search_company)
        self.load_user_settings()   
        self.load_json_data()


        # Create instances of your redirectors
        self.stdout_redirector = StdoutRedirector(text_widget=self.terminal_widget, progress_bar=self.progress_bar)
        self.stderr_redirector = StderrRedirector(text_widget=self.terminal_widget, progress_bar=self.progress_bar)

        # Redirect sys.stdout and sys.stderr to your redirectors
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector

        
    def Intialize_all_Layouts(self):
        """
        Initialize the main layouts of the platform UI.
        Returns:
            None
        """
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        layout_names = [
            "sideBar_Column_1",
            "Company_Selection_Column_2",
            "selectedCompanies_Column_3",
            "debugger_Column_4",
            "phase2_FileSection_ListViewer_Column_2",
            "phase2_graph_Machine_Column_3",
            "Phase2_Debugger_Text_Column4",
        ]

        for layout_name in layout_names:
            layout_widget = QWidget()  # Create a widget to hold the layout
            layout = QVBoxLayout(layout_widget)
            setattr(self, layout_name, layout)
            layout.setContentsMargins(5, 5, 5, 5)
            main_layout.addWidget(layout_widget)  # Add the layout widget to the main layout
            
        self.phase2_FileSection_ListViewer_Column_2.parentWidget().setVisible(False)  # Initially hide the layout
        self.phase2_graph_Machine_Column_3.parentWidget().setVisible(False)  # Initially hide the layout
        self.Phase2_Debugger_Text_Column4.parentWidget().setVisible(False)  # Initially hide the layout
        
        self.phase2_FileSection_ListViewer_Column_2.parentWidget().setMaximumWidth(500)
        self.sideBar_Column_1.parentWidget().setMaximumWidth(100)

    def Intialize_Side_Bar_Column_1(self):
        """
        Initialize the side bar of the platform UI with buttons and a spacer.
        Buttons:
        - "ML Toggle": Toggles the visibility of specific UI components related to Machine Learning.
        Returns:
            None
        """
        
        buttons = [
            ("ML Toggle", self.Button_FunctiOn_Switch_To_Machine_Learning),
            ("Phase 2", self.sidebar_button_event),  # Add handler if needed
            ("Phase 3", self.sidebar_button_event)   # Add handler if needed
        ]
        for button_text, button_handler in buttons:
            self.create_button(button_text, self.sideBar_Column_1, button_handler)
            
        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sideBar_Column_1.addItem(spacer_bottom)

    def phase2_init_column2(self):
        """
        Initialize the components in Column 2 for Phase 2 of the platform UI.

        This method sets up the user interface elements in Column 2, which includes
        options for selecting a database file, browsing tables, searching for specific
        tables, displaying table data, metadata, and a chart view.

        Returns:
            None
        """
        # Column 2 will include an edit and browse to allow a user to read database files, with a list of the tables below
        folder_table_input_layout = QVBoxLayout()
        
        # Step 1: Select Database File
        self.create_label("Step 1: Select Database File:", folder_table_input_layout)
        self.search_DataBase_file = QLineEdit()
        self.search_DataBase_file.setPlaceholderText("Link to Database File")
        folder_table_input_layout.addWidget(self.search_DataBase_file)
        
        # Browse Button
        self.select_folder_path_button = self.create_button("Browse", folder_table_input_layout, self.Phase2_select_database_file_button_clicked)
        
        # Search Table Input
        self.search_table_input = QLineEdit()
        self.search_table_input.setPlaceholderText("Search Table")
        self.search_table_input.textChanged.connect(self.phase2_search_table_names)
        folder_table_input_layout.addWidget(self.search_table_input)
        
        # List Widget
        self.list_widget = QListWidget()
        self.table_widget = QTableWidget()
        self.table_widget.setSortingEnabled(True)
        folder_table_input_layout.addWidget(self.list_widget)
        folder_table_input_layout.addWidget(self.table_widget)
        self.list_widget.itemClicked.connect(self.phase2_show_table_data)        

        # Metadata Widget
        self.metadata_widget = QWidget()  
        metadata_layout = QVBoxLayout()    
        self.metadata_widget.setLayout(metadata_layout)
        folder_table_input_layout.addWidget(self.metadata_widget)  

        # Set the layout for the column
        self.phase2_FileSection_ListViewer_Column_2.addLayout(folder_table_input_layout)

    def phase2_init_column3(self):
        """
        Initialize the components in Column 3 for Phase 2 of the platform UI.

        This method sets up the user interface elements in Column 3, which includes
        a chart view and a simulated terminal or output.

        Components:
        - Chart View Widget: QChartView for displaying charts.
        - Terminal Widget: QTextEdit for simulating terminal or output.

        Returns:
            None
        """
        # Create a splitter to divide the column
        splitter = QSplitter(Qt.Vertical)

        
         # Chart View Widget
        self.chart_widget = QChartView()
        splitter.addWidget(self.chart_widget)
        
        
        # Simulated Terminal or Output Widget wrapped in a QScrollArea
        #terminal_widget = QTextEdit()
        self.terminal_widget.setReadOnly(True)  # Set read-only property

        terminal_scroll_area = QScrollArea()
        terminal_scroll_area.setWidgetResizable(True)
        terminal_scroll_area.setWidget(self.terminal_widget)

        splitter.addWidget(terminal_scroll_area)

        # Set the size ratio for the splitter
        splitter.setSizes([3 * self.height() // 4, self.height() // 4])
        
 
        
        # Add the splitter to Column 3
        self.phase2_graph_Machine_Column_3.addWidget(splitter)
    
    def phase1_Intialize_Debugger_Column(self):
        # Add the debugger frame to Column 4
        self.debugger_text = QTextEdit()
        self.debugger_text.setReadOnly(True)  # Set read-only property
        self.debugger_Column_4.addWidget(self.debugger_text)
               
    def phase1_init_company_selection(self):
        self.create_label("Step 1: Select Companies", self.Company_Selection_Column_2)
        
        self.Search_Entry_Company_Letter_Word = QLineEdit()
        self.Search_Entry_Company_Letter_Word.setPlaceholderText("Enter company name")
        self.Company_Selection_Column_2.addWidget(self.Search_Entry_Company_Letter_Word)
        
        self.List_Box_Company_Selection = QListWidget(self)
        self.List_Box_Company_Selection.setSelectionMode(QAbstractItemView.MultiSelection)
        self.Company_Selection_Column_2.addWidget(self.List_Box_Company_Selection)
           
    def phase1_init_user_input(self):
        userInput_layout = QVBoxLayout()

        self.create_label("Step 2: Full Name:", userInput_layout)
        self.Full_Name_Entry_var = QLineEdit()
        self.Full_Name_Entry_var.setPlaceholderText("Enter Full Name")
        userInput_layout.addWidget(self.Full_Name_Entry_var)

        self.create_label("Step 4: Input Email:", userInput_layout)
        self.Email_Entry_var = QLineEdit()
        self.Email_Entry_var.setPlaceholderText("Enter Email")
        userInput_layout.addWidget(self.Email_Entry_var)

        self.create_label("Step 5: Select File Format (DB or Excel):", userInput_layout)
        self.file_Format_var = QComboBox()
        self.file_Format_var.addItems(["Data Base", "Excel"])
        userInput_layout.addWidget(self.file_Format_var)

        self.create_label("Step 6: Select Download Folder Location:", userInput_layout)
        self.select_folder_path_var = QLineEdit()
        self.select_folder_path_var.setPlaceholderText("Use Browse Button to Select Folder")
        userInput_layout.addWidget(self.select_folder_path_var)

        self.select_load_company_button= self.create_button("Load Companies", userInput_layout, self.accept_name_and_email)
        self.select_folder_path_button = self.create_button("Browse", userInput_layout, self.select_folder_path_button_clicked)
        self.submit_button = self.create_button("Submit", userInput_layout, self.submit_button_clicked)

        self.selectedCompanies_Column_3.addLayout(userInput_layout)

    def phase1_init_tab_view(self):
        tab_widget = QTabWidget()

        # Define the QTextEdit widgets
        self.selected_companies_var = QTextEdit()
        self.selected_cik_str_var = QTextEdit()
        self.selected_ticker_str_var = QTextEdit()

        tab_info = [
            ("Company", self.selected_companies_var),
            ("CIK", self.selected_cik_str_var),
            ("Ticker", self.selected_ticker_str_var)
        ]

        for tab_name, widget in tab_info:
            tab_widget.addTab(widget, tab_name)
            tab_layout = QVBoxLayout(widget)
            # Add any additional widgets to the specific tab layout if needed

        tab_layout = QVBoxLayout()
        tab_layout.addWidget(tab_widget)
        self.selectedCompanies_Column_3.addLayout(tab_layout)

    def create_label(self, text, parent_layout):
        label = QLabel(text)
        label.setFixedHeight(20)
        parent_layout.addWidget(label)
        
    def create_button(self, text, parent_layout, clicked_handler=None):
        button = QPushButton(text)
        button.setFixedHeight(30)
        
        if clicked_handler:
            #print(f"Connecting button '{text}' to handler '{clicked_handler.__name__}'")
            button.clicked.connect(clicked_handler)
        else:
            print(f"No handler provided for button '{text}'")
        
        parent_layout.addWidget(button)

    def create_combo_box(self, items, parent_layout):
        combo_box = QComboBox()
        combo_box.addItems(items)
        parent_layout.addWidget(combo_box)

    def Button_FunctiOn_Switch_To_Machine_Learning(self):
        # Function to toggle the frames visibility
        if self.frames_visible:
            # Hide the entire columns
            self.Company_Selection_Column_2.parentWidget().setVisible(False)
            self.selectedCompanies_Column_3.parentWidget().setVisible(False)
            self.debugger_Column_4.parentWidget().setVisible(False)
        
            self.phase2_FileSection_ListViewer_Column_2.parentWidget().setVisible(True)  # Initially hide the layout
            self.phase2_graph_Machine_Column_3.parentWidget().setVisible(True)  # Initially hide the layout
            #self.Phase2_Debugger_Text_Column4.parentWidget().setVisible(True)  # Initially hide the layout
            self.frames_visible = False
        else:
            # Show the entire columns
            self.Company_Selection_Column_2.parentWidget().setVisible(True)
            self.selectedCompanies_Column_3.parentWidget().setVisible(True)
            self.debugger_Column_4.parentWidget().setVisible(True)
            
            self.phase2_FileSection_ListViewer_Column_2.parentWidget().setVisible(False)  # Initially hide the layout
            self.phase2_graph_Machine_Column_3.parentWidget().setVisible(False)  # Initially hide the layout
            #self.Phase2_Debugger_Text_Column4.parentWidget().setVisible(False)  # Initially hide the layout
            self.frames_visible = True

    def sidebar_button_event(self):
        print("sidebar_button click")
        
    def select_folder_path_button_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.select_folder_path_var.setText(folder_path)
        
    def phase2_search_table_names(self, search_text):
        """
        Search for table names in the database based on the provided search text.
        
        Parameters:
        - search_text (str): The text to be used for filtering table names.

        This function fetches all table names from the database, filters them based on the
        search text, and populates the list widget with the filtered table names.
        """
        # Clear existing items from the list widget
        self.list_widget.clear()

        # Fetch all table names from the database
        try:
            database_path = self.search_DataBase_file.text()
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = cursor.fetchall()

            # Filter table names based on search_text
            filtered_table_names = [table[0] for table in table_names if search_text.lower() in table[0].lower()]

            # Add the filtered table names to the list widget
            self.list_widget.addItems(filtered_table_names)

        except sqlite3.Error as e:
            print("Error:", e)
        finally:
            connection.close()
            
    def phase2_show_table_data(self, item):
        """
        Show data for the selected table in the table widget and update metadata and chart.
        
        Parameters:
        - item (QListWidgetItem): The selected item containing the table name.

        This function fetches column names, data, and metadata from the selected table
        in the database. It then populates the table widget, updates metadata display,
        and updates the chart based on the selected table's data.
        """
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)

        selected_table = item.text()

        try:
            database_path = self.search_DataBase_file.text()
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()

            # Fetch column names and data from the selected table
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns = cursor.fetchall()
            cursor.execute(f"SELECT * FROM {selected_table}")
            data = cursor.fetchall()

            # Set headers and populate column names
            column_names = [column[1] for column in columns]
            self.table_widget.setColumnCount(len(column_names))
            self.table_widget.setHorizontalHeaderLabels(column_names)

            # Call the function to populate the table widget
            self.phase2_populate_table_widget(data, columns)
            
            # Fetch metadata from Metadata_Table
            cursor.execute("SELECT array_parameter1, label_name, description_name, unit_name FROM Metadata_Table WHERE table_name = ?", (selected_table,))
            metadata = cursor.fetchone()

            if metadata:
                array_parameter1, label_name, description_name,unit_name = metadata

                # Clear any previous contents in metadata layout
                metadata_layout = self.metadata_widget.layout()
                for i in reversed(range(metadata_layout.count())):
                    widget_item = metadata_layout.itemAt(i)
                    widget = widget_item.widget()
                    metadata_layout.removeWidget(widget)
                    widget.deleteLater()

                # Create QLabel widgets to display metadata information
                array_label = QLabel(f"Array Parameter: {array_parameter1}")
                array_label.setWordWrap(True)
                
                label_label = QLabel(f"Label Name: {label_name}")
                label_label.setWordWrap(True)
                
                description_label = QLabel(f"Description: {description_name}")
                description_label.setWordWrap(True)
                
                Unit_label = QLabel(f"unit: {unit_name}")
                Unit_label.setWordWrap(True)
                
                # Add the QLabel widgets to the metadata layout
                metadata_layout.addWidget(array_label)
                metadata_layout.addWidget(label_label)
                metadata_layout.addWidget(description_label)
                metadata_layout.addWidget(Unit_label)

                # Update the metadata widget's layout
                self.metadata_widget.setLayout(metadata_layout)
                
            # Update the chart based on the selected table's data
            self.Phase_2_Update_Chart_Widget(data, column_names,label_name,unit_name)    

        except sqlite3.Error as e:
            print("Error:", e)
        finally:
            connection.close()

    def Phase_2_Update_Chart_Widget(self, data, column_names, title, unit):
        """
        Update the chart with data from the selected table.
        
        Parameters:
        - data (list): The data to be plotted on the chart.
        - column_names (list): The names of the columns in the data.
        - title (str): The title of the chart.
        - unit (str): The unit for the Y-axis values.

        This function creates a line series chart and updates it with the provided data,
        column names, title, and unit. It also handles date formatting and axis configurations.
        """
        chart = QChart()
        series = QLineSeries()

        end_column = None
        val_column = None

        for keyword in ["end", "val"]:
            for column_name in column_names:
                if keyword in column_name.lower():
                    if keyword == "end":
                        end_column = column_name
                    elif keyword == "val":
                        val_column = column_name

        if end_column and val_column:
            end_index = column_names.index(end_column)
            val_index = column_names.index(val_column)

            min_val = float("inf")
            max_val = float("-inf")
            min_date = None
            max_date = None
            
            existing_dates = set()  # To track existing dates in the series

            for row in data:
                end_date = row[end_index]
                val = row[val_index]

                if end_date and val:
                    try:
                        # Convert end_date to a QDateTime object
                        end_date_time = QDateTime.fromString(end_date, "yyyy-MM-dd")
                        print(f"The End Date Time: {end_date_time}")
                        if isinstance(val, str):
                            val = float(val.replace("$", "").replace(",", ""))
                        elif isinstance(val, (int, float)):
                            val = float(val)
                       
                        # Check if the end_date already exists in the series
                        if end_date_time not in existing_dates:
                        
                            # Append the QDateTime object (X-axis) and val (Y-axis)
                            x_timestamp = end_date_time.toSecsSinceEpoch()
                           
                            # Create a QPointF with the tooltip
                            point = QPointF(x_timestamp, val)
                            # Append the point to the series
                            series.append(point)
                            
                            
                            existing_dates.add(end_date_time)  # Add the date to the set

                            # Track the minimum and maximum date
                            if min_date is None or end_date_time < min_date:
                                min_date = end_date_time

                            if max_date is None or end_date_time > max_date:
                                max_date = end_date_time
                            
                    except (ValueError, TypeError):
                        continue

            print(f"Data points in series for {title}:")
            for point in series.pointsVector():
                x_value = point.x()
                y_value = point.y()
                print(f"X: {x_value}, Y: {y_value}")
                
            print(f"{min_date} {type(min_date)} - {max_date}")
                        
            # Create new QDateTimeAxis for the X-axis and set its format
            x_axis = QDateTimeAxis()
            x_axis.setFormat("yyyy-MM-dd")
            x_axis.setTitleText("Date")

            # Set the X-axis range based on the minimum and maximum date values
            x_axis.setMin(min_date)
            x_axis.setMax(max_date)

            # Add axes to the chart
            chart.addAxis(x_axis, Qt.AlignBottom)

            # Attach the series to the axes
            series.attachAxis(x_axis)
            
            # Add the series to the chart
            chart.addSeries(series)

            # Create new QValueAxis for the y-axis and set its range and label format
            y_axis = QValueAxis()
            y_axis.setRange(min_val, max_val)
            y_axis.setLabelFormat("%'0.2f")
            y_axis.setTitleText(unit)

            # Set the tick interval for the Y-axis to control which values are shown
            y_axis.setTickCount(10)  # 11 intervals to show key values and breakdown
        
            # Add the y-axis to the chart
            chart.addAxis(y_axis, Qt.AlignLeft)
            series.attachAxis(y_axis)
            
            # Add the series to the chart
            chart.addSeries(series)
            
            # Apply a theme to the chart
            chart.setTheme(QChart.ChartThemeDark)
            chart.setTitle(title)  # Set an empty string as the chart title
            
            
        #self.chart_widget.setChart(chart_view)
        self.chart_widget.setChart(chart)
                
    def phase2_populate_table_widget(self, data, columns):
        """
        Populate the table widget with data.
        
        Parameters:
        - data (list): The data to be displayed in the table widget.
        - columns (list): The column names corresponding to the data.

        This function sets up the headers of the table widget using the provided column names
        and populates the table with the provided data.
        """
        # Set headers and populate column names
        column_names = [column[1] for column in columns]
        self.table_widget.setColumnCount(len(column_names))
        self.table_widget.setHorizontalHeaderLabels(column_names)

        # Populate table with data
        self.table_widget.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, cell_value in enumerate(row_data):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(cell_value)))

    def Phase2_select_database_file_button_clicked(self):
        """
        Handle the click event for selecting a database file.
        
        This function opens a file dialog to allow the user to select a compatible database file.
        If a file is selected, it updates the database file path, fetches table names,
        and populates the list widget with the table names.
        """
        self.table_widget.clear()
        self.list_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        
        compatible_file_formats = ["Database Files (*.db *.sqlite *.sqlite3)"]
        folder_path, selected_filter = QFileDialog.getOpenFileName(self, "Select Database File", filter=";;".join(compatible_file_formats))

        if folder_path:
            self.search_DataBase_file.setText(folder_path)
            try:
                connection = sqlite3.connect(folder_path)
                cursor = connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = cursor.fetchall()
                for table in table_names:
                    self.list_widget.addItem(table[0])
            except sqlite3.Error as e:
                print("Error:", e)
            finally:
                connection.close()  
        else:
            self.show_error("Please select a compatible database file.")
        
    def load_user_settings(self):
        try:
            name = self.config.get("UserSettings", "Name")
            email = self.config.get("UserSettings", "Email")
            file_path = self.config.get("UserSettings", "FilePath")
            self.Full_Name_Entry_var.setText(name)
            self.Email_Entry_var.setText(email)
            self.select_folder_path_var.setText(file_path)
        except (configparser.NoSectionError, configparser.NoOptionError):
            # Handle case when config file or section is not found
            pass

    def save_user_settings(self):
        name = self.Full_Name_Entry_var.text()
        email = self.Email_Entry_var.text()
        file_path = self.select_folder_path_var.text()
        self.config["UserSettings"] = {"Name": name, "Email": email, "FilePath": file_path}
        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

    def validate_input(self):
        selected_companies = self.selected_companies_var.toPlainText()
        folder_path = self.select_folder_path_var.text()
        download_type = self.file_Format_var.currentText()
        Full_Name_Entry = self.Full_Name_Entry_var.text()
        Email_Entry = self.Email_Entry_var.text()

        if not selected_companies:
            self.show_error("Please select at least one company")
            return False

        if not folder_path:
            self.show_error("Please select a folder path")
            return False

        if not download_type:
            self.show_error("Please select at least one download type")
            return False

        if not Full_Name_Entry:
            self.show_error("Please enter your full name")
            return False

        if not Email_Entry:
            self.show_error("Please enter your email address")
            return False

        return True

    def search_company(self, text):
        search_text = text.lower()
        if search_text:
            matching_options = [option for option in self.List_of_All_Companies_From_Json_Tickers if search_text in option.lower()]
            self.List_Box_Company_Selection.clear()
            self.List_Box_Company_Selection.addItems(matching_options)
        else:
            self.List_Box_Company_Selection.clear()
            self.List_Box_Company_Selection.addItems(self.List_of_All_Companies_From_Json_Tickers)

    def on_select_company(self):
        selected_items = self.List_Box_Company_Selection.selectedItems()
        selected_companies = [item.text() for item in selected_items]
        cik_str_list = [self.List_of_All_CIKs_From_Json_Tickers[self.List_of_All_Companies_From_Json_Tickers.index(company)] for company in selected_companies]
        ticker_str_list = [self.List_of_All_Tickers_From_Json_Tickers[self.List_of_All_Companies_From_Json_Tickers.index(company)] for company in selected_companies]

        cik_str_list = [str(cik) for cik in cik_str_list]  # Convert integers to strings
        selected_ticker_str = "\n".join(ticker_str_list)

        selected_cik_str = "\n".join(cik_str_list)
        # selected_ticker_str = "\n".join(ticker_str_list)

        self.selected_companies_var.setPlainText("\n".join(selected_companies))
        self.selected_cik_str_var.setPlainText(selected_cik_str)
        self.selected_ticker_str_var.setPlainText(selected_ticker_str)

    def load_json_data(self):
        full_name = self.Full_Name_Entry_var.text()
        Email_Entry = self.Email_Entry_var.text()
        user_agent = f'{full_name} {Email_Entry}'

        filings2 = Filling_Links_Intial(user_agent)
        data = filings2.load_CIK_Values()
            
        try:
            # Check if data is empty
            if not data:
                # Prompt the user to input name and email
                self.accept_name_and_email()
                return

            self.List_of_All_Companies_From_Json_Tickers = [data[key]["title"] for key in data.keys()]
            self.List_of_All_CIKs_From_Json_Tickers = [data[key]["cik_str"] for key in data.keys()]
            self.List_of_All_Tickers_From_Json_Tickers = [data[key]["ticker"] for key in data.keys()]
            self.List_Box_Company_Selection.addItems(self.List_of_All_Companies_From_Json_Tickers)
        except json.JSONDecodeError:
            self.debugger_text.append("Failed to decode JSON data.")
                             
    def accept_name_and_email(self):
        full_name = self.Full_Name_Entry_var.text()
        Email_Entry = self.Email_Entry_var.text()
        missing_info = []

        # Check if name is missing
        if not full_name:
            missing_info.append("Name")

        # Check if email is missing
        if not Email_Entry:
            missing_info.append("Email")

        # If either or both are missing, inform the user
        if missing_info:
            message = f"The following information is missing: {', '.join(missing_info)}"
            # Modify this part based on how you display messages in your existing dialog
            self.show_error(f"{message}")
        else:
            # Run the function again with the updated values
            self.load_json_data()
            
    def show_error(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Warning)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec()

    def submit_button_clicked(self):
        if not self.validate_input():
            return

        folder_path = self.select_folder_path_var.text()
        download_type = self.file_Format_var.currentText()
        company_CIKS = self.selected_cik_str_var.toPlainText()
        company_Name = self.selected_companies_var.toPlainText()
        full_name = self.Full_Name_Entry_var.text()
        Email_Entry = self.Email_Entry_var.text()
        user_agent = f'{full_name} {Email_Entry}'

        self.save_user_settings()

        # Redirect stdout and stderr to the debugger_text widget
        sys.stdout = StdoutRedirector(self.debugger_text, self.progress_bar)
        sys.stderr = StderrRedirector(self.debugger_text, self.progress_bar)

        string_Level_User = f'{folder_path}, {company_Name}'

        # Indicate the start of the process
        self.debugger_text.append(f"Performing API extract and download for {string_Level_User}...")

        # Show the progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # Initialize progress to 0%
        
        cik_list = company_CIKS.split("\n")
        zfilled_cik_list = [cik.strip().zfill(10) for cik in cik_list]

        if download_type == "Excel":
            filings1 = Filling_Links(zfilled_cik_list, folder_path, user_agent)
            filings1.get_companyfacts_json_excel()
        elif download_type == "Data Base":
            filings2 = Filling_Links(zfilled_cik_list, folder_path, user_agent)
            filings2.get_companyfacts_json_db()

        # Indicate the completion of the process
        self.debugger_text.append("API extraction and download complete.")

        # Clear the form fields and list box selection
        self.selected_companies_var.setPlainText("")
        self.selected_cik_str_var.setPlainText("")
        self.selected_ticker_str_var.setPlainText("")
        self.List_Box_Company_Selection.clearSelection()  # Clear list box selection

        # Hide the progress bar
        self.progress_bar.setVisible(False)
        
        # Show a message box indicating extraction completion
        QMessageBox.information(self, "Extraction Complete", "API extraction and download complete.")

class StdoutRedirector:
    def __init__(self, text_widget,progress_bar):
        self.text_widget = text_widget
        self.progress_bar = progress_bar
        
    def write(self, message):
        self.text_widget.append(message)  # Use appendPlainText to avoid extra white spaces
        self.text_widget.ensureCursorVisible()  # Ensure cursor is visible

        # Update the progress bar (example: increment by 10% for each write)
        self.progress_bar.setValue(self.progress_bar.value() + 10)
        
    def flush(self):
        pass

class StderrRedirector:
    def __init__(self, text_widget, progress_bar):
        self.text_widget = text_widget
        self.progress_bar = progress_bar
        
    def write(self, message):
        # Apply a custom style for error messages
        self.text_widget.append(f'<span style="color:red;">{message}</span>')
        self.text_widget.ensureCursorVisible()  # Ensure cursor is visible
        
        # Update the progress bar (example: increment by 10% for each write)
        self.progress_bar.setValue(self.progress_bar.value() + 10)
        print(f"Error: {message}")
        
    def flush(self):
        pass
    


