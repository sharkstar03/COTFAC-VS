from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models import db, Cotizacion, Factura
from ..utils.helpers import format_currency

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', stats=get_dashboard_stats())

@main_bp.route('/api/stats')
@login_required
def get_stats():
    return jsonify(get_dashboard_stats())

def get_dashboard_stats():
    # Fecha inicial (30 días atrás)
    fecha_inicio = datetime.now() - timedelta(days=30)
    
    # Estadísticas básicas
    stats = {
        'total_ventas': db.session.query(func.sum(Factura.total))\
            .filter(Factura.fecha >= fecha_inicio).scalar() or 0,
        'total_cotizaciones': Cotizacion.query\
            .filter(Cotizacion.fecha >= fecha_inicio).count(),
        'total_facturas': Factura.query\
            .filter(Factura.fecha >= fecha_inicio).count(),
        'total_clientes': db.session.query(func.count(func.distinct(Cotizacion.nombre)))\
            .filter(Cotizacion.fecha >= fecha_inicio).scalar() or 0,
        'cotizaciones_aprobadas': Cotizacion.query\
            .filter(Cotizacion.estado == 'aprobada')\
            .filter(Cotizacion.fecha >= fecha_inicio).count(),
        'cotizaciones_rechazadas': Cotizacion.query\
            .filter(Cotizacion.estado == 'rechazada')\
            .filter(Cotizacion.fecha >= fecha_inicio).count(),
        'facturas_pendientes': Factura.query\
            .filter(Factura.estado == 'pendiente').count()
    }
    
    # Formato de moneda para el total de ventas
    stats['total_ventas_formato'] = format_currency(stats['total_ventas'])
    
    # Datos para el gráfico de ingresos mensuales
    ingresos_mensuales = db.session.query(
        func.date_trunc('month', Factura.fecha).label('mes'),
        func.sum(Factura.total).label('total')
    ).group_by('mes')\
     .order_by('mes')\
     .limit(12)\
     .all()
    
    stats['grafico_ingresos'] = [{
        'mes': mes.strftime('%B %Y'),
        'total': float(total)
    } for mes, total in ingresos_mensuales]
    
    return stats