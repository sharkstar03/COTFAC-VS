from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import pandas as pd
import io
from ..models import db, Cotizacion, Factura, Item
from ..utils.helpers import format_currency

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
def index():
    return render_template('reportes/index.html')

@reportes_bp.route('/ventas')
@login_required
def ventas():
    periodo = request.args.get('periodo', 'mensual')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')
        
    query = db.session.query(
        func.date_trunc(periodo, Factura.fecha).label('periodo'),
        func.count(Factura.id).label('cantidad'),
        func.sum(Factura.total).label('total')
    ).filter(
        Factura.fecha.between(fecha_inicio, fecha_fin)
    ).group_by('periodo').order_by('periodo')
    
    resultados = query.all()
    
    datos = [{
        'periodo': r.periodo.strftime('%Y-%m-%d'),
        'cantidad': r.cantidad,
        'total': format_currency(r.total)
    } for r in resultados]
    
    return render_template('reportes/ventas.html', 
                         datos=datos,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         periodo=periodo)

@reportes_bp.route('/clientes')
@login_required
def clientes():
    top_clientes = db.session.query(
        Cotizacion.nombre,
        Cotizacion.empresa,
        func.count(Factura.id).label('total_facturas'),
        func.sum(Factura.total).label('total_ventas')
    ).join(Factura).group_by(
        Cotizacion.nombre,
        Cotizacion.empresa
    ).order_by(
        func.sum(Factura.total).desc()
    ).limit(10).all()
    
    return render_template('reportes/clientes.html', clientes=top_clientes)

@reportes_bp.route('/productos')
@login_required
def productos():
    top_productos = db.session.query(
        Item.descripcion,
        func.count(Item.id).label('cantidad_vendida'),
        func.sum(Item.total).label('total_ventas')
    ).join(Cotizacion).join(Factura).group_by(
        Item.descripcion
    ).order_by(
        func.sum(Item.total).desc()
    ).limit(10).all()
    
    return render_template('reportes/productos.html', productos=top_productos)

@reportes_bp.route('/exportar/<tipo>')
@login_required
def exportar(tipo):
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if tipo == 'ventas':
        data = get_ventas_data(fecha_inicio, fecha_fin)
        filename = 'reporte_ventas.xlsx'
    elif tipo == 'clientes':
        data = get_clientes_data()
        filename = 'reporte_clientes.xlsx'
    elif tipo == 'productos':
        data = get_productos_data()
        filename = 'reporte_productos.xlsx'
    else:
        return jsonify({'error': 'Tipo de reporte no válido'}), 400
    
    # Crear Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Reporte', index=False)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

def get_ventas_data(fecha_inicio, fecha_fin):
    query = db.session.query(
        Factura.numero,
        Factura.fecha,
        Cotizacion.nombre,
        Cotizacion.empresa,
        Factura.total,
        Factura.estado
    ).join(Cotizacion).filter(
        Factura.fecha.between(fecha_inicio, fecha_fin)
    ).all()
    
    return pd.DataFrame([{
        'Número': r.numero,
        'Fecha': r.fecha,
        'Cliente': r.nombre,
        'Empresa': r.empresa,
        'Total': r.total,
        'Estado': r.estado
    } for r in query])

def get_clientes_data():
    query = db.session.query(
        Cotizacion.nombre,
        Cotizacion.empresa,
        func.count(Factura.id).label('total_facturas'),
        func.sum(Factura.total).label('total_ventas')
    ).join(Factura).group_by(
        Cotizacion.nombre,
        Cotizacion.empresa
    ).all()
    
    return pd.DataFrame([{
        'Cliente': r.nombre,
        'Empresa': r.empresa,
        'Total Facturas': r.total_facturas,
        'Total Ventas': r.total_ventas
    } for r in query])

def get_productos_data():
    query = db.session.query(
        Item.descripcion,
        func.count(Item.id).label('cantidad_vendida'),
        func.avg(Item.precio_unitario).label('precio_promedio'),
        func.sum(Item.total).label('total_ventas')
    ).join(Cotizacion).join(Factura).group_by(
        Item.descripcion
    ).all()
    
    return pd.DataFrame([{
        'Producto': r.descripcion,
        'Cantidad Vendida': r.cantidad_vendida,
        'Precio Promedio': r.precio_promedio,
        'Total Ventas': r.total_ventas
    } for r in query])