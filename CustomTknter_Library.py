import tkinter
import tkinter.messagebox
import customtkinter
import sys
import tkinter as tk
from CTkListbox import *
from tkinter import messagebox, filedialog
import requests
import json
import threading
from Filling_Links import Filling_Links
import configparser

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # configure window
        self.title("SEC-Company-Facts-Extractor")
        self.geometry(f"{1100}x{580}")
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        

        # configure grid layout
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure((2, 0,1), weight=0)
        self.grid_rowconfigure((0, 1, 2,3), weight=1)

        ############### Frames Start ###############
        # Frame to house sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        # Frame to house Company Label and Search Features Label
        self.Company_Frame = customtkinter.CTkFrame(self, width=320, corner_radius=0)
        self.Company_Frame.grid(row=0, column=1, rowspan=8, sticky="nsew")
        self.Company_Frame.grid_rowconfigure(2, weight=1)
        #Frame to house TabView showing companies selected
        self.tabview = customtkinter.CTkFrame(self,width=320, corner_radius=0)
        self.tabview.grid(row=0, column=2, rowspan = 8 ,sticky="nsew")   
        self.tabview.grid_rowconfigure(6, weight=1)
        #Frame to house TabView showing companies selected
        self.scrollable_frame_Scrollable = customtkinter.CTkScrollableFrame(self.tabview, width= 320, corner_radius=0)
        self.scrollable_frame_Scrollable.grid(row=6, column=0, columnspan = 2,  rowspan = 3, sticky="nsew") 
        #self debugger frame
        self.debugger_text = customtkinter.CTkTextbox(master = self, width=320, activate_scrollbars= True)
        self.debugger_text.grid(row=0, column=3,rowspan=8,  sticky="nsew")
        ############### Frames End ###############
        
        
        
        ############### Side Frame Buttons, Entry and Labels Start ###############
        #Title Label for Side Bar
        self.title_label = customtkinter.CTkLabel(self.sidebar_frame, text="Phase Menu", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        #Side Buttons part of the Side Frame
        self.sidebar_button_Phase1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text= "Phase 1")
        self.sidebar_button_Phase1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_Phase2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event,text= "Phase 2")
        self.sidebar_button_Phase2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_Phase3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event,text= "Phase 3")
        self.sidebar_button_Phase3.grid(row=3, column=0, padx=20, pady=10)
        #Apperance and Scale label with buttons
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        ############### Side Frame Buttons, Entry and Labels Finish ###############
   
        ############### Column 1 Company List box, lavel and search Entry Start ###############
        #Select Company label
        self.company_Label_Group = customtkinter.CTkLabel(self.Company_Frame, text="1. Select Company", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.company_Label_Group.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="nsew")
        #Search Entry 
        self.Search_Entry_Company_Letter_Word = customtkinter.CTkEntry(self.Company_Frame, placeholder_text= "Search Company")
        self.Search_Entry_Company_Letter_Word.grid(row=1, column=0,columnspan=1, pady=10, padx=20, sticky="nsew")
        #Company Selection Frame
        self.List_Box_Company_Selection = tkinter.Listbox(self.Company_Frame, selectmode="extended", exportselection=False, width = 60)
        self.List_Box_Company_Selection.grid(row=2,column=0,columnspan=1, rowspan=999, pady=10, padx=20, sticky="nsew")
        self.load_json_data()
        ############### Column 1 Company List box, lavel and search Entry Finish ###############
        
        
        # Column Lavel User Input 
        self.Company_label = customtkinter.CTkLabel(self.tabview, text="2. User Input", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.Company_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="")
        # Full Name label
        self.Full_Name_label = customtkinter.CTkLabel(self.tabview, text="Full Name:", anchor = "w", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.Full_Name_label.grid(row=1, column=0,columnspan=1, padx=20, pady=(20, 10))  
        # Full Name Variable Entry 
        self.Full_Name_Entry_var = customtkinter.CTkEntry(self.tabview, placeholder_text= "Full Name")
        self.Full_Name_Entry_var.grid(row=1, column=1, columnspan=1,padx=20, pady=(20, 10)) 
        # Email Entry label
        self.Email_Entry_label = customtkinter.CTkLabel(self.tabview, text="Email:", anchor = "w",font=customtkinter.CTkFont(size=14, weight="bold"))
        self.Email_Entry_label.grid(row=2, column=0,columnspan=1, padx=20, pady=(20, 10))  
        # Email Entry Variable 
        self.Email_Entry_var = customtkinter.CTkEntry(self.tabview, placeholder_text= "Email Address")
        self.Email_Entry_var.grid(row=2, column=1,columnspan=1, padx=20, pady=(10, 10))
        # File Format Label
        self.file_Format_label = customtkinter.CTkLabel(self.tabview, text="File Format:", anchor = "w",font=customtkinter.CTkFont(size=14, weight="bold"))
        self.file_Format_label.grid(row=3, column=0, columnspan=1,padx=20, pady=(20, 10))       
        # File Format combo box
        self.file_Format_var= customtkinter.CTkComboBox(self.tabview,values=["Data Base", "Excel"])
        self.file_Format_var.grid(row=3, column=1,columnspan=1, padx=20, pady=(10, 10))
        # Folder Path Value Value
        self.select_folder_path_var = tk.StringVar()
        self.select_folder_path_entry = customtkinter.CTkEntry(self.tabview, placeholder_text="Download Location",textvariable=self.select_folder_path_var)
        self.select_folder_path_entry.grid(row=4, column=1, columnspan=1, padx=20, pady=(10, 10))
        # Button for Selecting a folder path
        self.select_folder_path_button = customtkinter.CTkButton(self.tabview, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),text= "Browse", command=self.select_folder_path_button_clicked)
        self.select_folder_path_button.grid(row=4, column=0, columnspan=1,padx=(20, 20), pady=(20, 20), sticky="nsew")
        # submit button
        self.submit_button = customtkinter.CTkButton(self.tabview, border_width=2, text_color=("gray10", "#DCE4EE"),text= "Submit",command=self.submit_button_clicked)
        self.submit_button.grid(row=5, column=0, columnspan = 2, pady=(20, 20), padx=40, sticky="n")            
        #Tab View within
        self.tabview_Tab = customtkinter.CTkTabview(self.scrollable_frame_Scrollable)
        self.tabview_Tab.grid(row=0, column=0, columnspan =2, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.tabview_Tab.add("Company")
        self.tabview_Tab.add("CIK")
        self.tabview_Tab.add("Ticker")
        self.selected_companies_var = tk.StringVar()
        self.selected_companies_label = customtkinter.CTkLabel(self.tabview_Tab.tab("Company"), textvariable=self.selected_companies_var,  wraplength=200, justify="left")
        self.selected_companies_label.grid(row=0, column=0,  columnspan = 2,padx=20)
        self.selected_ticker_str_var = tk.StringVar()
        self.selected_ticker_str_label = customtkinter.CTkLabel(self.tabview_Tab.tab("Ticker"), textvariable=self.selected_ticker_str_var,  wraplength=200, justify="left")
        self.selected_ticker_str_label.grid(row=0, column=0,  columnspan = 2,padx=20)
        self.selected_cik_str_var = tk.StringVar()
        self.selected_cik_str_label = customtkinter.CTkLabel(self.tabview_Tab.tab("CIK"), textvariable=self.selected_cik_str_var, wraplength=200, justify="left")
        self.selected_cik_str_label.grid(row=0, column=0, columnspan = 2,  padx=20)     
     
     
        # set default values
        self.sidebar_button_Phase1.configure(state="disabled", text="Phase 1")
        self.sidebar_button_Phase2.configure(state="disabled", text="Phase 2")
        self.sidebar_button_Phase3.configure(state="disabled", text="Phase 3")
        self.file_Format_var.set("Excel")
        
        #Appearance and Scaling Settings - To be Remain as is
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        
        self.List_Box_Company_Selection.bind("<<ListboxSelect>>", self.on_select_company)
        self.Search_Entry_Company_Letter_Word.bind("<KeyRelease>", self.search_company)  
        self.load_user_settings()


    ################################################################# Start of Button Function
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")
        
    def select_folder_path_button_clicked(self):
        folder_path = filedialog.askdirectory()
        self.select_folder_path_var.set(folder_path)
    ################################################################ End of Button Functions 
    
    def load_user_settings(self):     
        try:
            name = self.config.get("UserSettings", "Name")
            email = self.config.get("UserSettings", "Email")
            file_path = self.config.get("UserSettings", "FilePath")
            self.Full_Name_Entry_var.insert(0, name)
            self.Email_Entry_var.insert(0, email)
            self.select_folder_path_var.set(file_path)
        except (configparser.NoSectionError, configparser.NoOptionError):
                # Handle case when config file or section is not found
            pass             

    def save_user_settings(self):
        name = self.Full_Name_Entry_var.get()
        email = self.Email_Entry_var.get()
        file_path = self.select_folder_path_var.get()
        self.config["UserSettings"] = {"Name": name,"Email": email,"FilePath": file_path}
        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

    def validate_input(self):
        selected_companies = self.selected_companies_var.get()
        folder_path = self.select_folder_path_var.get()
        download_type = self.file_Format_var.get()
        Full_Name_Entry = self.Full_Name_Entry_var.get()
        Email_Entry = self.Email_Entry_var.get()

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
    
    def search_company(self, event):
            search_text = self.Search_Entry_Company_Letter_Word.get().lower()
            if search_text:
                matching_options = []
                for index, option in enumerate(self.List_of_All_Companies_From_Json_Tickers):
                    if search_text in option.lower():
                        matching_options.append(option)
                self.List_Box_Company_Selection.delete(0, tk.END)
                for option in matching_options:
                    self.List_Box_Company_Selection.insert(tk.END, option)
            else:
                self.List_Box_Company_Selection.delete(0, tk.END)
                for option in self.List_of_All_Companies_From_Json_Tickers:
                    self.List_Box_Company_Selection.insert(tk.END, option)

    # def on_select_company(self, event):
    #         selected_indices = self.List_Box_Company_Selection.curselection()
            
    #         selected_companies = [self.List_Box_Company_Selection.get(index) for index in selected_indices]

    #         cik_str_list = [self.List_of_All_CIKs_From_Json_Tickers[index] for index in selected_indices]
    #         selected_cik_str = "\n".join(str(cik_str) for cik_str in cik_str_list)

    #         ticker_str_list = [self.List_of_All_Tickers_From_Json_Tickers[index] for index in selected_indices]
    #         selected_ticker_str = "\n".join(str(ticker_str) for ticker_str in ticker_str_list)

    #         self.selected_companies_var.set("\n".join(selected_companies))
    #         self.selected_cik_str_var.set(selected_cik_str)
    #         self.selected_ticker_str_var.set(selected_ticker_str)

    def on_select_company(self, event):
        # selected_indices = []
        # for i in self.List_Box_Company_Selection.curselection():
        #     company_name = self.List_Box_Company_Selection.get(i)
        #     print(company_name)
        #     try:
        #         index = self.List_of_All_Companies_From_Json_Tickers.index(company_name)
        #         selected_indices.append(index)
        #         print(f'Following Index got appended: {selected_indices}')
        #     except ValueError:
        #         pass
        # selected_companies = [self.List_Box_Company_Selection.get(index) for index in selected_indices]
        
        # cik_str_list = [self.List_of_All_CIKs_From_Json_Tickers[index] for index in selected_indices]
        # selected_cik_str = "\n".join(str(cik_str) for cik_str in cik_str_list)

        # ticker_str_list = [self.List_of_All_Tickers_From_Json_Tickers[index] for index in selected_indices]
        # selected_ticker_str = "\n".join(str(ticker_str) for ticker_str in ticker_str_list)
        # print(f"Selected Companies: {selected_companies}")
        # self.selected_companies_var.set("\n".join(selected_companies))
        # self.selected_cik_str_var.set(selected_cik_str)
        # self.selected_ticker_str_var.set(selected_ticker_str)
        
        selected_companies = []
        cik_str_list = []
        ticker_str_list = []
        
        for i in self.List_Box_Company_Selection.curselection():
            company_name = self.List_Box_Company_Selection.get(i)
            print(company_name)
            if company_name in self.List_of_All_Companies_From_Json_Tickers:
                index = self.List_of_All_Companies_From_Json_Tickers.index(company_name)
                selected_companies.append(company_name)
                cik_str_list.append(self.List_of_All_CIKs_From_Json_Tickers[index])
                ticker_str_list.append(self.List_of_All_Tickers_From_Json_Tickers[index])
        
        selected_cik_str = "\n".join(str(cik_str) for cik_str in cik_str_list)
        selected_ticker_str = "\n".join(str(ticker_str) for ticker_str in ticker_str_list)

        self.selected_companies_var.set("\n".join(selected_companies))
        self.selected_cik_str_var.set(selected_cik_str)
        self.selected_ticker_str_var.set(selected_ticker_str)
    




    def load_json_data(self):
        def fetch_json_data():
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.List_of_All_Companies_From_Json_Tickers = [data[key]["title"] for key in data]
                    self.List_of_All_CIKs_From_Json_Tickers = [data[key]["cik_str"] for key in data]
                    self.List_of_All_Tickers_From_Json_Tickers = [data[key]["ticker"] for key in data]
                    
                    for option in self.List_of_All_Companies_From_Json_Tickers:
                        self.List_Box_Company_Selection.insert(tk.END, option)
                        
                    total_companies = len(self.List_of_All_Companies_From_Json_Tickers)
                    print("Total number of companies found:", total_companies)
                
                except json.JSONDecodeError:
                    self.show_error("Failed to parse JSON data")
            else:
                self.show_error("Failed to fetch JSON data")

        threading.Thread(target=fetch_json_data).start()

    

                      
    def submit_button_clicked(self):
        if not self.validate_input():
            return

        folder_path = self.select_folder_path_var.get()
        download_type = self.file_Format_var.get()
        company_CIKS = self.selected_cik_str_var.get()
        company_Name = self.selected_companies_var.get()
        company_tickers = self.selected_ticker_str_var.get()
        full_name = self.Full_Name_Entry_var.get()
        Email_Entry = self.Email_Entry_var.get()
        user_agent= f'{full_name} {Email_Entry}'
        
        self.save_user_settings()
        
        # Redirect stdout and stderr to the debugger_text widget
        sys.stdout = StdoutRedirector(self.debugger_text)
        sys.stderr = StderrRedirector(self.debugger_text)

        string_Lavel_User = f'{folder_path}, {company_Name}, {company_tickers}, {user_agent}'
        # Perform the API extract and download logic

        self.debugger_text.insert(tk.END, "Performing API extract and download...\n")
        self.debugger_text.insert(tk.END, string_Lavel_User + "\n")
    

        cik_list = company_CIKS.split("\n")
        zfilled_cik_list = [cik.strip().zfill(10) for cik in cik_list]
        
        if download_type == "Excel":
            filings1 = Filling_Links(zfilled_cik_list, folder_path, user_agent)
            filings1.get_companyfacts_json_excel()
        elif download_type == "Data Base":
            filings2 = Filling_Links(zfilled_cik_list, folder_path, user_agent)
            filings2.get_companyfacts_json_db()
            
         # Reset the form fields
        self.selected_companies_var.set("")
        self.selected_cik_str_var.set("")
        self.selected_ticker_str_var.set("")
                 
        messagebox.showinfo("Extraction Complete", "API extraction and download complete.")

    def show_error(self, message):
        messagebox.showerror("Error", message)



class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class StderrRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message, "error")  # Apply a custom style for error messages
        self.text_widget.see(tk.END)

    def flush(self):
        pass