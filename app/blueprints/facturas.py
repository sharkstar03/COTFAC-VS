from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import login_required
from sqlalchemy import or_
import json
from datetime import datetime
from ..models import db, Factura, Cotizacion
from ..utils.pdf import generar_pdf_factura
from ..utils.email import enviar_factura
from ..utils.helpers import format_currency

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@facturas_bp.route('/')
@login_required
def lista():
    # Parámetros de filtrado y paginación
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', None)
    query = request.args.get('query', '')
    
    # Construir consulta base
    facturas_query = Factura.query
    
    # Aplicar filtros
    if estado:
        facturas_query = facturas_query.filter_by(estado=estado)
    
    if query:
        facturas_query = facturas_query.join(Cotizacion).filter(
            or_(
                Factura.numero.ilike(f'%{query}%'),
                Cotizacion.nombre.ilike(f'%{query}%'),
                Cotizacion.empresa.ilike(f'%{query}%')
            )
        )
    
    # Ordenar y paginar
    facturas = facturas_query.order_by(Factura.fecha.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    # Obtener estadísticas
    stats = {
        'total_facturas': Factura.query.count(),
        'facturas_pagadas': Factura.query.filter_by(estado='pagada').count(),
        'facturas_pendientes': Factura.query.filter_by(estado='pendiente').count(),
        'total_monto': format_currency(
            db.session.query(db.func.sum(Factura.total)).scalar() or 0
        )
    }
    
    return render_template('facturas/lista.html', 
                         facturas=facturas,
                         stats=stats,
                         estado_filtro=estado,
                         query=query)

@facturas_bp.route('/<numero>')
@login_required
def ver_factura(numero):
    factura = Factura.query.filter_by(numero=numero).first_or_404()
    return render_template('facturas/ver_factura.html', factura=factura)

@facturas_bp.route('/<numero>/pdf')
@login_required
def descargar_pdf(numero):
    factura = Factura.query.filter_by(numero=numero).first_or_404()
    pdf = generar_pdf_factura(factura)
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'factura_{numero}.pdf'
    )

@facturas_bp.route('/<numero>/enviar-email', methods=['POST'])
@login_required
def enviar_email(numero):
    factura = Factura.query.filter_by(numero=numero).first_or_404()
    
    try:
        pdf = generar_pdf_factura(factura)
        enviar_factura(factura, pdf)
        
        return jsonify({
            'success': True,
            'message': 'Factura enviada por email exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al enviar el email: {str(e)}'
        }), 500

@facturas_bp.route('/<numero>/marcar-pagada', methods=['POST'])
@login_required
def marcar_pagada(numero):
    factura = Factura.query.filter_by(numero=numero).first_or_404()
    
    if factura.estado == 'pagada':
        return jsonify({
            'success': False,
            'message': 'La factura ya está marcada como pagada'
        }), 400
    
    try:
        factura.estado = 'pagada'
        factura.fecha_pago = datetime.utcnow()
        factura.metodo_pago = request.form.get('metodo_pago', '')
        factura.referencia_pago = request.form.get('referencia_pago', '')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factura marcada como pagada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al marcar la factura como pagada: {str(e)}'
        }), 500

@facturas_bp.route('/<numero>/anular', methods=['POST'])
@login_required
def anular_factura(numero):
    factura = Factura.query.filter_by(numero=numero).first_or_404()
    
    if factura.estado == 'anulada':
        return jsonify({
            'success': False,
            'message': 'La factura ya está anulada'
        }), 400
    
    try:
        factura.estado = 'anulada'
        factura.cotizacion.estado = 'pendiente'  # Revertir estado de la cotización
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factura anulada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al anular la factura: {str(e)}'
        }), 500

@facturas_bp.route('/api/stats')
@login_required
def get_stats():
    try:
        # Estadísticas generales
        stats = {
            'total_facturas': Factura.query.count(),
            'facturas_pagadas': Factura.query.filter_by(estado='pagada').count(),
            'facturas_pendientes': Factura.query.filter_by(estado='pendiente').count(),
            'total_monto': format_currency(
                db.session.query(db.func.sum(Factura.total)).scalar() or 0
            )
        }
        
        # Facturas por mes (últimos 12 meses)
        facturas_por_mes = db.session.query(
            db.func.date_trunc('month', Factura.fecha).label('mes'),
            db.func.count().label('cantidad'),
            db.func.sum(Factura.total).label('total')
        ).group_by('mes')\
         .order_by('mes')\
         .limit(12)\
         .all()
        
        stats['facturas_por_mes'] = [{
            'mes': mes.strftime('%B %Y'),
            'cantidad': cantidad,
            'total': format_currency(float(total))
        } for mes, cantidad, total in facturas_por_mes]
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500