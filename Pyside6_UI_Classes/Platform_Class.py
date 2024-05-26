from collections import defaultdict
import datetime
import logging
import time
import sys
import json
import configparser
import sqlite3

from SEC_API_Filling_Class.Filling_Links import Filling_Links, Filling_Links_Intial
from PySide6.QtGui import  QFont, QFontMetrics, QPainterPath, QColor ,QGradient, QPen, QLinearGradient, QPainter
from PySide6.QtCore import Qt, QPointF, QRectF, QRect ,QDateTime
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsSimpleTextItem, QSplitter, QScrollArea,
    QWidget, QListWidget, QTableWidgetItem, QTableWidget, QSpacerItem,
    QProgressBar, QSizePolicy, QAbstractItemView, QSizePolicy, QComboBox,
    QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, QLineEdit, QFileDialog,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QScatterSeries,
    QSplineSeries,QAreaSeries
)

# Create a class for the main platform UI
class Platform(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Read configuration from file
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # Define these attributes before using them
        self.selected_companies_var = QTextEdit()
        self.selected_cik_str_var = QTextEdit()
        self.selected_ticker_str_var = QTextEdit()
        
        # Create the terminal widget
        self.terminal_widget = QTextEdit()
        self.terminal_widget.setReadOnly(True)  # Set read-only property
        
        # Initialize layouts and UI elements
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
        
         # Connect signals to functions
        self.List_Box_Company_Selection.currentItemChanged.connect(self.on_select_company)
        self.List_Box_Company_Selection.itemSelectionChanged.connect(self.on_select_company)
        self.Search_Entry_Company_Letter_Word.textChanged.connect(self.search_company)
       
        # Load user settings and JSON data
        self.load_user_settings()   
        self.load_json_data()
                
        # Create instances of  redirectors
        self.stdout_redirector = StdoutRedirector(text_widget=self.terminal_widget, progress_bar=self.progress_bar)
        self.stderr_redirector = StderrRedirector(text_widget=self.terminal_widget, progress_bar=self.progress_bar)

        # Redirect sys.stdout and sys.stderr to your redirectors
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        
        self.view_instance = None
        
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
        - "DB Viewer": Toggles the visibility of specific UI components related to Machine Learning.
        Returns:
            None
        """
        
        buttons = [
            ("DB Viewer", self.Button_FunctiOn_Switch_To_Machine_Learning),
            ("Not Used", self.sidebar_button_event),  # Add handler if needed
            ("Not Used", self.sidebar_button_event)   # Add handler if needed
        ]
        for button_text, button_handler in buttons:
            self.create_button(button_text, self.sideBar_Column_1, button_handler)
            
        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sideBar_Column_1.addItem(spacer_bottom)

    def phase2_init_column2(self):
        """
        Initialize the components in Column 2 for Not Used of the platform UI.

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
        Initialize the components in Column 3 for Not Used of the platform UI.

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

        # self.chart_widget = QChartView()
        
        # Chart View Widget
        self.chart_widget = QChartView()
        self.chart_widget.setMouseTracking(True)
        
        splitter.addWidget(self.chart_widget)

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
            
            # Call the function to alter the table by deleting rows
            self.alter_table_by_deleting_rows(selected_table, data, column_names,database_path)
            
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns = cursor.fetchall()
            cursor.execute(f"SELECT * FROM {selected_table}")
            data = cursor.fetchall()

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

    def alter_table_by_deleting_rows(self, selected_table, data, column_names, database_path):
        print(f"The path is {database_path}")
        print(f"The selected table: {selected_table}")
        rows_to_keep = []
        val_column, frame_column, start_column, end_column, filed_column, index_column, fp_column = None, None, None, None, None, None, None

        try:
            for column_name in column_names:
                if "val" in column_name.lower():
                    val_column = column_name
                elif "frame" in column_name.lower():
                    frame_column = column_name
                elif "start" in column_name.lower():
                    start_column = column_name
                elif "end" in column_name.lower():
                    end_column = column_name
                elif "filed" in column_name.lower():
                    filed_column = column_name                    
                elif "index" in column_name.lower():
                    index_column = column_name    
                elif "fp" in column_name.lower():
                    fp_column = column_name
            
            #balance sheet clean up        
            if val_column and frame_column and start_column is None and end_column and filed_column and index_column:
                end_index = column_names.index(end_column)
                filed_index = column_names.index(filed_column)
                index_column_index = column_names.index(index_column)

                # Create a dictionary to store the latest filed_date for each unique end_value
                End_Date_Dictionary = defaultdict(lambda: {"index": None, "end_date": None, "filed_date": None})


                # Check if any row has a value in the 'val' column
                for i in range(0, len(data)):
                    # Check if End Date is None, file date is none and the value doesn't exist in the dictionary
                    if data[i][end_index] is not None and data[i][index_column_index] is not None and data[i][filed_index] is not None and data[i][end_index] not in End_Date_Dictionary:
                        # Add values to the dictionary for the current end_value
                        End_Date_Dictionary[data[i][end_index]]["index"] = data[i][index_column_index]
                        End_Date_Dictionary[data[i][end_index]]["end_date"] = data[i][end_index] # You can set it to a default value if needed
                        End_Date_Dictionary[data[i][end_index]]["filed_date"] = data[i][filed_index]  # You can set it to a default value if needed

                    elif data[i][end_index] in End_Date_Dictionary:
                        format = "%Y-%m-%d"
                        End_Date_1 = End_Date_Dictionary[data[i][end_index]]["filed_date"] 
                        End_Date_1_converted_from_string = datetime.datetime(*(time.strptime(End_Date_1, format)[0:6]))
                        End_Date_2 = data[i][filed_index] 
                        End_Date_2_converted_from_string = datetime.datetime(*(time.strptime(End_Date_2, format)[0:6]))                        
                        
                        if End_Date_1_converted_from_string < End_Date_2_converted_from_string:
                            End_Date_Dictionary[data[i][end_index]]["filed_date"] = data[i][filed_index] 
                            End_Date_Dictionary[data[i][end_index]]["index"] = data[i][index_column_index]

                # Index rows to keep based on the stored indices in End_Date_Dictionary
                for end_value, info in End_Date_Dictionary.items():
                    if info["index"] is not None:
                        rows_to_keep.append(info["index"])

                indices_to_delete = []

                for j, row in enumerate(data):
                    index_column_value = row[index_column_index]
                    
                    if index_column_value not in rows_to_keep:
                        # Print information before deleting
                        print(f"Deleting Row {j}")
                        print(f"Values: {row}")
                        indices_to_delete.append(j)

                # Delete rows from the table
                if indices_to_delete:
                    connection = sqlite3.connect(database_path)
                    cursor = connection.cursor()

                    for n in reversed(indices_to_delete):
                        column_name_to_delete = index_column  
                        column_name_to_delete = f'"{index_column}"'
                        value_to_delete = data[n][index_column_index]
                        cursor.execute(f"DELETE FROM {selected_table} WHERE {column_name_to_delete}=?", (value_to_delete,))
                            
                    connection.commit()
                    connection.close()
                    
            ############## Case 2 ###################
            #Cash flow and Income Earning formula, in which there is a start and end date condition
            elif (val_column is not None and
                    frame_column is not None and
                    start_column is not None and
                    fp_column is not None and
                    end_column is not None and
                    filed_column is not None and
                    index_column is not None):
                
                end_index = column_names.index(end_column)
                filed_index = column_names.index(filed_column)
                index_column_index = column_names.index(index_column)
                fp_index = column_names.index(fp_column)
                start_index = column_names.index(start_column)

                # Create a set
                unique_entries = set()
               
                # Check if any row has a value in the 'val' column
                for i in range(0, len(data)):
                    # Check if End Date is None, file date is none and the value doesn't exist in the dictionary
                    end_date_i = data[i][end_index]
                    start_date_i =data[i][start_index]
                    filed_date_i = data[i][filed_index] 
                    fp_value_i =data[i][fp_index]
                    index_value_i =  data[i][index_column_index]
                    
                    current_entry = (index_value_i, start_date_i, end_date_i, fp_value_i, filed_date_i)

                    if (end_date_i is not None
                        and start_date_i is not None
                        and filed_date_i is not None
                        and fp_value_i is not None
                        and index_value_i is not None):
                        
                        # Check if the combination exists in unique_entries
                        matching_entries = [entry for entry in unique_entries if entry[1:4] == (start_date_i, end_date_i, fp_value_i)]
                        if not matching_entries:
                            # If no matching entry, add the current entry to unique_entries
                            unique_entries.add(current_entry)
                        else:
                            # If matching entries exist, compare and update based on filed_date_i
                            for matching_entry in matching_entries:
                                format = "%Y-%m-%d"
                                
                                End_Date_1 = matching_entry[4]
                                End_Date_1_converted_from_string = datetime.datetime(*(time.strptime(End_Date_1, format)[0:6]))
                                End_Date_2 = data[i][filed_index]
                                End_Date_2_converted_from_string = datetime.datetime(*(time.strptime(End_Date_2, format)[0:6]))

                                if End_Date_1_converted_from_string < End_Date_2_converted_from_string:
                                    # Your logic here, for example:
                                    # Update the set with the new combination
                                    unique_entries.remove(matching_entry)
                                    unique_entries.add(current_entry)
                    
                # Index rows to keep based on the stored indices in End_Date_Dictionary
                rows_to_keep_case_2 = [entry[0] for entry in unique_entries if entry[0] is not None]
                
                indices_to_delete = []

                for j, row in enumerate(data):
                    index_column_value = row[index_column_index]

                    if index_column_value not in rows_to_keep_case_2:
                        # Print information before deleting
                        print(f"Deleting Row {j}")
                        print(f"Values: {row}")
                        indices_to_delete.append(j)

                # Delete rows from the table
                if indices_to_delete:
                    connection = sqlite3.connect(database_path)
                    cursor = connection.cursor()

                    for n in reversed(indices_to_delete):
                        column_name_to_delete = index_column  
                        column_name_to_delete = f'"{index_column}"'
                        value_to_delete = data[n][index_column_index]
                        cursor.execute(f"DELETE FROM {selected_table} WHERE {column_name_to_delete}=?", (value_to_delete,))

                    connection.commit()
                    connection.close()

        except Exception as e:
            print(f"An error occurred: {e}")
                
  
  ######## Graph Fuction######       
        
    def print_data_points(self, series, title):
        print(f"Data points in series for {title}:")
        for point in series.pointsVector():
            x_value, y_value = point.x(), point.y()
            print(f"X: {x_value}, Y: {y_value}") 

    def configure_y_axis(self, min_val, max_val, unit):
        try:
            # Check if min_val and max_val are equal
            if min_val == max_val:
                # Handle the case where both min_val and max_val are zero
                range_value = 1 if min_val == 0 else max(0.1 * abs(min_val), 1)
                min_val -= range_value
                max_val += range_value

            y_axis = QValueAxis()
            y_axis.setRange(min_val, max_val)
            y_axis.setLabelFormat("%'0.2f")
            y_axis.setTitleText(unit)
            y_axis.setTickCount(15)
 
            return y_axis      
         
        except Exception as e:
            logging.error(f"Error in configure_y_axis: {e}")
    
    def configure_x_axis(self, min_date, max_date):
        
        try:
            # Check if the X-axis minimum and maximum timestamps are equal
            if min_date == max_date:
                # Add an additional value to the max_timestamp to create a range
                min_date -= 86400  # Subtract 24 hours (86400 seconds)
                max_date += 86400  # Add 24 hours (86400 seconds)
                                    
            min_date, max_date = QDateTime.fromSecsSinceEpoch(min_date), QDateTime.fromSecsSinceEpoch(max_date)
            x_axis = QDateTimeAxis()
            x_axis.setFormat("yyyy-MM-dd")
            x_axis.setTitleText("Date")
            x_axis.setRange(min_date , max_date)
            
            # Calculate the difference in days
            days_difference = min_date.daysTo(max_date)

            # Adjust the tick count based on the difference
            if days_difference <= 10:
                x_axis.setTickCount(days_difference - 1)
            else:
                x_axis.setTickCount(10)
                
            return x_axis  # Return x_axis instead of series   
        
        except Exception as e:
            logging.error(f"Error in configure_x_axis: {e}")


    def calculate_min_max_values(self, data, end_index, val_index, start_index=None):
            try:
                min_val, max_val = float("inf"), float("-inf")
                min_date, max_date = None, None
                stored_points_start, stored_points_end = [], []
                
                for row in data:
                    end_date, val = row[end_index], row[val_index]
                    start_date = row[start_index] if start_index is not None else None
                    
                    if end_date and val is not None:
                        try:
                            val = float(val.replace("$", "").replace(",", "")) if isinstance(val, str) else float(val)

                            if start_index is not None:
                                start_date = QDateTime.fromString(start_date, "yyyy-MM-dd")
                                start_x = start_date.toSecsSinceEpoch()
                                point_start = QPointF(start_x, val)
                                stored_points_start.append(point_start)

                                # Track the minimum and maximum start date
                                min_date = min(min_date, start_x) if min_date else start_x
                                max_date = max(max_date, start_x) if max_date else start_x

                            end_date_time = QDateTime.fromString(end_date, "yyyy-MM-dd")
                            end_x = end_date_time.toSecsSinceEpoch()
                            point_end = QPointF(end_x, val)
                            stored_points_end.append(point_end)

                            # Track the minimum and maximum end date
                            min_date = min(min_date, end_x) if min_date else end_x
                            max_date = max(max_date, end_x) if max_date else end_x

                            min_val, max_val = min(min_val, val), max(max_val, val)
    
                        except (ValueError, TypeError) as e:
                            logging.error(f"Error processing row: {e}")
                            continue

            except (ValueError, TypeError) as e:
                logging.error(f"Error in calculate_min_max_values: {e}")

            return min_date, max_date, min_val, max_val, stored_points_start, stored_points_end
    
            
    def Phase_2_Update_Chart_Widget(self, data, column_names, title, unit):
        try:
            chart = QChart()
        
            end_column = next((col for col in column_names if "end" in col.lower()), None)
            start_column = next((col for col in column_names if "start" in col.lower()), None)
            val_column = next((col for col in column_names if "val" in col.lower()), None)
            
            if end_column and val_column and start_column is None:
                series = QScatterSeries() if len(data) == 1 else  QLineSeries() 
   
                end_index = column_names.index(end_column)
                val_index = column_names.index(val_column)
                min_date, max_date, min_val, max_val, stored_points_start, stored_points_end = self.calculate_min_max_values(data, end_index, val_index)
                
                if stored_points_end:
                        series.append(stored_points_end)   
                        chart.addSeries(series)   
                        x_axis = self.configure_x_axis(min_date, max_date)
                        y_axis = self.configure_y_axis( min_val, max_val, unit)  
                        self.print_data_points(series, title)
                        
              
            elif end_column and val_column and start_column:
                
                end_index, val_index, start_index = column_names.index(end_column), column_names.index(val_column), column_names.index(start_column)
                min_date, max_date, min_val, max_val, stored_points_start, stored_points_end = self.calculate_min_max_values(data, end_index, val_index, start_index)
                
                if stored_points_start and stored_points_end:                        
                        for start_point, end_point in zip(stored_points_start, stored_points_end):
                            # Plot the upper line
                            upper_series = QLineSeries()
                            upper_series.append(start_point)
                            upper_series.append(end_point)
                            chart.addSeries(upper_series)
                            
                            # Plot the lower line
                            lower_series = QLineSeries()
                            lower_series.append(QPointF(start_point.x(), min_val))
                            lower_series.append(QPointF(end_point.x(), min_val))
                            chart.addSeries(lower_series)
   
                            area_series = QAreaSeries(upper_series, lower_series)
                            chart.addSeries(area_series)
                            
                        x_axis = self.configure_x_axis(min_date, max_date)
                        y_axis = self.configure_y_axis(min_val, max_val, unit)
                                     
            chart.createDefaultAxes()
            chart.setAcceptHoverEvents(True)
            
            self.configure_chart_axes(chart, x_axis, y_axis)
            self.set_chart_properties(chart, title)
            
            self.chart_widget.setChart(chart)
            self.chart_widget.setMouseTracking(True)
     
            if end_column and val_column and start_column:
                self.view_instance = View(chart, area_series)
            else:
                self.view_instance = View(chart, series) 

        except Exception as e:
            logging.error(f"Error in Phase_2_Update_Chart_Widget: {e}")        

    def configure_chart_axes(self, chart, x_axis, y_axis):
        default_x_axis = chart.axisX()
        default_y_axis = chart.axisY()
        chart.removeAxis(default_x_axis)
        chart.removeAxis(default_y_axis)
        chart.addAxis(x_axis, Qt.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignLeft)
        
    def set_chart_properties(self, chart, title):
        chart.setTheme(QChart.ChartThemeDark)
        chart.setTitle(title)
        chart.setDropShadowEnabled(True)
        chart.legend().setVisible(False)
        for series in chart.series():
            # Set properties for data points in the series
            series.setPointsVisible(True)

            if isinstance(series, QScatterSeries):
                 series.setMarkerShape(QScatterSeries.MarkerShapeTriangle)  

            # Set the properties for the line connecting the data points (if applicable)
            if isinstance(series, QLineSeries) or isinstance(series, QSplineSeries):
                pen = series.pen()
                pen.setWidth(2)  # Set the width of the line
                series.setPen(pen)
                
            # Set the properties for the line connecting the data points (if applicable)
            if isinstance(series, QAreaSeries):                
                series.setColor("green")
                pen = QPen(0x059605)
                pen.setWidth(2)
                series.setPen(pen)
                
        
     ######## Graph Fuction End######                     
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
                
                # Filter tables with relevant column headers
                relevant_tables = []
                for table_name in table_names:
                    cursor.execute(f"PRAGMA table_info({table_name[0]})")
                    columns = [column[1] for column in cursor.fetchall()]
                    if any(keyword.lower() in columns for keyword in ["val", "start", "end"]):
                        relevant_tables.append(table_name[0])

                # Populate list widget with relevant table names
                for table in relevant_tables:
                    self.list_widget.addItem(table)
        
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
    


class Callout(QGraphicsItem):
    """
    A QGraphicsItem representing a callout with rounded rectangle and text.

    Parameters:
        - chart (QChart): The chart to which the callout is associated.

    Methods:
        - __init__(self, chart): Initializes the Callout instance.
        - boundingRect(self): Returns the bounding rectangle of the callout.
        - paint(self, painter, option, widget): Paints the callout on the chart.
        - mousePressEvent(self, event): Handles mouse press events on the callout.
        - mouseMoveEvent(self, event): Handles mouse move events on the callout.
        - set_text(self, text): Sets the text content of the callout.
        - set_anchor(self, point): Sets the anchor point of the callout.
        - update_geometry(self): Updates the geometry of the callout.

    Attributes:
        - _chart (QChart): The associated chart.
        - _text (str): The text content of the callout.
        - _textRect (QRectF): The rectangle bounding the text.
        - _anchor (QPointF): The anchor point of the callout.
        - _font (QFont): The font used for text.
        - _rect (QRectF): The overall rectangle of the callout.
    """
    def __init__(self, chart):
        QGraphicsItem.__init__(self, chart)
        self._chart = chart
        self._text = ""
        self._textRect = QRectF()
        self._anchor = QPointF()
        self._font = QFont()
        self._rect = QRectF()

    def boundingRect(self):
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        rect = QRectF()
        rect.setLeft(min(self._rect.left(), anchor.x()))
        rect.setRight(max(self._rect.right(), anchor.x()))
        rect.setTop(min(self._rect.top(), anchor.y()))
        rect.setBottom(max(self._rect.bottom(), anchor.y()))
        return rect

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.addRoundedRect(self._rect, 5, 5)
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        if not self._rect.contains(anchor) and not self._anchor.isNull():
            point1 = QPointF()
            point2 = QPointF()

            above = anchor.y() <= self._rect.top()
            above_center = (anchor.y() > self._rect.top() and anchor.y() <= self._rect.center().y())
            below_center = (anchor.y() > self._rect.center().y() and anchor.y() <= self._rect.bottom())
            below = anchor.y() > self._rect.bottom()

            on_left = anchor.x() <= self._rect.left()
            left_of_center = (anchor.x() > self._rect.left() and anchor.x() <= self._rect.center().x())
            right_of_center = (anchor.x() > self._rect.center().x() and anchor.x() <= self._rect.right())
            on_right = anchor.x() > self._rect.right()

            x = (on_right + right_of_center) * self._rect.width()
            y = (below + below_center) * self._rect.height()
            corner_case = ((above and on_left) or (above and on_right) or (below and on_left) or (below and on_right))
            vertical = abs(anchor.x() - x) > abs(anchor.y() - y)

            x1 = (x + left_of_center * 10 - right_of_center * 20 + corner_case * int(not vertical) * (on_left * 10 - on_right * 20))
            y1 = (y + above_center * 10 - below_center * 20 + corner_case * vertical * (above * 10 - below * 20))
            point1.setX(x1)
            point1.setY(y1)

            x2 = (x + left_of_center * 20 - right_of_center * 10 + corner_case * int(not vertical) * (on_left * 20 - on_right * 10))
            y2 = (y + above_center * 20 - below_center * 10 + corner_case * vertical * (above * 20 - below * 10))
            point2.setX(x2)
            point2.setY(y2)

            path.moveTo(point1)
            path.lineTo(anchor)
            path.lineTo(point2)
            path = path.simplified()

        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)
        painter.drawText(self._textRect, self._text)

    def mousePressEvent(self, event):
        event.setAccepted(True)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.setPos(self._chart.mapToParent(event.pos() - event.buttonDownPos(Qt.LeftButton)))
            event.setAccepted(True)
        else:
            event.setAccepted(False)

    def set_text(self, text):
        self._text = text
        metrics = QFontMetrics(self._font)
        self._textRect = QRectF(metrics.boundingRect(QRect(0.0, 0.0, 150.0, 150.0), Qt.AlignLeft, self._text))
        self._textRect.translate(5, 5)
        self.prepareGeometryChange()
        self._rect = self._textRect.adjusted(-5, -5, 5, 5)

    def set_anchor(self, point):
        self._anchor = QPointF(point)

    def update_geometry(self):
        self.prepareGeometryChange()
        self.setPos(self._chart.mapToPosition(self._anchor) + QPointF(10, -50))


