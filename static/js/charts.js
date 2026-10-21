/**
 * GRAMA SEVA – Chart.js Integration
 * Renders interactive administrative charts with real database metrics
 */

document.addEventListener('DOMContentLoaded', function () {
  initAdminDashboardCharts();
});

function initAdminDashboardCharts() {
  // Check if Chart.js is loaded
  if (typeof Chart === 'undefined') return;

  // Set Chart.js global defaults
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.color = "#64748b";
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;

  // 1. Complaints by Category Chart (Doughnut)
  const categoryCanvas = document.getElementById('chartCategory');
  if (categoryCanvas) {
    const rawData = categoryCanvas.getAttribute('data-chart') || '[]';
    let catData = [];
    try { catData = JSON.parse(rawData); } catch (e) { catData = []; }

    const labels = catData.map(c => c.name_en);
    const counts = catData.map(c => c.count);
    const colors = catData.map(c => c.color || '#166534');

    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { boxWidth: 12, font: { size: 11 } }
          }
        },
        cutout: '65%'
      }
    });
  }

  // 2. Monthly Trend Chart (Bar & Line Combo)
  const monthlyCanvas = document.getElementById('chartMonthly');
  if (monthlyCanvas) {
    const rawData = monthlyCanvas.getAttribute('data-chart') || '[]';
    let monthData = [];
    try { monthData = JSON.parse(rawData); } catch (e) { monthData = []; }

    const months = monthData.map(m => m.month || 'Current');
    const totals = monthData.map(m => m.total || 0);
    const resolved = monthData.map(m => m.resolved || 0);

    new Chart(monthlyCanvas, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          {
            label: 'Total Registered',
            data: totals,
            backgroundColor: '#166534',
            borderRadius: 6,
            barPercentage: 0.6
          },
          {
            label: 'Resolved',
            data: resolved,
            backgroundColor: '#16a34a',
            borderRadius: 6,
            barPercentage: 0.6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12 } }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  // 3. Ward-wise Statistics Chart (Horizontal Bar)
  const wardCanvas = document.getElementById('chartWard');
  if (wardCanvas) {
    const rawData = wardCanvas.getAttribute('data-chart') || '[]';
    let wardData = [];
    try { wardData = JSON.parse(rawData); } catch (e) { wardData = []; }

    const wards = wardData.map(w => w.ward_no);
    const counts = wardData.map(w => w.count);

    new Chart(wardCanvas, {
      type: 'bar',
      data: {
        labels: wards,
        datasets: [{
          label: 'Complaints',
          data: counts,
          backgroundColor: '#f59e0b',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false }
          }
        }
      }
    });
  }

  // 4. Resolution Status Distribution (Pie)
  const statusCanvas = document.getElementById('chartStatus');
  if (statusCanvas) {
    const rawData = statusCanvas.getAttribute('data-chart') || '[]';
    let statusData = [];
    try { statusData = JSON.parse(rawData); } catch (e) { statusData = []; }

    const statusColors = {
      'Submitted': '#2563eb',
      'Under Review': '#f59e0b',
      'Assigned': '#4f46e5',
      'In Progress': '#9333ea',
      'Resolved': '#16a34a',
      'Rejected': '#dc2626'
    };

    const labels = statusData.map(s => s.status);
    const counts = statusData.map(s => s.count);
    const bgColors = labels.map(l => statusColors[l] || '#64748b');

    new Chart(statusCanvas, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });
  }
}
