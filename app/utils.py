from datetime import datetime
from weasyprint import HTML
from flask import render_template
import os

def generar_numero_cotizacion():
    """Genera un número único para la cotización"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"COT{timestamp}"

def generar_numero_factura():
    """Genera un número único para la factura"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"FAC{timestamp}"

def calcular_totales(items, incluir_itbms=False):
    """Calcula subtotal, ITBMS y total"""
    subtotal = sum(item['precio_unitario'] * item['unidades'] for item in items)
    itbms = subtotal * 0.07 if incluir_itbms else 0
    total = subtotal + itbms
    return subtotal, itbms, total

def generar_pdf_cotizacion(cotizacion, template_path):
    """Genera PDF de cotización"""
    html_content = render_template(template_path, cotizacion=cotizacion)
    return HTML(string=html_content).write_pdf()

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS