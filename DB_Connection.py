import os
import sqlite3
from sqlite3 import Error
import sys

class DB_Connection:
    # Initialize the object's attributes.
    def __init__(self, db_name, folder_path):
        self.db_name = db_name
        self.folder_path = folder_path
 
    # Create a directory for the DB file if the directory does not exist.
    def create_folder(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            print(f'Successfully created a new folder path {self.folder_path}.')
        else:
            print(f'Folder path {self.folder_path} already exists.')
 

    def create_table_of_contents(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()

            # Drop existing table_of_contents table if it exists
            c.execute("DROP TABLE IF EXISTS table_of_contents")

            # Create table_of_contents table
            c.execute('''
                CREATE TABLE table_of_contents (
                    id INTEGER PRIMARY KEY,
                    table_name TEXT
                );
            ''')

            # Insert table names into table_of_contents
            c.execute('''
                INSERT INTO table_of_contents (table_name) 
                SELECT name FROM sqlite_master WHERE type='table';
            ''')

            conn.commit()
            print("Table of Contents created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    # Open connection to the database, if connection fails abort the program.
    # If the DB file does not already exist, it will be automatically created.
    @classmethod
    def open_conn(cls, db_path):
        try:
            cls.conn = sqlite3.connect(db_path)
            print(f'Successfully connected to the {db_path} database.')
            return cls.conn
        except sqlite3.Error as e:
            print(f'Error occurred, unable to connect to the {db_path} database.\
                    \n{e}\nAbording program.')
            # sys.exit(0) means the program is exiting without any errors
            # sys.exit(1) means there was an error.
            sys.exit(1)
    # Close connection to the database.
    
    @classmethod
    def close_conn(cls):
        try:
            cls.conn.commit()
            print('Committed transactions.')
            cls.conn.close()
            print('Closing all database connections.')
        except Exception as e:
            print(f'Unable to close database connection.\n{e}')




