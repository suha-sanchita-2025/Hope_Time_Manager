from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from collections import defaultdict
from calendar import monthrange

app = Flask(__name__)
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
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/')
def index():
    return render_template('index.html')

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
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
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calendar')
def calendar():
    today = date.today()
    year = today.year
    month = today.month
    first_day = date(year, month, 1).weekday()
    first_day - (first_day + 1) % 7
    days_in_month = monthrange(year, month)[1]

    tasks = Task.query.all()
    tasks_by_date = defaultdict(list)
    for task in tasks:
        if tasks.due_date:
            date_str = task.due_date.strftime('%Y-%m-%d')
            tasks_by_date[date_str].append({
                'name': task.name
            })

    return render_template('calendar.html',
        year=year,
        month=month,
        month_name=today.strftime("%B"),
        days_in_month=days_in_month,
        first_day_of_month=first_day,
        tasks_by_date=tasks_by_date
                           )

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
    return redirect(url_for('login'))

@app.route('/task_list', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
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
    data = request.json
    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    new_task = Task(
        name=data['name'],
        category=data['category'],
        priority=data['priority'],
        due_date=due_date,
        completed=data.get('completed', False)
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added successfully!"}), 201

# Get a single task by ID
@app.route('/task_list/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
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

# Delete a task by ID
@app.route('/task_list/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'})

# Edit (update) a task by ID
@app.route('/task_list/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    data = request.json
    print(data)  # Debug: print incoming JSON data
    task.name = data.get('name', task.name)
    task.category = data.get('category', task.category)
    task.priority = data.get('priority', task.priority)
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'})

if __name__ == '__main__':
    app.run(debug=True)

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
    return redirect(url_for('login'))

@app.route('/task_list', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
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
    data = request.json
    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    new_task = Task(
        name=data['name'],
        category=data['category'],
        priority=data['priority'],
        due_date=due_date,
        completed=data.get('completed', False)
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added successfully!"}), 201

# Get a single task by ID
@app.route('/task_list/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
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

# Delete a task by ID
@app.route('/task_list/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'})

# Edit (update) a task by ID
@app.route('/task_list/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    data = request.json
    print(data)  # Debug: print incoming JSON data
    task.name = data.get('name', task.name)
    task.category = data.get('category', task.category)
    task.priority = data.get('priority', task.priority)
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'})

if __name__ == '__main__':
    app.run(debug=True)