// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    cargarEstadisticas();
    inicializarGraficos();
});

function cargarEstadisticas() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            actualizarCards(data);
            actualizarGraficos(data);
        })
        .catch(error => console.error('Error:', error));
}

function actualizarCards(data) {
    document.getElementById('totalVentas').textContent = `$${data.total_ventas.toFixed(2)}`;
    document.getElementById('totalCotizaciones').textContent = data.total_cotizaciones;
    document.getElementById('totalFacturas').textContent = data.total_facturas;
    document.getElementById('cotizacionesAprobadas').textContent = data.cotizaciones_aprobadas;
    document.getElementById('cotizacionesRechazadas').textContent = data.cotizaciones_rechazadas;
    document.getElementById('facturasPendientes').textContent = data.facturas_pendientes;
}

function inicializarGraficos() {
    const ctx = document.getElementById('graficoIngresos').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Ingresos Mensuales',
                data: [],
                borderColor: '#3B82F6',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `$${value}`
                    }
                }
            }
        }
    });
}