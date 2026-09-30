/**
 * AI Predictive Maintenance - Dashboard Charts (Chart.js Light Theme)
 */

document.addEventListener('DOMContentLoaded', () => {
  initFailureDistributionChart();
  initConditionClustersChart();
});

function initFailureDistributionChart() {
  const ctx = document.getElementById('failureDistributionChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Normal Machines (96.61%)', 'Machine Failures (3.39%)'],
      datasets: [{
        data: [9661, 339],
        backgroundColor: ['#10B981', '#EF4444'],
        hoverBackgroundColor: ['#059669', '#DC2626'],
        borderColor: '#FFFFFF',
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 600 },
            color: '#475569',
            padding: 16,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        },
        tooltip: {
          backgroundColor: '#0F172A',
          titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 13, weight: 700 },
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
          padding: 12,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const val = context.raw || 0;
              return ` ${val.toLocaleString()} units`;
            }
          }
        }
      }
    }
  });
}

function initConditionClustersChart() {
  const ctx = document.getElementById('conditionClustersChart');
  if (!ctx) return;

  // Realistic synthetic sample scatter points representing K-Means clustering on AI4I (Torque vs Tool Wear)
  const cluster0 = [
    {x: 32, y: 15}, {x: 38, y: 35}, {x: 42, y: 50}, {x: 35, y: 65}, {x: 45, y: 25},
    {x: 28, y: 40}, {x: 39, y: 75}, {x: 44, y: 60}, {x: 36, y: 85}, {x: 48, y: 45},
    {x: 33, y: 70}, {x: 41, y: 30}, {x: 37, y: 55}, {x: 46, y: 80}, {x: 30, y: 60}
  ];

  const cluster1 = [
    {x: 45, y: 110}, {x: 52, y: 135}, {x: 48, y: 155}, {x: 56, y: 120}, {x: 50, y: 165},
    {x: 42, y: 130}, {x: 54, y: 145}, {x: 58, y: 115}, {x: 47, y: 175}, {x: 53, y: 160},
    {x: 49, y: 125}, {x: 55, y: 170}, {x: 46, y: 140}, {x: 57, y: 150}, {x: 51, y: 180}
  ];

  const cluster2 = [
    {x: 62, y: 190}, {x: 68, y: 215}, {x: 72, y: 200}, {x: 65, y: 225}, {x: 75, y: 235},
    {x: 60, y: 205}, {x: 70, y: 220}, {x: 67, y: 230}, {x: 74, y: 240}, {x: 63, y: 210},
    {x: 69, y: 245}, {x: 76, y: 215}, {x: 66, y: 195}, {x: 71, y: 235}, {x: 78, y: 250}
  ];

  new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Cluster 0: Optimal Condition',
          data: cluster0,
          backgroundColor: '#0284C7',
          borderColor: '#0284C7',
          pointRadius: 6,
          pointHoverRadius: 8
        },
        {
          label: 'Cluster 1: Medium Condition',
          data: cluster1,
          backgroundColor: '#F59E0B',
          borderColor: '#F59E0B',
          pointRadius: 6,
          pointHoverRadius: 8
        },
        {
          label: 'Cluster 2: High Load Condition',
          data: cluster2,
          backgroundColor: '#EF4444',
          borderColor: '#EF4444',
          pointRadius: 6,
          pointHoverRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Torque [Nm]',
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 700 },
            color: '#475569'
          },
          grid: {
            color: '#F1F5F9'
          },
          ticks: {
            font: { family: "'Plus Jakarta Sans', sans-serif" },
            color: '#64748B'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Tool Wear [min]',
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 700 },
            color: '#475569'
          },
          grid: {
            color: '#F1F5F9'
          },
          ticks: {
            font: { family: "'Plus Jakarta Sans', sans-serif" },
            color: '#64748B'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: 600 },
            color: '#475569',
            usePointStyle: true,
            pointStyle: 'circle'
          }
        },
        tooltip: {
          backgroundColor: '#0F172A',
          titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 700 },
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
          padding: 10,
          cornerRadius: 6,
          callbacks: {
            label: function(ctx) {
              return ` Torque: ${ctx.raw.x} Nm, Tool Wear: ${ctx.raw.y} min`;
            }
          }
        }
      }
    }
  });
}
