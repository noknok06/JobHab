document.addEventListener("DOMContentLoaded", function () {
    const graphData = JSON.parse(document.getElementById("weekly-post-chart-data").textContent);
    const ctx = document.getElementById("weeklyPostChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: graphData.weeks,
            datasets: [{
                label: "Post 作成数 (週単位)",
                data: graphData.counts,
                borderColor: "rgba(75, 192, 192, 1)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "週"
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "作成数"
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: "top"
                }
            }
        }
    });
});
