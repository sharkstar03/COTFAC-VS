class NotificationManager {
    constructor() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'fixed bottom-4 right-4 space-y-2';
        document.body.appendChild(this.container);
    }

    show(message, type = 'success', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} notification-enter`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${this.getIcon(type)} mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        this.container.appendChild(notification);

        // Activar animación de entrada
        setTimeout(() => {
            notification.classList.remove('notification-enter');
            notification.classList.add('notification-enter-active');
        }, 10);

        // Remover después del tiempo especificado
        setTimeout(() => {
            notification.classList.remove('notification-enter-active');
            notification.classList.add('notification-exit');
            setTimeout(() => {
                notification.classList.add('notification-exit-active');
                setTimeout(() => {
                    this.container.removeChild(notification);
                }, 500);
            }, 10);
        }, duration);
    }

    getIcon(type) {
        switch(type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
}

window.notifications = new NotificationManager();