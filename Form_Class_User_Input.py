import sys
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
import json
import threading
from Filling_Links import Filling_Links
import configparser

class UserInputForm:
    def __init__(self):

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        


        self.window = tk.Tk()
        
        
        self.window.title("SEC Exchange API Extract")
        self.window.geometry("900x600")
        self.window.configure(bg="#042940")

        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        self.window.grid_rowconfigure(4, weight=2)
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_rowconfigure(6, weight=1)
        self.window.grid_rowconfigure(7, weight=1)
        self.window.grid_rowconfigure(8, weight=1)
        self.window.grid_rowconfigure(9, weight=1)
        self.window.grid_rowconfigure(10, weight=1)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_columnconfigure(3, weight=1)
        self.window.grid_columnconfigure(4, weight=1)


        title_label = tk.Label(self.window, text="SEC Exchange API Extract", font=("Arial", 14, "bold"), bg="#042940", fg="white")
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.select_company_label = tk.Label(self.window, text="Select Company Name:", bg="#005C53", fg="white", width=20, justify="left")
        self.select_company_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        
       
        self.Full_Name_label = tk.Label(self.window, text="First and Family Name:", bg="#005C53", fg="white", width=20, justify="left")
        self.Full_Name_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        self.Full_Name_Entry_var = tk.Entry(self.window)
        self.Full_Name_Entry_var.grid(row=1, column=1, sticky="we", padx=10)
        

        self.Enter_Email_label = tk.Label(self.window, text="Email:", bg="#005C53", fg="white", width=20, justify="left")
        self.Enter_Email_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.Email_Entry_var = tk.Entry(self.window)
        self.Email_Entry_var.grid(row=2, column=1, sticky="we", padx=10)


        listbox_frame = tk.Frame(self.window)
        listbox_frame.grid(row=3, column=1, columnspan=1, rowspan=2, sticky="nsew")
        self.select_company_listbox = tk.Listbox(listbox_frame, selectmode="extended", exportselection=False, width=50)
        self.select_company_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.load_json_data()

        self.search_entry = tk.Entry(self.window)
        self.search_entry.grid(row=4, column=2, sticky="we", padx=10)
        self.search_entry.bind("<KeyRelease>", self.search_company)

        self.select_company_label = tk.Label(self.window, text="Filter Companies:", bg="#005C53", fg="white", width=20, justify="left")
        self.select_company_label.grid(row=3, column=2, sticky="w", padx=10, pady=10)

        vertical_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.select_company_listbox.yview)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        horizontal_scrollbar = tk.Scrollbar(self.window, orient=tk.HORIZONTAL, command=self.select_company_listbox.xview)
        horizontal_scrollbar.grid(row=5, column=1, sticky="ew", columnspan=1)
        self.select_company_listbox.config(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

        self.selected_companies_var = tk.StringVar()
        self.selected_companies_label = tk.Label(self.window, textvariable=self.selected_companies_var, bg="#005C53", fg="white", height=5, wraplength=200, justify="left", width=50)
        self.selected_companies_label.grid(row=6, column=1, rowspan=2, sticky="w", padx=10, pady=10)

        self.selected_ticker_str_var = tk.StringVar()
        self.selected_companies_label = tk.Label(self.window, textvariable=self.selected_ticker_str_var, bg="#005C53", fg="white", height=5, wraplength=200, justify="left", width=50)
        self.selected_companies_label.grid(row=6, column=0, rowspan=2, sticky="w", padx=10, pady=10)
        
        
        self.selected_cik_str_var = tk.StringVar()
        self.selected_cik_str_label = tk.Label(self.window, textvariable=self.selected_cik_str_var, bg="#005C53", fg="white", height=5, wraplength=200, justify="left", width=50)
        self.selected_cik_str_label.grid(row=6, column=2, rowspan=2, sticky="w", padx=10, pady=10)
                                 
                                           
        self.select_folder_path_label = tk.Label(self.window, text="Select Folder Path:", bg="#005C53", fg="white")
        self.select_folder_path_label.grid(row=8, column=0, sticky="w", padx=10, pady=10)

        self.select_folder_path_var = tk.StringVar()
        self.select_folder_path_entry = tk.Entry(self.window, textvariable=self.select_folder_path_var, state="readonly")
        self.select_folder_path_entry.grid(row=8, column=2, columnspan=2, padx=10, pady=10, sticky="we")
        

        self.select_folder_path_button = tk.Button(self.window, text="Browse", command=self.select_folder_path_button_clicked)
        self.select_folder_path_button.grid(row=8, column=1, padx=10, pady=10, sticky="w")

        self.download_type_var = tk.StringVar()
        self.csv_checkbox = tk.Checkbutton(self.window, text="Excel", variable=self.download_type_var, onvalue="Excel", offvalue="")
        self.csv_checkbox.grid(row=10, column=2, sticky="w", padx=10, pady=10)

        self.db_checkbox = tk.Checkbutton(self.window, text="DB", variable=self.download_type_var, onvalue="db", offvalue="")
        self.db_checkbox.grid(row=10, column=1, sticky="w", padx=10, pady=10)

        self.submit_button = tk.Button(self.window, text="Submit", command=self.submit_button_clicked)
        self.submit_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

        self.debugger_text = tk.Text(self.window, height=4, width=50, state="normal")
        self.debugger_text.grid(row=12, column=0, columnspan=3, padx=10, pady=10)
   
        # Create the cancel button
        self.cancel_operation = False
        self.cancel_button = tk.Button(self.window, text="Cancel", command=self.cancel_button_clicked)
        self.cancel_button.grid(row=11, column=1, columnspan=1, padx=10, pady=10)

        self.select_company_listbox.bind("<<ListboxSelect>>", self.on_select_company)

        # Configure grid weight to expand listbox and label
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        
        self.load_user_settings()

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

        self.config["UserSettings"] = {
            "Name": name,
            "Email": email,
            "FilePath": file_path
        }

        with open("config.ini", "w") as config_file:
            self.config.write(config_file)


    def search_company(self, event):
        search_text = self.search_entry.get().lower()
        if search_text:
            # Filter the listbox options based on the search text
            matching_options = [option for option in self.all_companies if search_text in option.lower()]
            self.select_company_listbox.delete(0, tk.END)
            for option in matching_options:
                self.select_company_listbox.insert(tk.END, option)
        else:
            # If the search box is empty, display the original list of options
            self.select_company_listbox.delete(0, tk.END)
            for option in self.all_companies:
                self.select_company_listbox.insert(tk.END, option)


    def load_json_data(self):
        def fetch_json_data():
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.all_companies = [data[key]["title"] for key in data]
                    self.all_companies_cik = [data[key]["cik_str"] for key in data]
                    self.all_companies_ticker = [data[key]["ticker"] for key in data]
                    self.update_company_listbox()
                    total_companies = len(self.all_companies)
                    print("Total number of companies found:", total_companies)
                
                except json.JSONDecodeError:
                    self.show_error("Failed to parse JSON data")
            else:
                self.show_error("Failed to fetch JSON data")

        threading.Thread(target=fetch_json_data).start()

    def update_company_listbox(self):
        for option in self.all_companies:
            self.select_company_listbox.insert(tk.END, option)

    def select_folder_path_button_clicked(self):
        folder_path = filedialog.askdirectory()
        self.select_folder_path_var.set(folder_path)

    def validate_input(self):
        selected_companies = self.selected_companies_var.get()
        folder_path = self.select_folder_path_var.get()
        download_type = self.download_type_var.get()

        
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

    def on_select_company(self, event):
            selected_indices = self.select_company_listbox.curselection()
            selected_companies = [self.select_company_listbox.get(index) for index in selected_indices]

            cik_str_list = [self.all_companies_cik[index] for index in selected_indices]
            selected_cik_str = "\n".join(str(cik_str) for cik_str in cik_str_list)

            ticker_str_list = [self.all_companies_ticker[index] for index in selected_indices]
            selected_ticker_str = "\n".join(str(ticker_str) for ticker_str in ticker_str_list)

            self.selected_companies_var.set("\n".join(selected_companies))
            self.selected_cik_str_var.set(selected_cik_str)
            self.selected_ticker_str_var.set(selected_ticker_str)
        
            
    def submit_button_clicked(self):
        if not self.validate_input():
            return

        folder_path = self.select_folder_path_var.get()
        download_type = self.download_type_var.get()
        company_CIKS = self.selected_cik_str_var.get()
        full_name = self.Full_Name_Entry_var.get()
        Email_Entry = self.Email_Entry_var.get()

        user_agent= f'{full_name} {Email_Entry}'
        
        self.save_user_settings()
        
        # Redirect stdout and stderr to the debugger_text widget
        sys.stdout = StdoutRedirector(self.debugger_text)
        sys.stderr = StderrRedirector(self.debugger_text)


        # Perform the API extract and download logic
        self.debugger_text.insert(tk.END, "Performing API extract and download...\n")
        self.debugger_text.insert(tk.END, {folder_path}, {company_CIKS}, {user_agent})
        
        
        # Reset the form fields
        self.selected_companies_var.set("")
        self.selected_cik_str_var.set("")
        self.selected_ticker_str_var.set("")
        
        self.csv_checkbox.deselect()
        self.db_checkbox.deselect()
        cik_list = company_CIKS.split("\n")
        zfilled_cik_list = [cik.strip().zfill(10) for cik in cik_list]
        
        
        if download_type == "Excel":
            filings1 = Filling_Links(zfilled_cik_list, folder_path, user_agent)
            filings1.get_companyfacts_json_excel()
        elif download_type == "db":
            filings2 = Filling_Links(zfilled_cik_list, folder_path, user_agent)
            filings2.get_companyfacts_json_db()
    
        # Check if the operation was canceled
        if self.cancel_operation:
            self.debugger_text.insert(tk.END, "Operation canceled.\n")
        else:
            messagebox.showinfo("Extraction Complete", "API extraction and download complete.")
                     
        messagebox.showinfo("Extraction Complete", "API extraction and download complete.")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def run(self):
        self.window.mainloop()

    def cancel_button_clicked(self):
        self.cancel_operation = True

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