
import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from collections import defaultdict
from calendar import monthrange

ALLOWED_CATEGORIES = ['school', 'work', 'personal']
ALLOWED_PRIORITIES = ['low', 'medium', 'high']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'


# Set UPLOAD_FOLDER as an absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

CORS(app)
db = SQLAlchemy(app)

# API endpoint to fetch a random quote
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
    avatar_url = db.Column(db.String(200))  # Add this field
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
    notes = db.Column(db.Text)

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

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/task_list', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    priority = request.args.get('priority', '').strip()
    query = Task.query.filter_by(user_id=session['user_id'])
    if search:
        query = query.filter(Task.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)
    tasks = query.all()
    return jsonify([
        {
            "id": task.id,
            "name": task.name,
            "category": task.category,
            "priority": task.priority,
            "due_date": task.due_date.strftime('%Y-%m-%d'),
            "completed": task.completed,
            "notes": task.notes
        }
        for task in tasks
    ])

@app.route('/task_list', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    today = datetime.today().date()
    if due_date < today:
        return jsonify({'error': 'Due date cannot be in the past'}), 400
    if data['category'] not in ALLOWED_CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400
    if data['priority'] not in ALLOWED_PRIORITIES:
        return jsonify({'error': 'Invalid priority'}), 400
    new_task = Task(
        name=data['name'],
        category=data['category'],
        priority=data['priority'],
        due_date=due_date,
        completed=data.get('completed', False),
        user_id=session['user_id'],
        notes=data.get('notes', '')
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
        "completed": task.completed,
        "notes": task.notes  # Added
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
    if 'priority' in data:
        if data['priority'] not in ALLOWED_PRIORITIES:
            return jsonify({'error': 'Invalid priority'}), 400
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    task.completed = data.get('completed', task.completed)
    task.notes = data.get('notes', task.notes)  # Added
    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'})

@app.route('/calendar')
def calendar():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('calendar.html')

@app.route('/api/user_tasks', methods=['GET'])
def user_tasks():
    if 'user_id' not in session:
        return jsonify([])  # or return jsonify({'error': 'Unauthorized'}), 401
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([
        {
            'id': t.id,
            'name': t.name,
            'category': t.category,
            'priority': t.priority,
            'due_date': t.due_date.strftime('%Y-%m-%d'),
            'completed': t.completed,
            'notes': t.notes  # Added
        } for t in tasks
    ])

# Mark all tasks as completed
@app.route('/task_list/complete_all', methods=['POST'])
def complete_all_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    Task.query.filter_by(user_id=session['user_id'], completed=False).update({'completed': True})
    db.session.commit()
    return jsonify({'message': 'All tasks marked as completed!'})

# Delete all completed tasks
@app.route('/task_list/delete_completed', methods=['DELETE'])
def delete_completed_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    Task.query.filter_by(user_id=session['user_id'], completed=True).delete()
    db.session.commit()
    return jsonify({'message': 'All completed tasks deleted!'})

@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))
    if not user.avatar_url:
        user.avatar_url = url_for('static', filename='default-avatar.png')
    return render_template('account.html', user=user)
# Account management routes

@app.route('/account/update', methods=['POST'])
def update_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    username = request.form['username']
    email = request.form['email']
    file = request.files.get('avatar')

    if email != user.email and User.query.filter_by(email=email).first():
        flash('Email already registered', 'error')
        return redirect(url_for('account'))
    user.username = username
    user.email = email

    if file and file.filename != '':
        if allowed_file(file.filename):
            filename = secure_filename(f"{user.id}_{file.filename}")
            # Save to disk using os.path.join (handles Windows paths)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Set URL using forward slashes for Flask static serving
            user.avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')
        else:
            flash('Invalid file type. Please upload an image.', 'error')
            return redirect(url_for('account'))

    db.session.commit()
    flash('Profile updated!', 'success')
    return redirect(url_for('account'))


@app.route('/account/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('account'))
    user.password = generate_password_hash(new_password)
    db.session.commit()
    flash('Password changed!', 'success')
    return redirect(url_for('account'))

@app.route('/account/delete', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Account deleted.', 'success')
    return redirect(url_for('signup'))

@app.route('/statistics')
def statistics():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch tasks for the current user
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    categories = ['School', 'Work', 'Personal']
    tasks_by_category = [0, 0, 0]
    bar_completed = [0, 0, 0]
    bar_incomplete = [0, 0, 0]
    completed = 0
    incomplete = 0

    # Count tasks by category and completion
    for task in tasks:
        if task.category.capitalize() in categories:
            idx = categories.index(task.category.capitalize())
            tasks_by_category[idx] += 1
            if task.completed:
                bar_completed[idx] += 1
                completed += 1
            else:
                bar_incomplete[idx] += 1
                incomplete += 1

    # Productivity: tasks completed per day for the last 7 days
    today = datetime.today().date()
    productivity = []
    productivity_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = sum(1 for t in tasks if t.completed and t.due_date == day)
        productivity.append(count)
        productivity_labels.append(day.strftime('%a'))  # e.g., 'Mon', 'Tue', etc.

    return render_template(
        'statistics.html',
        categories=categories,
        tasks_by_category=tasks_by_category,
        completed=completed,
        incomplete=incomplete,
        bar_completed=bar_completed,
        bar_incomplete=bar_incomplete
    )



if __name__ == '__main__':
    app.run(debug=True)