from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_socketio import SocketIO

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Registrar blueprints
        from .blueprints.auth import auth_bp
        from .blueprints.main import main_bp
        from .blueprints.cotizaciones import cotizaciones_bp
        from .blueprints.facturas import facturas_bp
        from .blueprints.config import config_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(cotizaciones_bp)
        app.register_blueprint(facturas_bp)
        app.register_blueprint(config_bp)
        
        # Crear directorios necesarios
        import os
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.static_folder, 'uploads', 'logos'), exist_ok=True)
        os.makedirs(os.path.join(app.static_folder, 'uploads', 'temp'), exist_ok=True)
        
        # Crear tablas
        db.create_all()
        @app.template_filter('format_currency')
        def format_currency(value):
            if value is None:
                return "$0.00"
            return f"${value:,.2f}"

        @app.template_filter('abs')
        def abs_filter(value):
            return abs(value)
        
        return app