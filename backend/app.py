from flask import Flask, jsonify, request, send_from_directory, render_template
import logging
import requests
import json
import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder="../frontend", static_url_path="/", template_folder="../frontend")


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

@app.route('/fetch_data', methods=['POST'])
def fetch_data_endpoint():
    country = request.json.get('country')
    tags = request.json.get('tags')
    data = fetch_data_from_tikapi(country, tags)
    
    logging.debug(f"API Response: {data}")

    try:
        if 'user_list' in data and data['user_list']:
            user_info = data['user_list'][0]['user_info']
            with open(JSON_FILE, 'w') as file:
                json.dump(user_info, file, indent=4)
            insert_data_to_database(user_info)
        else:
            logging.error("Key 'user_list' not found in API response or it's empty.")
            return jsonify({"error": "Unexpected API response format."})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)})
    
    return jsonify({"message": "Data fetched and inserted into the database successfully!", "file": JSON_FILE})

@app.route('/download_json', methods=['GET'])
def download_json():
    return send_from_directory('.', JSON_FILE, as_attachment=True)

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/display_data', methods=['GET'])
def display_data():
    data = fetch_data_from_database()
    return render_template('display.html', data=data)

def insert_data_to_database(user_info):
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO tiktok_users (follower_count, nickname, signature, uid, unique_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (user_info['follower_count'],
                                  user_info['nickname'],
                                  user_info.get('signature', ''),
                                  user_info['uid'],
                                  user_info['unique_id']))
    connection.commit()
    cursor.close()
    connection.close()

def fetch_data_from_database():
    db_host = os.getenv("DB_HOST", 'localhost')
    db_user = os.getenv("DB_USER", 'root')
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", 'tiktok')

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    fetch_query = "SELECT * FROM tiktok_users"
    cursor.execute(fetch_query)
    data = cursor.fetchall()

    cursor.close()
    connection.close()
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
