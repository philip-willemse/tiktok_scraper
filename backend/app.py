from dotenv import load_dotenv
from pysendpulse.pysendpulse import PySendPulse
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import requests
import pymysql
import os
import json
from itsdangerous import URLSafeTimedSerializer
from flask_wtf.csrf import CSRFProtect, CSRFError
from database import get_hashed_password_from_database  # Import the function from database.py

# Load environment variables
load_dotenv()

# SendPulse Credentials
SENDPULSE_ID = os.getenv('SENDPULSE_ID')
SENDPULSE_SECRET = os.getenv('SENDPULSE_SECRET')

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder="static", static_url_path="/static", template_folder="templates")

# Flask configurations
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Create the serializer object after the app object
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Initialize CSRF protection
csrf = CSRFProtect(app)

def validate_csrf_token(token):
    # Implement your validation logic here
    # You can compare the token with the one generated for the user's session
    return token == session.get('csrf_token')

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
    return data

def send_email(to_email, subject, html_content):
    SP_API = PySendPulse(SENDPULSE_ID, SENDPULSE_SECRET, 'token_storage.txt')

    email = {
        'html': html_content,
        'text': 'text version of your email',
        'subject': subject,
        'from': {
            'name': 'Check Coverage',
            'email': 'socialmedia@smartafrica.co.za'
        },
        'to': [
            {
                'email': to_email
            }
        ]
    }

    result = SP_API.smtp_send_mail(email)
    logging.info(f"SendPulse API Response: {result}")

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

    cursor.close()
    connection.close()

    if user_email:
        return user_email[0]  # Assuming the email is in the first column of the result
    else:
        return None  # Return None if the user is not found

@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
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

def fetch_collected_data(username, db_host, db_user, db_password, db_name):
    # Implement your logic here to fetch collected data from the database
    # You may need to adapt this code to match your database schema and queries
    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tiktok_users WHERE client_id = (SELECT client_id FROM clients WHERE username = %s)", (username,))
    collected_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return collected_data


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

# Add a new function to fetch collected data from the database
def fetch_collected_data_from_database():
    # Implement your logic here to fetch the collected data from the database
    # This is just a placeholder, replace it with the actual database query
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tiktok_users")
    collected_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return collected_data  # Return the fetched data

@app.route('/scrape_data', methods=['POST'])
def scrape_data():
    if 'username' in session:
        # Extract other scraping parameters from the form data
        country = request.form.get('country')
        min_followers = request.form.get('min_followers')
        max_followers = request.form.get('max_followers')
        tags = request.form.get('tags')

        # Perform the scraping based on the parameters
        scraped_data = fetch_data_from_tikapi(country=country, tags=tags)

        # Save the scraped data to the JSON file
        with open(JSON_FILE, 'w') as json_file:
            json.dump(scraped_data, json_file)

        flash("Scraping completed successfully.", 'success')
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

                # After successful registration, send confirmation email
                email_token = serializer.dumps(email, salt='email-confirmation')
                confirmation_link = url_for('confirm_email', token=email_token, _external=True)

                html_content = f'''
                <!DOCTYPE html>
                <html>
                <!-- Rest of the HTML content for the confirmation email -->
                </html>
                '''

                # Replace the placeholder with the actual confirmation link
                html_content = html_content.replace('{confirmation_link}', confirmation_link)

                send_email(email, 'Email Confirmation', html_content)

                flash("Registration successful! Please check your email for a verification link.", 'success')
                return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirmation', max_age=3600)
    except Exception as e:
        logging.error("An error occurred while processing the confirmation link.", exc_info=True)
        return "The confirmation link is invalid or has expired.", 400

    # Mark email as confirmed in the database
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM clients WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if not existing_user:
        flash("User not found.", 'error')
        return redirect(url_for('login'))

    cursor.execute("UPDATE clients SET email_verified = TRUE WHERE email = %s", (email,))
    connection.commit()

    cursor.close()
    connection.close()

    # Log the user in
    session['username'] = email

    flash("Email verification successful! You can now log in.", 'success')

    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
