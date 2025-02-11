from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import login_required
from sqlalchemy import or_
import json
from datetime import datetime
from ..models import db, Cotizacion, Item, Factura
from ..forms import CotizacionEmpresaForm, CotizacionNaturalForm
from ..utils.pdf import generar_pdf_cotizacion
from ..utils.email import enviar_cotizacion
from ..utils.helpers import generar_numero_cotizacion, calcular_totales

cotizaciones_bp = Blueprint('cotizaciones', __name__, url_prefix='/cotizaciones')

@cotizaciones_bp.route('/select_type')
@login_required
def select_type():
    return render_template('cotizaciones/select_type.html')

@cotizaciones_bp.route('/empresa/nueva', methods=['GET', 'POST'])
@login_required
def nueva_empresa():
    form = CotizacionEmpresaForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Crear cotización
                cotizacion = Cotizacion(
                    numero=generar_numero_cotizacion(),
                    tipo='empresa',
                    nombre=form.nombre.data,
                    empresa=form.empresa.data,
                    ubicacion=form.ubicacion.data,
                    telefono=form.telefono.data,
                    correo=form.correo.data,
                    ruc=form.ruc.data,
                    dv=form.dv.data,
                    itbms=form.itbms.data,
                    observaciones=form.observaciones.data,
                    validez=int(form.validez.data)
                )
                
                # Procesar items
                items_data = json.loads(request.form.get('items', '[]'))
                for item_data in items_data:
                    item = Item(
                        descripcion=item_data['descripcion'],
                        precio_unitario=float(item_data['precio_unitario']),
                        unidades=int(item_data['unidades'])
                    )
                    item.calcular_total()
                    cotizacion.items.append(item)
                
                # Calcular totales
                cotizacion.calcular_totales()
                
                # Guardar en base de datos
                db.session.add(cotizacion)
                db.session.commit()
                
                # Generar PDF
                pdf = generar_pdf_cotizacion(cotizacion)
                
                # Enviar por email si se solicitó
                if request.form.get('enviar_email') == 'true':
                    enviar_cotizacion(cotizacion, pdf)
                
                return jsonify({
                    'success': True,
                    'message': 'Cotización creada exitosamente',
                    'numero': cotizacion.numero
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Error al crear la cotización: {str(e)}'
                }), 500
                
    return render_template('cotizaciones/formulario_empresa.html', form=form)

@cotizaciones_bp.route('/natural/nueva', methods=['GET', 'POST'])
@login_required
def nueva_natural():
    form = CotizacionNaturalForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Similar a nueva_empresa pero sin campos empresariales
                cotizacion = Cotizacion(
                    numero=generar_numero_cotizacion(),
                    tipo='natural',
                    nombre=form.nombre.data,
                    ubicacion=form.ubicacion.data,
                    telefono=form.telefono.data,
                    correo=form.correo.data,
                    itbms=form.itbms.data,
                    observaciones=form.observaciones.data,
                    validez=int(form.validez.data)
                )
                
                # Procesar items
                items_data = json.loads(request.form.get('items', '[]'))
                for item_data in items_data:
                    item = Item(
                        descripcion=item_data['descripcion'],
                        precio_unitario=float(item_data['precio_unitario']),
                        unidades=int(item_data['unidades'])
                    )
                    item.calcular_total()
                    cotizacion.items.append(item)
                
                cotizacion.calcular_totales()
                db.session.add(cotizacion)
                db.session.commit()
                
                pdf = generar_pdf_cotizacion(cotizacion)
                
                if request.form.get('enviar_email') == 'true':
                    enviar_cotizacion(cotizacion, pdf)
                
                return jsonify({
                    'success': True,
                    'message': 'Cotización creada exitosamente',
                    'numero': cotizacion.numero
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Error al crear la cotización: {str(e)}'
                }), 500
                
    return render_template('cotizaciones/formulario_natural.html', form=form)

@cotizaciones_bp.route('/buscar')
@login_required
def buscar():
    return render_template('cotizaciones/buscar.html')

@cotizaciones_bp.route('/api/buscar')
@login_required
def api_buscar():
    query = request.args.get('query', '')
    tipo = request.args.get('tipo', 'todos')
    estado = request.args.get('estado', 'todos')
    
    cotizaciones = Cotizacion.query
    
    if tipo != 'todos':
        cotizaciones = cotizaciones.filter_by(tipo=tipo)
    
    if estado != 'todos':
        cotizaciones = cotizaciones.filter_by(estado=estado)
    
    if query:
        cotizaciones = cotizaciones.filter(
            or_(
                Cotizacion.numero.ilike(f'%{query}%'),
                Cotizacion.nombre.ilike(f'%{query}%'),
                Cotizacion.empresa.ilike(f'%{query}%')
            )
        )
    
    cotizaciones = cotizaciones.order_by(Cotizacion.fecha.desc()).all()
    
    return jsonify([c.to_dict() for c in cotizaciones])

