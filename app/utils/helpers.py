from datetime import datetime
import locale
from flask import current_app
import os
from werkzeug.utils import secure_filename
import uuid

# Configurar locale para Panamá
try:
    locale.setlocale(locale.LC_ALL, 'es_PA.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Fallback

def format_currency(amount):
    """Formatea cantidades monetarias"""
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"

def format_date(date):
    """Formatea fechas al formato local"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    return date.strftime("%d de %B de %Y")

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder='uploads'):
    """Guarda un archivo de forma segura"""
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return filename
    return None

def delete_file(filename, folder='uploads'):
    """Elimina un archivo de forma segura"""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

def generar_numero_cotizacion():
    """Genera un número único para la cotización"""
    timestamp = datetime.now().strftime('%Y%m%d')
    unique = uuid.uuid4().hex[:6].upper()
    return f"COT{timestamp}{unique}"

def generar_numero_factura():
    """Genera un número único para la factura"""
    timestamp = datetime.now().strftime('%Y%m%d')
    unique = uuid.uuid4().hex[:6].upper()
    return f"FAC{timestamp}{unique}"

def calcular_totales(items, incluir_itbms=False):
    """Calcula subtotal, ITBMS y total"""
    subtotal = sum(item.precio_unitario * item.unidades for item in items)
    itbms = subtotal * 0.07 if incluir_itbms else 0
    total = subtotal + itbms
    return subtotal, itbms, total