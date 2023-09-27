# database.py

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_hashed_password_from_database(username):
    try:
        # Create a database connection
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", 'localhost'),
            user=os.getenv("DB_USER", 'root'),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", 'tiktok')
        )
        cursor = connection.cursor()

        # Execute a query to retrieve the hashed password for the given username
        cursor.execute("SELECT password FROM clients WHERE username = %s", (username,))
        hashed_password = cursor.fetchone()

        if hashed_password:
            return hashed_password[0]  # Return the hashed password
        else:
            return None  # Return None if the user does not exist

    except Exception as e:
        # Handle any database-related exceptions here
        print("Error fetching hashed password from the database:", str(e))
        return None
