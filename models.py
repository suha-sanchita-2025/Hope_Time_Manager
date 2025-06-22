# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    priority = db.Column(db.String(50))
    due_date = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)