// static/js/notificaciones.js
const socket = io();

socket.on('connect', () => {
    console.log('Conectado al servidor de websockets');
});

socket.on('nueva_notificacion', (data) => {
    mostrarNotificacion(data);
});

function mostrarNotificacion(data) {
    const toast = document.createElement('div');
    toast.className = `
        fixed top-4 right-4 bg-white shadow-lg rounded-lg p-4 
        transform transition-transform duration-300 ease-in-out
        ${getColorClaseNotificacion(data.tipo)}
    `;
    
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${getIconoNotificacion(data.tipo)} mr-3"></i>
            <div>
                <h4 class="font-semibold">${getTituloNotificacion(data.tipo)}</h4>
                <p class="text-sm">${data.mensaje}</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transform = 'translateX(150%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function getColorClaseNotificacion(tipo) {
    switch(tipo) {
        case 'exito': return 'bg-green-100 text-green-800';
        case 'error': return 'bg-red-100 text-red-800';
        case 'advertencia': return 'bg-yellow-100 text-yellow-800';
        default: return 'bg-blue-100 text-blue-800';
    }
}

function getIconoNotificacion(tipo) {
    switch(tipo) {
        case 'exito': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'advertencia': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

function getTituloNotificacion(tipo) {
    switch(tipo) {
        case 'exito': return '¡Éxito!';
        case 'error': return 'Error';
        case 'advertencia': return 'Advertencia';
        default: return 'Información';
    }
}