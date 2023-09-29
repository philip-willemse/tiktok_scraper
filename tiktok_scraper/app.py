from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import requests
import pymysql
import os
from flask_wtf.csrf import CSRFProtect
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
    "x-api-key": "q9D43JnetinWD5JIwhfiQaHJACzKkx7JHBmCmCJgv8f8XHZn",
    "client-id": "c_4Y8MUIXBOR"
}

def fetch_data_from_tikapi(country=None, tags=None):
    try:
        print("Debug: fetch_data_from_tikapi accessed")
        url = f"{BASE_URL}/some/endpoint"
        params = {
            "country": country,
            "tags": tags
        }
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print("Debug: API response code:", response.status_code)
            return []
        
        data = response.json()
        
        if not isinstance(data, list):
            print("Debug: API response is not a list:", data)
            return []
        
        users = [item.get('user_info', {}) for item in data]
        print("Debug: Data fetched from API")
        return users
    except Exception as e:
        print("Debug: Exception occurred in fetch_data_from_tikapi:", e)
        return []

    # Extracting the 'user_info' key from each dictionary in the list
    users = [item.get('user_info', {}) for item in data]

    if not users:
        print("API response doesn't contain user data.")
        return []

    # Save the data to the MySQL database
    connection = pymysql.connect(host="localhost", user="root", password="TIKTOKPASS123", db="tiktok")
    cursor = connection.cursor()
    
    for user_info in users:
        username = user_info.get('nickname', '')
        followers = user_info.get('follower_count', 0)
        country = user_info.get('country', '')
        
        # Insert data into the tiktok_users table
        sql_query = "INSERT INTO tiktok_users (username, followers, country) VALUES (%s, %s, %s)"
        cursor.execute(sql_query, (username, followers, country))
    
    # Commit the changes to save the data
    connection.commit()
    
    # Close the connection
    connection.close()

    return users

# Example usage

fetch_data_from_tikapi(country="US", tags="fortnite")
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
        tags = request.form.get('tags')

        # Perform the scraping based on the parameters
        print("Scraping parameters:", country, tags)
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

            # Save the scraped data to the MySQL database
            connection = pymysql.connect(host="localhost", user="root", password="TIKTOKPASS123", db="tiktok")
            cursor = connection.cursor()
            
            for user in user_data:
                username = user['username']
                followers = user['followers']
                country = user['country']
                tags = user['tags']
                
                # Insert data into the tiktok_users table
                sql_query = "INSERT INTO tiktok_users (username, followers, country, tags) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_query, (username, followers, country, tags))
            
            # Commit the changes to save the data
            connection.commit()
            
            # Close the connection
            connection.close()
            
            flash("Scraping and data saving completed successfully.", 'success')
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
