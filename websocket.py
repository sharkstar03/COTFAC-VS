def socket_init(socketio):
    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')

    @socketio.on('nueva_cotizacion')
    def handle_nueva_cotizacion(data):
        socketio.emit('actualizar_dashboard')