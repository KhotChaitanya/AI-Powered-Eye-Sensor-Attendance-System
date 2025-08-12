import sqlite3
import json

# This function connects to the database and creates the 'users' table if it doesn't exist yet.
def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create a table to store user_id, name, and the face embedding.
    # The embedding is stored as TEXT because SQLite doesn't have an array type.
    # We will use the JSON library to convert the list of numbers into a string.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# This function adds a new user to the database.
def add_user(name, embedding):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Convert the embedding (which is a list of numbers) into a JSON string to store it.
    embedding_json = json.dumps(embedding)
    
    # Insert the user's name and their embedding string into the 'users' table.
    cursor.execute("INSERT INTO users (name, embedding) VALUES (?, ?)", (name, embedding_json))
    
    conn.commit()
    conn.close()
    print(f"User '{name}' has been added to the database.")


if __name__ == '__main__':
    create_table()
    print("Database table created successfully.")