from app import create_app
from flask_socketio import SocketIO
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
socketio = SocketIO(app)

@app.cli.command("init-db")
def init_db_command():
    """Crea las tablas de la base de datos e inicializa el usuario admin."""
    with app.app_context():
        db.create_all()
        # Crear usuario admin si no existe
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado.")
        print("Base de datos inicializada.")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
