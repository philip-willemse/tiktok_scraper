from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import requests
import pymysql
import os
import json
from flask_wtf.csrf import CSRFProtect, CSRFError
import csv
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder="static", static_url_path="/static", template_folder="templates")

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:TIKTOKPASS123@localhost/tiktok'
db = SQLAlchemy(app)

# Flask configurations
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Constants for TikAPI integration
BASE_URL = "https://api.tikapi.io"
HEADERS = {
    "X-API-KEY": os.getenv("TIKAPI_X_API_KEY"),
    "Client-Id": os.getenv("TIKAPI_CLIENT_ID"),
    "Api-Key": os.getenv("TIKAPI_API_KEY")
}
JSON_FILE = "tiktok_data.json"

def fetch_data_from_tikapi(country=None, tags=None):
    if not tags:
        print("Tags not provided.")
        return []

    search_endpoint = f"{BASE_URL}/public/search/users"
    params = {
        "query": tags,
    }
    if country:
        params["country"] = country

    response = requests.get(search_endpoint, headers=HEADERS, params=params)
    print("API Request Params:", params)
    print("API Response Status Code:", response.status_code)
    print("Full API Response:", response.json())

    if response.status_code != 200:
        print("API Error Response:", response.json())
        return []

    data = response.json()

    if not data or "users" not in data:
        print("API response doesn't contain user data.")
        return []

    users = data["users"]
    
    # Save the entire API response to a CSV file
    with open('scraped_data.csv', 'w', newline='') as csvfile:
        fieldnames = users[0].keys() if users else []  # Use the keys from the first item if available
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for user in users:
            writer.writerow(user)
    
    return users

def get_user_email(username):
    # Implement your logic here to fetch the user's email from the database
    # This is just a placeholder, replace it with the actual database query
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT email FROM clients WHERE username = %s", (username,))
    user_email = cursor.fetchone()

    if user_email:
        return user_email[0]  # Assuming the email is in the first column of the result
    else:
        return None  # Return None if the user is not found

def get_hashed_password_from_database(username):
    # Implement your logic here to fetch the hashed password from the database
    # This is just a placeholder, replace it with the actual database query
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT password FROM clients WHERE username = %s", (username,))
    hashed_password = cursor.fetchone()

    if hashed_password:
        return hashed_password[0]  # Assuming the hashed password is in the first column of the result
    else:
        return None  # Return None if the user is not found

def login():
    if request.method == 'POST':
        # Handle the login logic here
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch the hashed password from the database
        hashed_password_from_database = get_hashed_password_from_database(username)

        if hashed_password_from_database and check_password_hash(hashed_password_from_database, password):
            # Login is successful
            session['username'] = username  # Set the session variable
            return redirect(url_for('dashboard'))  # Redirect to the 'dashboard' route
        else:
            flash("Invalid credentials. Please try again.", 'error')

    # If it's a GET request or login fails, display the login form
    return render_template('login.html')

@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password_from_database = get_hashed_password_from_database(username)

        if hashed_password_from_database and check_password_hash(hashed_password_from_database, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", 'error')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Retrieve database connection variables from environment variables
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')
    
    # Check if the user is logged in (you can customize this logic)
    if 'username' in session:
        # Get the username from the session
        username = session['username']
        
        # You can fetch additional user data (e.g., email) and pass it to the template
        user_email = get_user_email(username)  # Implement this function to fetch user email
        
        # Pass the username and user_email to the template
        # Also pass the database connection variables
        collected_data = fetch_collected_data(username, db_host, db_user, db_password, db_name)
        
        return render_template('dashboard.html', username=username, user_email=user_email, collected_data=collected_data)
    else:
        flash("You must be logged in to access the dashboard.", 'error')
        return redirect(url_for('login'))


def fetch_collected_data(username, db_host, db_user, db_password, db_name):
    # Get the client_id based on the username
    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT client_id FROM clients WHERE username = %s", (username,))
    client_id = cursor.fetchone()

    if client_id:
        # Fetch collected data based on the client_id
        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM tiktok_users WHERE client_id = %s", (client_id[0],))
        collected_data = cursor.fetchall()

        return collected_data
    else:
        return []  # Return an empty list if the user is not found

# Flask endpoint to fetch collected data
@app.route("/get_collected_data", methods=["GET"])
def get_collected_data():
    # Fetch data from the database (Replace this with your actual SQL query)
    data = fetch_data_from_db()
    print("Debug: get_collected_data accessed")
    return jsonify(data)

# Function to fetch data from the database
conn = pymysql.connect(host="localhost", user="root", password="TIKTOKPASS123", db="tiktok")
cursor = conn.cursor()
sql_query = "SELECT * FROM tiktok_users"
cursor.execute(sql_query)
data = cursor.fetchall()
conn.close()
def fetch_data_from_db():
    # Example data (Replace this with your actual SQL query result)
    example_data = [
        {"nickname": "user1", "signature": "sig1", "uid": "uid1", "unique_id": "unique1"},
        {"nickname": "user2", "signature": "sig2", "uid": "uid2", "unique_id": "unique2"}
    ]
    return example_data

# Function to add a new column to the table if it doesn't exist
def add_column_if_not_exists(column_name, data_type):
    table_name = 'tiktok_users'
    connection = db.engine.connect()
    existing_columns = db.engine.execute(f"DESCRIBE {table_name};")
    
    # Check if the column already exists
    if any(column[0] == column_name for column in existing_columns):
        return
    
    # Add the new column
    connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type};")

@app.route('/scrape_data', methods=['POST'])
def scrape_data():
    if 'username' in session:
        # Extract other scraping parameters from the form data
        country = request.form.get('country')
        min_followers = request.form.get('min_followers')
        max_followers = request.form.get('max_followers')
        tags = request.form.get('tags')

        # Perform the scraping based on the parameters
        print("Scraping parameters:", country, min_followers, max_followers, tags)
        scraped_data = fetch_data_from_tikapi(country=country, tags=tags)

        # Check if scraped_data is not empty
        if scraped_data:
            # Extract user data from the API response
            user_data = []
            for user in scraped_data:
                user_info = user.get('user_info', {})
                user_data.append({
                    'username': user_info.get('nickname', ''),
                    'followers': user_info.get('follower_count', ''),
                    'country': user_info.get('country', ''),
                    'tags': tags  # Assuming you want to store the input tags
                })

            # Save the scraped data to a CSV file
            with open('scraped_data.csv', 'w', newline='') as csvfile:
                fieldnames = ['username', 'followers', 'country', 'tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user in user_data:
                    writer.writerow(user)

            flash("Scraping completed successfully.", 'success')
        else:
            flash("No data was scraped.", 'warning')
    else:
        flash("You must be logged in to scrape data.", 'error')

    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['GET'])
def logout():
    # Implement logout logic here
    # For example, you can clear the user session and redirect to the login page
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not username or not password or not email:
            flash("Username or email already exists!", 'error')
        else:
            hashed_password = generate_password_hash(password, method='sha256')

            # Insert the user into the database
            db_host = os.getenv("DB_HOST", 'localhost')
            db_user = os.getenv("DB_USER", 'root')
            db_password = os.getenv("DB_PASSWORD")
            db_name = os.getenv("DB_NAME", 'tiktok')

            connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
            cursor = connection.cursor()

            # Check if user already exists
            cursor.execute("SELECT * FROM clients WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username or email already exists!", 'error')
            else:
                # Insert new user
                cursor.execute("INSERT INTO clients (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
                connection.commit()

            return render_template('register.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
