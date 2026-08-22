// Chart.js helper managers for Home bar chart and Category donut chart

let homeBarChart = null;
let categoryDonutChart = null;

function renderHomeHorizontalBar(income, expense) {
  const ctx = document.getElementById('homeBarChart');
  if (!ctx) return;

  if (homeBarChart) {
    homeBarChart.destroy();
  }

  homeBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Receitas', 'Despesas'],
      datasets: [{
        data: [income, expense],
        backgroundColor: [
          'rgba(16, 185, 129, 0.85)',
          'rgba(239, 68, 68, 0.85)'
        ],
        borderColor: [
          '#10b981',
          '#ef4444'
        ],
        borderWidth: 1,
        borderRadius: 8,
        barThickness: 22
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ' ' + context.parsed.x.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#94a3b8',
            callback: function(value) {
              return 'R$ ' + value;
            }
          }
        },
        y: {
          grid: { display: false },
          ticks: {
            color: '#f8fafc',
            font: { weight: '600', size: 13 }
          }
        }
      }
    }
  });
}

function renderCategoryDonut(categoriesWithExpense) {
  const ctx = document.getElementById('categoryDonutChart');
  if (!ctx) return;

  if (categoryDonutChart) {
    categoryDonutChart.destroy();
  }

  // Filter only categories with expense > 0
  const activeCategories = categoriesWithExpense.filter(c => c.total_expense > 0);

  if (activeCategories.length === 0) {
    // Render placeholder donut
    categoryDonutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Sem despesas no período'],
        datasets: [{
          data: [1],
          backgroundColor: ['rgba(255, 255, 255, 0.08)'],
          borderColor: ['rgba(255, 255, 255, 0.1)'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        }
      }
    });
    return;
  }

  const labels = activeCategories.map(c => c.name);
  const data = activeCategories.map(c => c.total_expense);
  const colors = activeCategories.map(c => c.color || '#6366f1');

  categoryDonutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: '#0b0f19',
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#94a3b8',
            boxWidth: 12,
            padding: 14,
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.parsed;
              return ` ${context.label}: ${val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`;
            }
          }
        }
      }
    }
  });
}
