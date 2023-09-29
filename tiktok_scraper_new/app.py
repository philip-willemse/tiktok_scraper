from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

# Constants for TikAPI integration
BASE_URL = "https://api.tikapi.io"
HEADERS = {
    "X-API-KEY": os.getenv("TIKAPI_X_API_KEY"),
    "Client-Id": os.getenv("TIKAPI_CLIENT_ID"),
    "Api-Key": os.getenv("TIKAPI_API_KEY")
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

def fetch_data_from_tikapi(tags=None):
    if not tags:
        print("Tags not provided.")
        return []

    search_endpoint = f"{BASE_URL}/public/search/users"
    params = {
        "query": tags,
    }

    response = requests.get(search_endpoint, headers=HEADERS, params=params)
    print("API Request Params:", params)
    print("API Response Status Code:", response.status_code)
    print("Full API Response:", response.json())

    if response.status_code != 200:
        print("API Error Response:", response.json())
        return []

    data = response.json()
    return data

def fetch_tiktok_profile(username):
    url = f"https://api.tiktok.com/node/share/user/@{username}?unique_id={username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        profile_data = data.get('body', {}).get('userData', {})
        
        unique_id = profile_data.get('unique_id', 'N/A')
        sec_uid = profile_data.get('sec_uid', 'N/A')
        nickname = profile_data.get('nickname', 'N/A')
        signature = profile_data.get('signature', 'N/A')
        follower_count = profile_data.get('follower_count', 'N/A')
        
        return {
            "Unique ID": unique_id,
            "Sec UID": sec_uid,
            "Nickname": nickname,
            "Signature": signature,
            "Follower Count": follower_count
        }
    else:
        return {"error": f"Failed to fetch profile for {username}. Status Code: {response.status_code}"}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.password == password:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})

@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.json.get('username')
    password = request.json.get('password')
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"status": "Account created successfully"})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/fetch_tag', methods=['GET'])
def fetch_tag():
    tag = request.args.get('tag')
    if not tag:
        return jsonify({"error": "Tag is required"}), 400

    tag_data = fetch_data_from_tikapi(tag)
    if not tag_data:
        return jsonify({"error": "No data found for the given tag"}), 404

    # Extract and format only the relevant information
    formatted_data = []
    for user in tag_data.get('user_list', []):
        user_info = user.get('user_info', {})
        formatted_data.append({
            "nickname": user_info.get("nickname", "N/A"),
            "follower_count": user_info.get("follower_count", "N/A"),
            "signature": user_info.get("signature", "N/A")
        })

    return jsonify({"Tag Data from TikAPI": formatted_data}), 200

@app.route('/get_tiktok_profile', methods=['GET'])
def get_tiktok_profile():
    username = request.args.get('username')
    if username:
        profile_data = fetch_tiktok_profile(username)
        return render_template('tiktok_profile.html', profile_data=profile_data)
    else:
        return jsonify({"error": "Username parameter is missing"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
