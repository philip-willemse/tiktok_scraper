from flask import Flask, jsonify, request, send_from_directory
import requests
import json

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

# Constants for TikAPI integration
BASE_URL = "https://api.tikapi.io"
HEADERS = {
    "X-API-KEY": "q9D43JnetinWD5JIwhfiQaHJACzKkx7JHBmCmCJgv8f8XHZn",
    "Client-Id": "c_4Y8MUIXBOR",
    "Api-Key": "q9D43JnetinWD5JIwhfiQaHJACzKkx7JHBmCmCJgv8f8XHZn"
}
JSON_FILE = "tiktok_data.json"

def fetch_data_from_tikapi(country=None, tags=None):
    # Check if tags are provided
    if not tags:
        print("Tags not provided.")
        return []

    search_endpoint = f"{BASE_URL}/public/search/users"
    params = {
        "query": tags,
    }
    if country:
        params["country"] = country  # Add country parameter if provided

    print("API Request Params:", params)

    response = requests.get(search_endpoint, headers=HEADERS, params=params)
    print("API Response Status Code:", response.status_code)

    if response.status_code != 200:
        print("API Error Response:", response.json())
        return []

    data = response.json()

    return data

@app.route('/fetch_data', methods=['POST'])
def fetch_data_endpoint():
    country = request.json.get('country')
    tags = request.json.get('tags')
    print("Tags received:", tags)
    data = fetch_data_from_tikapi(country, tags)
    
    try:
        with open(JSON_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Error writing to JSON:", str(e))
        return jsonify({"error": "Error writing to JSON"})
    
    return jsonify({"message": "Data fetched successfully!", "file": JSON_FILE})

@app.route('/download_json', methods=['GET'])
def download_json():
    return send_from_directory('.', JSON_FILE, as_attachment=True)

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
