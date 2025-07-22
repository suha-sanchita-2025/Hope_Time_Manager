# TaskFusion

A web-based task manager with user authentication, task categorization, calendar view, and productivity statistics.

## Tech Stack

- Python (Flask)  
- SQLAlchemy (SQLite)  
- JavaScript  
- HTML/CSS

## Prerequisites

- Python 3.8 or higher installed on your system.

## Setup

1. Clone the repository.  
2. Install dependencies:  
pip install -r requirements.txt
3. Run the app:  
python app.py
4. Open your browser and go to:  
http://localhost:5000


## API Endpoints

- `/api/quote`  
- `/task_list`  
- `/task_list/<int:id>`  
- `/api/user_tasks`  
- `/task_list/complete_all`  
- `/task_list/delete_completed`  
- `/account`

## Database Schema

**User:**  
- id  
- username  
- email  
- password  
- avatar_url

**Task:**  
- id  
- name  
- category  
- priority  
- due_date  
- completed  
- user_id  
- notes

## Features

1. User registration with email and username  
2. Secure user login and logout  
3. Password hashing for account security  
4. Add new tasks with name, category, priority, and due date  
5. Edit existing tasks’ details  
6. Delete tasks individually  
7. Mark tasks as completed or pending  
8. Task categorization (school, work, personal)  
9. Priority levels (low, medium, high) for tasks  
10. Search and filter tasks by name, category, or priority  
11. View tasks in a calendar layout  
12. Productivity statistics with charts showing task progress  
13. Bulk mark all tasks as completed  
14. Bulk delete all completed tasks  
15. Upload and update user profile avatar  