class View:
    """
    A class representing the view for displaying and interacting with a chart.

    Parameters:
        - chart (QChart): The chart to be displayed.
        - Series_1 (QAbstractSeries): The first series to be displayed on the chart.
        - Series_2 (QAbstractSeries, optional): The second series to be displayed on the chart.

    Methods:
        - __init__(self, chart, Series_1, Series_2=None): Initializes the View instance.
        - mouseMoveEvent(self, event): Handles the mouse move event to update displayed coordinates.
        - keep_callout(self): Keeps the current callout in the list of callouts.
        - tooltip(self, point, state): Displays a tooltip with X and Y coordinates when a data point is hovered.
    """
    def __init__(self, chart, Series_1, Series_2=None):
        self._chart = chart
        self._chart.setAcceptHoverEvents(True)

        self._coordX = QGraphicsSimpleTextItem(self._chart)
        self._coordX.setPos(self._chart.size().width() / 2 - 50, self._chart.size().height())
        self._coordX.setText("X: ")
        self._coordY = QGraphicsSimpleTextItem(self._chart)
        self._coordY.setPos(self._chart.size().width() / 2 + 50, self._chart.size().height())
        self._coordY.setText("Y: ")

        self._callouts = []
        self._tooltip = Callout(self._chart)

        Series_1.clicked.connect(self.keep_callout)
        Series_1.hovered.connect(self.tooltip)

        if Series_2 is not None:
            Series_2.clicked.connect(self.keep_callout)
            Series_2.hovered.connect(self.tooltip)

    def mouseMoveEvent(self, event):
        """
        Handles the mouse move event to update displayed coordinates.

        Parameters:
            - event (QGraphicsSceneMouseEvent): The mouse move event.
        """
        pos = self._chart.mapToValue(event.position().toPoint())
        x = pos.x()
        y = pos.y()
        self._coordX.setText(f"X: {x:.2f}")
        self._coordY.setText(f"Y: {y:.2f}")

    def keep_callout(self):
        """
        Keeps the current callout in the list of callouts.
        """
        self._callouts.append(self._tooltip)
        self._tooltip = Callout(self._chart)


    def tooltip(self, point, state):
        """
        Displays a tooltip with X and Y coordinates when a data point is hovered.

        Parameters:
            - point (QPointF): The data point hovered.
            - state (bool): The hover state (True if hovered, False otherwise).
        """
        if self._tooltip == 0:
            self._tooltip = Callout(self._chart)

        if state:
            x = point.x()
            y = point.y()
            
            # Convert timestamp (x) to QDateTime format
            x_datetime = QDateTime.fromSecsSinceEpoch(int(x))
            x_formatted = x_datetime.toString("dd/MM/yyyy")

            # Format Y as currency
            y_formatted = f"${y:,.2f}"

            self._tooltip.set_text(f"X: {x_formatted}\nY: {y_formatted}")
            
            self._tooltip.set_anchor(point)
            self._tooltip.setZValue(11)
            self._tooltip.update_geometry()
            self._tooltip.show()
        else:
            self._tooltip.hide()
    
    
 