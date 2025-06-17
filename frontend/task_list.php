<!DOCTYPE html>
<html>
<head>
    <title>Task List</title>
</head>
<body>

<!-- Navigation bar -->
<nav>
    <a href="{{ url_for('home') }}">Home</a>
    <a href="{{ url_for('task_list') }}">Tasks</a>
    <a href="#">Calendar</a>
    <a href="#">Statistics</a>
    <a href="{{ url_for('logout') }}">Logout</a>
</nav>

<!-- Search form: sends GET to /task_list -->
<form method="GET" action="{{ url_for('task_list') }}">
    <input type="text" name="search" placeholder="Search Tasks" value="{{ request.args.get('search', '') }}">
    <button type="submit">Search</button>
</form>

<!-- Task results -->
{% for task in tasks %}
<div style="border: 1px solid black; padding: 10px; margin: 10px;">
    <h3>{{ task.name }}</h3>
</div>
{% else %}
<p>No tasks found.</p>
{% endfor %}

</body>
</html>

<?php
// Include database connection file
include 'db_conn.php';

// Get the 'search' parameter from the URL if it exists, or default to an empty string
$search = isset($_GET['search']) ? $_GET['search'] : '';

// SQL query to select tasks that match the search term using LIKE for partial matching
$query = "SELECT * FROM tasks WHERE name LIKE ?";

// Prepare the SQL statement
$stmt = $pdo->prepare($query);

// Add wildcard characters for partial match search
$likeSearch = "%$search%";

// Bind the search parameter to the prepared statement
$stmt->bind_param("s", $likeSearch);

// Execute the query
$stmt->execute();

// Get the results from the executed statement
$result = $stmt->get_result();

// Loop through each row and display the task details
while ($row = $result->fetch_assoc()) {
    echo "<div style='border: 1px solid black; padding: 10px; margin: 10px;'>";
    echo "<h3>{$row['name']}</h3>";
    echo "Category: {$row['category']}<br>";
    echo "Priority: {$row['priority']}<br>";
    echo "Due Date: {$row['due_date']}<br>";
    echo "Completed: {$row['completed']}<br>";
    echo "</div>";
}
?>
