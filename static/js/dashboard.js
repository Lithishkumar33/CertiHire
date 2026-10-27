document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("revenueChart");

    if (!canvas) {
        return;
    }

    const labelsElement =
        document.getElementById("chart-labels");

    const dataElement =
        document.getElementById("chart-data");

    const labels = labelsElement
        ? JSON.parse(labelsElement.textContent)
        : [];

    const revenue = dataElement
        ? JSON.parse(dataElement.textContent)
        : [];

    const totalRevenue = revenue.length
        ? Math.max(...revenue)
        : 0;


    // Create gradient
    const ctx = canvas.getContext("2d");

    const gradient = ctx.createLinearGradient(
        0,
        0,
        0,
        350
    );

    gradient.addColorStop(
        0,
        "rgba(37, 99, 235, 0.30)"
    );

    gradient.addColorStop(
        1,
        "rgba(37, 99, 235, 0.02)"
    );


    new Chart(canvas, {

        type: "line",

        data: {

            labels: labels,

            datasets: [{

                data: revenue,

                borderColor: "#2563EB",

                backgroundColor: gradient,

                borderWidth: 4,

                fill: true,

                tension: 0.45,

                pointRadius: 8,

                pointHoverRadius: 11,

                pointBackgroundColor: "#2563EB",

                pointBorderColor: "#ffffff",

                pointBorderWidth: 4

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            interaction: {
                intersect: false,
                mode: "index"
            },

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {

                    backgroundColor: "#111827",

                    titleColor: "#ffffff",

                    bodyColor: "#ffffff",

                    padding: 14,

                    cornerRadius: 10,

                    displayColors: false,

                    callbacks: {

                        label: function (context) {

                            return "₹" +
                                Number(context.parsed.y)
                                .toLocaleString("en-IN");

                        }

                    }

                }

            },

            scales: {

                x: {

                    grid: {
                        display: false
                    },

                    border: {
                        display: false
                    },

                    ticks: {

                        color: "#64748B",

                        font: {
                            size: 13,
                            weight: "500"
                        }

                    }

                },

                y: {

                    beginAtZero: true,

                    suggestedMax:
                        totalRevenue > 0
                            ? totalRevenue * 1.25
                            : 500,

                    grid: {

                        color:
                            "rgba(148, 163, 184, 0.15)"

                    },

                    border: {
                        display: false
                    },

                    ticks: {

                        color: "#64748B",

                        padding: 10,

                        callback: function (value) {

                            return "₹" +
                                Number(value)
                                .toLocaleString("en-IN");

                        }

                    }

                }

            }

        }

    });

});