from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import os
import json
import requests
from flask_mail import Mail, Message
import uuid

# Configuration
app = Flask(__name__, static_url_path='', static_folder='../frontend')

app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/tiktok'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask Login Config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mail Config
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = '2525'
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(256), nullable=True, unique=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        token = str(uuid.uuid4())
        new_user.token = token
        
        db.session.add(new_user)
        db.session.commit()

        msg = Message('Email Verification', sender='noreply@yourdomain.com', recipients=[email])
        msg.body = f'Please click the following link to verify your email: {url_for("verify", token=token, _external=True)}'
        mail.send(msg)

        flash('Thanks for signing up! Please check your email to verify your account.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    user = User.query.filter_by(token=token).first()
    if not user:
        return 'Token is invalid!', 400

    user.email_verified = True
    db.session.commit()
    
    flash('Your email has been verified!')
    return redirect(url_for('login'))

@app.route('/tiktok', methods=['GET'])
def tiktok_users():
    url = "https://api.tikapi.io/discover/user"
    headers = {
        "apikey": "YOUR_API_KEY"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

@app.route('/tiktok/<username>', methods=['GET'])
def tiktok_user(username):
    url = f"https://api.tikapi.io/user/{username}"
    headers = {
        "apikey": "YOUR_API_KEY"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

@app.route('/tiktok/<username>/followings', methods=['GET'])
def tiktok_user_followings(username):
    url = f"https://api.tikapi.io/user/{username}/following"
    headers = {
        "apikey": "YOUR_API_KEY"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

@app.route('/tiktok/<username>/followers', methods=['GET'])
def tiktok_user_followers(username):
    url = f"https://api.tikapi.io/user/{username}/followers"
    headers = {
        "apikey": "YOUR_API_KEY"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

@app.route('/tiktok/<username>/liked', methods=['GET'])
def tiktok_user_liked(username):
    url = f"https://api.tikapi.io/user/{username}/liked"
    headers = {
        "apikey": "YOUR_API_KEY"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

@app.route('/')
@login_required
def index():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
