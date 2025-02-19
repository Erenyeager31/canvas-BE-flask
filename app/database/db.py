import sqlite3

class DBInstance:
    def __init__(self):
        self.sqliteConnection = sqlite3.connect('topics.db',check_same_thread=False)
        self.cursor = self.sqliteConnection.cursor()
        self.table_name = "topics"  # Constant table name
        print("Init DB successful")
        self.create_table()

    def create_table(self):
        """Creates the table (topics) if it doesn't exist."""
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL
            )
            """
            self.cursor.execute(query)
            self.sqliteConnection.commit()
            print(f"Table '{self.table_name}' created or already exists.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            if self.sqliteConnection:
                self.sqliteConnection.rollback()

    def insert_data(self, filenames):
        """Inserts multiple filenames into the topics table."""
        try:
            print(filenames)
            query = f"INSERT INTO {self.table_name} (filename) VALUES (?)"
            self.cursor.executemany(query, [(filename,) for filename in filenames])
            self.sqliteConnection.commit()
            print("Data inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            if self.sqliteConnection:
                self.sqliteConnection.rollback()

    def delete_data(self, where_clause, params=None):
        """Deletes data from the topics table."""
        try:
            query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.sqliteConnection.commit()
            print("Data deleted successfully")
        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")
            if self.sqliteConnection:
                self.sqliteConnection.rollback()

    def close_connection(self):
        if self.sqliteConnection:
            self.cursor.close()
            self.sqliteConnection.close()
            print("Database connection closed")

    def get_all_filenames(self):
        """Retrieves all filenames as a list without their index."""
        try:
            query = f"SELECT filename FROM {self.table_name}"
            self.cursor.execute(query)
            filenames = [row[0] for row in self.cursor.fetchall()]
            return filenames
        except sqlite3.Error as e:
            print(f"Error retrieving filenames: {e}")
            return []

    def delete_all_data(self):
        """Deletes all data in the table without removing the structure."""
        try:
            query = f"DELETE FROM {self.table_name}"
            self.cursor.execute(query)
            self.sqliteConnection.commit()
            print(f"All data deleted from '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")
            if self.sqliteConnection:
                self.sqliteConnection.rollback()