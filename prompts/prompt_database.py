import sqlite3
import os
from datetime import datetime

DATABASE_FILENAME = 'prompts.db'
script_directory = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH= os.path.join(script_directory,DATABASE_FILENAME)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def read_item(data, version_number):
    conn = get_db_connection()

    query = f'SELECT {data} FROM item_versions WHERE version_number = ? AND {data} IS NOT NULL ORDER BY id LIMIT 1'
    item = conn.execute(query,(version_number,)).fetchone()
    conn.close()
    if item is not None:
        readable_string = str(item[0])
    else:
        return "No data found"
    return readable_string

# USED TO DELETE A VERSION FROM DATABASE
class DeletePrompts:
    def __init__(self, column_name, version_to_delete):
        self.column_name = column_name
        self.version_to_delete = version_to_delete

    def delete_single_entry_by_version_number(self, cursor, version_number, column_name):
        # Delete only one entry where 'age' is not NULL for the specified version number
        cursor.execute(f"DELETE FROM item_versions WHERE id = (SELECT id FROM item_versions WHERE version_number = ? AND {column_name} IS NOT NULL LIMIT 1)", (version_number,))

    def delete_item(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Delete one entry with the specified version number
        self.delete_single_entry_by_version_number(cursor, self.version_to_delete, self.column_name)
        conn.commit()

        # Close the connection
        conn.close()

        return f"Version {self.version_to_delete} has been deleted from the {self.column_name} column."

# USED FOR LOADING NUMBER OF PROMPT VERSIONS
class LoadPrompts:
    def __init__(self, column_name=None):
        self.column_name = column_name
        self.default_columns = ['age', 'languageSkills', 'location']
    
    def get_all_version_numbers_for_column(self, cursor, column_name):
        query = f"SELECT DISTINCT version_number FROM item_versions WHERE {column_name} IS NOT NULL ORDER BY version_number"
        cursor.execute(query)
        # Fetch all results instead of just one
        versions = cursor.fetchall()
        version_numbers = [version[0] for version in versions]
        return version_numbers

    def load_prompts(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        version_numbers = {}

        if self.column_name:
            versions = self.get_all_version_numbers_for_column(cursor, self.column_name)
            version_numbers[self.column_name] = versions
        else:
            for column_name in self.default_columns:
                versions = self.get_all_version_numbers_for_column(cursor, column_name)
                version_numbers[column_name] = versions

        conn.close()

        return version_numbers

# USED FOR SAVING NEW PROMPTS
class SavePrompts:
    def __init__(self, new_prompt, column_name):
        self.column_name = column_name
        self.new_prompt = new_prompt
        
    def get_next_version_number(self,cursor, column_name):
        # Find the highest version number for the specified column
        cursor.execute(f"SELECT MAX(version_number) FROM item_versions WHERE {column_name} IS NOT NULL")
        max_version = cursor.fetchone()[0]

        # Check if there are any entries for this column
        if max_version is None:
            return 1

        # Find the next available version number
        for version in range(1, max_version + 2):
            cursor.execute(f"SELECT COUNT(*) FROM item_versions WHERE version_number = ? AND {column_name} IS NOT NULL", (version,))
            if cursor.fetchone()[0] == 0:
                return version

        return max_version + 1

    def insert_new_version(self, cursor, column_name, version_number, value):
        # Insert a new entry with the specified version number
        cursor.execute(f"INSERT INTO item_versions (version_number, {column_name}, version_date) VALUES (?, ?, ?)", (version_number, value, datetime.now()))

    def create_versions(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get the next version number for the 'age' column
        next_version = self.get_next_version_number(cursor, self.column_name)

        # Insert a new entry with the next version number (example value for 'age' is 30)
        self.insert_new_version(cursor, self.column_name, next_version, self.new_prompt)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return "Saved"