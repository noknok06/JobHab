const ctx = document.getElementById('statusChart').getContext('2d');

const statusCounts = {
    10: parseInt(document.getElementById("status-count-10").textContent),
    20: parseInt(document.getElementById("status-count-20").textContent),
    30: parseInt(document.getElementById("status-count-30").textContent),
    40: parseInt(document.getElementById("status-count-40").textContent),
};

const totalTicketsWithoutCompleted = Object.values(statusCounts).reduce((a, b) => a + b, 0);

const percentages = {
    10: (statusCounts[10] / totalTicketsWithoutCompleted * 100).toFixed(2),
    20: (statusCounts[20] / totalTicketsWithoutCompleted * 100).toFixed(2),
    30: (statusCounts[30] / totalTicketsWithoutCompleted * 100).toFixed(2),
    40: (statusCounts[40] / totalTicketsWithoutCompleted * 100).toFixed(2),
};

const data = {
    labels: ['未処理', '保留', '社内確認中', 'ベンダー処理中'],
    datasets: [{
        label: 'チケット状況',
        data: [percentages[10], percentages[20], percentages[30], percentages[40]],
        backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)'
        ],
        borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
    }]
};

const config = {
    type: 'bar',
    data: data,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return context.label + ': ' + context.raw + '%';
                    }
                }
            }
        }
    }
};

new Chart(ctx, config);

statusChart.options.onClick = function (event, elements) {
    if (elements.length > 0) {
        const chartIndex = elements[0].index; // クリックされたセグメントのインデックス
        const statusLabels = statusChart.data.labels; // ラベルリスト
        const selectedStatus = statusLabels[chartIndex]; // 選択されたステータス

        // フィルタリングを実行
        applyFilters(selectedStatus);
    }
};

function applyFilters(status) {
    // カレンダーの更新
    const calendar = FullCalendar.getCalendar(document.getElementById('calendar'));
    if (calendar) {
        calendar.refetchEvents(); // イベントデータをリロード
    }

    // Upcoming Deadlines の更新
    fetch(`/api/upcoming_deadlines/?status=${status}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch filtered deadlines.');
            }
            return response.json();
        })
        .then(data => {
            const deadlineContainer = document.querySelector('.upcoming-deadlines');
            if (deadlineContainer) {
                deadlineContainer.innerHTML = '';

                if (data.length === 0) {
                    deadlineContainer.innerHTML = `
                        <div class="alert alert-info" role="alert">
                            No upcoming deadlines for the selected status.
                        </div>`;
                } else {
                    data.forEach(ticket => {
                        const deadlineCard = `
                            <div class="col-md-3 mb-2">
                                <div class="card shadow-sm border-info">
                                    <div class="card-body">
                                        <h5 class="card-title text-info">${ticket.title}</h5>
                                        <p class="card-text">D期限: ${ticket.end_date}</p>
                                        <a href="${ticket.detail_url}" class="btn btn-outline-info btn-sm mt-2">View Details</a>
                                    </div>
                                </div>
                            </div>`;
                        deadlineContainer.innerHTML += deadlineCard;
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error fetching deadlines:', error);
        });
}
