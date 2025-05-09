fetch('/api/calorie_data')
.then(res => res.json())
.then(data => {
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Calories',
                data: data.calories,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        }
    });
});
