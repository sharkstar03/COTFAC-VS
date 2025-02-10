from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Cotizacion, Factura, Item
from datetime import datetime, timedelta
from sqlalchemy import func

def register_routes(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.cli.command("init-db")
    def init_db_command():
        """Inicializa la base de datos."""
        db.create_all()
        # Crear usuario admin por defecto si no existe
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
        print("Base de datos inicializada.")

    @app.route('/')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Usuario o contraseña incorrectos', 'error')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/api/stats')
    @login_required
    def get_stats():
        stats = {
            'total_ventas': db.session.query(func.sum(Factura.total)).scalar() or 0,
            'total_cotizaciones': Cotizacion.query.count(),
            'total_facturas': Factura.query.count(),
            'total_clientes': db.session.query(func.count(func.distinct(Cotizacion.nombre))).scalar(),
            'cotizaciones_aprobadas': Cotizacion.query.filter_by(estado='aprobada').count(),
            'cotizaciones_rechazadas': Cotizacion.query.filter_by(estado='rechazada').count(),
            'facturas_pendientes': Factura.query.filter_by(estado='pendiente').count()
        }
        return jsonify(stats)

    @app.route('/select_type')
    @login_required
    def select_type():
        return render_template('select_type.html')

    @app.route('/formulario_empresa')
    @login_required
    def formulario_empresa():
        return render_template('formulario_empresa.html')

    @app.route('/formulario_natural')
    @login_required
    def formulario_natural():
        return render_template('formulario_natural.html')

    @app.route('/generate_pdf_empresa', methods=['POST'])
    @login_required
    def generate_pdf_empresa():
        # Lógica para generar PDF de cotización empresarial
        # ...existing code...
        return redirect(url_for('dashboard'))

    @app.route('/generate_pdf_natural', methods=['POST'])
    @login_required
    def generate_pdf_natural():
        # Lógica para generar PDF de cotización personal
        # ...existing code...
        return redirect(url_for('dashboard'))

    @app.route('/buscar')
    @login_required
    def buscar():
        return render_template('buscar.html')

    @app.route('/buscar_ajax')
    @login_required
    def buscar_ajax():
        query = request.args.get('query', '')
        tipo = request.args.get('tipo', 'todos')
        
        cotizaciones = Cotizacion.query
        
        if tipo != 'todos':
            cotizaciones = cotizaciones.filter_by(tipo=tipo)
        
        if query:
            cotizaciones = cotizaciones.filter(
                db.or_(
                    Cotizacion.numero.like(f'%{query}%'),
                    Cotizacion.nombre.like(f'%{query}%'),
                    Cotizacion.empresa.like(f'%{query}%')
                )
            )
        
        cotizaciones = cotizaciones.order_by(Cotizacion.fecha.desc()).all()
        
        return jsonify([{
            'numero': c.numero,
            'fecha': c.fecha.strftime('%d/%m/%Y'),
            'nombre': c.nombre,
            'tipo': c.tipo,
            'total': f"${c.total:.2f}",
            'estado': c.estado
        } for c in cotizaciones])

    @app.route('/facturas')
    @login_required
    def facturas():
        facturas = Factura.query.order_by(Factura.fecha.desc()).all()
        return render_template('facturas.html', facturas=facturas)

    @app.route('/ver_factura/<numero>')
    @login_required
    def ver_factura(numero):
        factura = Factura.query.filter_by(numero=numero).first_or_404()
        return render_template('ver_factura.html', factura=factura)

    @app.route('/marcar_pagada/<numero>', methods=['POST'])
    @login_required
    def marcar_pagada(numero):
        factura = Factura.query.filter_by(numero=numero).first_or_404()
        factura.estado = 'pagada'
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/aprobar_cotizacion/<numero>', methods=['POST'])
    @login_required
    def aprobar_cotizacion(numero):
        cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
        
        if cotizacion.estado != 'pendiente':
            return jsonify({'error': 'Esta cotización no está pendiente'}), 400
        
        # Crear factura
        nueva_factura = Factura(
            numero=f"FAC{cotizacion.numero[3:]}",
            cotizacion_id=cotizacion.id,
            total=cotizacion.total
        )
        
        cotizacion.estado = 'aprobada'
        db.session.add(nueva_factura)
        db.session.commit()
        
        return jsonify({'success': True})

    @app.route('/rechazar_cotizacion/<numero>', methods=['POST'])
    @login_required
    def rechazar_cotizacion(numero):
        cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
        cotizacion.estado = 'rechazada'
        cotizacion.fecha_rechazo = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('buscar'))
    
    @app.route('/configuracion')
    @login_required  # Add login_required decorator if you have authentication
    def configuracion():
    # Add any necessary logic for the configuration page
        return render_template('configuracion.html')

    return app