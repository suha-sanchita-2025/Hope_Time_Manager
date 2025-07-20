// Pie Chart: Tasks by Category
new Chart(document.getElementById('categoryPieChart'), {
    type: 'pie',
    data: {
        labels: categories,
        datasets: [{
            data: tasksByCategory,
            backgroundColor: ['#0008ff', '#00b318', '#8102f7']
        }]
    }
});

// Donut Chart: Completed vs Incomplete Tasks
new Chart(document.getElementById('completionDonutChart'), {
    type: 'doughnut',
    data: {
        labels: ['Completed', 'Incomplete'],
        datasets: [{
            data: [completed, incomplete],
            backgroundColor: ['#2ecc71', '#e74c3c']
        }]
    }
});

// Stacked Bar Chart: Tasks per Category (Completed/Incomplete)
new Chart(document.getElementById('categoryBarChart'), {
    type: 'bar',
    data: {
        labels: categories,
        datasets: [
            {
                label: 'Completed',
                data: barCompleted,
                backgroundColor: '#2ecc71'
            },
            {
                label: 'Incomplete',
                data: barIncomplete,
                backgroundColor: '#e74c3c'
            }
        ]
    },
    options: {
        plugins: { legend: { position: 'top' } },
        responsive: true,
        scales: {
            x: { stacked: true },
            y: { stacked: true, beginAtZero: true }
        }
    }
});