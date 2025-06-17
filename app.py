
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='frontend')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

CORS(app)
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

# User registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='User already exists')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = email
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' in session:
        return send_from_directory('frontend', 'index.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Task API
@app.route('/task_list', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{"id": task.id, "name": task.name} for task in tasks])

@app.route('/task_list', methods=['POST'])
def add_task():
    data = request.json
    new_task = Task(name=data['name'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added successfully!"}), 201

# In your app.py or routes.py
from flask import render_template, request, redirect, url_for, flash


if __name__ == '__main__':
    app.run(debug=True)