@cotizaciones_bp.route('/<numero>')
@login_required
def ver_cotizacion(numero):
    cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
    return render_template('cotizaciones/ver_cotizacion.html', cotizacion=cotizacion)

@cotizaciones_bp.route('/<numero>/pdf')
@login_required
def descargar_pdf(numero):
    cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
    pdf = generar_pdf_cotizacion(cotizacion)
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'cotizacion_{numero}.pdf'
    )
@cotizaciones_bp.route('/<numero>/aprobar', methods=['POST'])
@login_required
def aprobar_cotizacion(numero):
    cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
    
    if cotizacion.estado != 'pendiente':
        return jsonify({
            'success': False,
            'message': 'Esta cotización no está pendiente de aprobación'
        }), 400
    
    try:
        # Cambiar estado de la cotización
        cotizacion.estado = 'aprobada'
        
        # Crear factura
        factura = Factura(
            numero=f"FAC{cotizacion.numero[3:]}",
            cotizacion_id=cotizacion.id,
            total=cotizacion.total,
            estado='pendiente'
        )
        
        db.session.add(factura)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cotización aprobada y factura generada exitosamente',
            'factura_numero': factura.numero
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al aprobar la cotización: {str(e)}'
        }), 500

@cotizaciones_bp.route('/<numero>/rechazar', methods=['POST'])
@login_required
def rechazar_cotizacion(numero):
    cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
    
    if cotizacion.estado != 'pendiente':
        return jsonify({
            'success': False,
            'message': 'Esta cotización no está pendiente'
        }), 400
    
    try:
        cotizacion.estado = 'rechazada'
        cotizacion.fecha_rechazo = datetime.utcnow()
        motivo = request.form.get('motivo', '')
        if motivo:
            cotizacion.observaciones = f"{cotizacion.observaciones or ''}\nMotivo de rechazo: {motivo}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cotización rechazada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al rechazar la cotización: {str(e)}'
        }), 500

@cotizaciones_bp.route('/<numero>/enviar-email', methods=['POST'])
@login_required
def reenviar_email(numero):
    cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
    
    try:
        pdf = generar_pdf_cotizacion(cotizacion)
        enviar_cotizacion(cotizacion, pdf)
        
        return jsonify({
            'success': True,
            'message': 'Cotización enviada por email exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al enviar el email: {str(e)}'
        }), 500

@cotizaciones_bp.route('/<numero>/duplicar', methods=['POST'])
@login_required
def duplicar_cotizacion(numero):
    cotizacion_original = Cotizacion.query.filter_by(numero=numero).first_or_404()
    
    try:
        # Crear nueva cotización con los mismos datos
        nueva_cotizacion = Cotizacion(
            numero=generar_numero_cotizacion(),
            tipo=cotizacion_original.tipo,
            nombre=cotizacion_original.nombre,
            empresa=cotizacion_original.empresa,
            ubicacion=cotizacion_original.ubicacion,
            telefono=cotizacion_original.telefono,
            correo=cotizacion_original.correo,
            ruc=cotizacion_original.ruc,
            dv=cotizacion_original.dv,
            itbms=cotizacion_original.itbms,
            validez=cotizacion_original.validez
        )
        
        # Duplicar items
        for item_original in cotizacion_original.items:
            nuevo_item = Item(
                descripcion=item_original.descripcion,
                precio_unitario=item_original.precio_unitario,
                unidades=item_original.unidades
            )
            nuevo_item.calcular_total()
            nueva_cotizacion.items.append(nuevo_item)
        
        nueva_cotizacion.calcular_totales()
        db.session.add(nueva_cotizacion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cotización duplicada exitosamente',
            'numero': nueva_cotizacion.numero
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al duplicar la cotización: {str(e)}'
        }), 500

@cotizaciones_bp.route('/<numero>', methods=['DELETE'])
@login_required
def eliminar_cotizacion(numero):
    cotizacion = Cotizacion.query.filter_by(numero=numero).first_or_404()
    
    if cotizacion.estado == 'aprobada' and hasattr(cotizacion, 'factura'):
        return jsonify({
            'success': False,
            'message': 'No se puede eliminar una cotización que ya tiene factura'
        }), 400
    
    try:
        db.session.delete(cotizacion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cotización eliminada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar la cotización: {str(e)}'
        }), 500