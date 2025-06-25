import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

ALLOWED_CATEGORIES = ['school', 'work', 'personal']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

CORS(app)
db = SQLAlchemy(app)

#API endpoint to fetch a random quote
@app.route('/api/quote')
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Could not fetch quote"}), 500

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/tasks')
def tasks():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('tasks.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered')
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = email
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/task_list', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([
        {
            "id": task.id,
            "name": task.name,
            "category": task.category,
            "priority": task.priority,
            "due_date": task.due_date.strftime('%Y-%m-%d'),
            "completed": task.completed
        }
        for task in tasks
    ])

@app.route('/task_list', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    if data['category'] not in ALLOWED_CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400
    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    new_task = Task(
        name=data['name'],
        category=data['category'],
        priority=data['priority'],
        due_date=due_date,
        completed=data.get('completed', False),
        user_id=session['user_id']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added successfully!"}), 201

@app.route('/task_list/<int:id>', methods=['GET'])
def get_task(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    task = Task.query.filter_by(id=id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({
        "id": task.id,
        "name": task.name,
        "category": task.category,
        "priority": task.priority,
        "due_date": task.due_date.strftime('%Y-%m-%d'),
        "completed": task.completed
    })

@app.route('/task_list/<int:id>', methods=['DELETE'])
def delete_task(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    task = Task.query.filter_by(id=id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'})

@app.route('/task_list/<int:id>', methods=['PUT'])
def update_task(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    task = Task.query.filter_by(id=id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    data = request.json
    task.name = data.get('name', task.name)
    if 'category' in data and data['category'] in ALLOWED_CATEGORIES:
        task.category = data['category']
    task.priority = data.get('priority', task.priority)
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'})

if __name__ == '__main__':
    app.run(debug=True)