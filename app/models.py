from flask_login import UserMixin
from datetime import datetime
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    tipo = db.Column(db.String(20))  # 'empresa' o 'natural'
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    nombre = db.Column(db.String(120))
    empresa = db.Column(db.String(120))
    ubicacion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(120))
    ruc = db.Column(db.String(20))
    dv = db.Column(db.String(5))
    itbms = db.Column(db.Boolean, default=False)
    subtotal = db.Column(db.Float)
    total = db.Column(db.Float)
    estado = db.Column(db.String(20), default='pendiente')
    fecha_rechazo = db.Column(db.DateTime)
    items = db.relationship('Item', backref='cotizacion', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizacion.id'))
    descripcion = db.Column(db.String(200))
    precio_unitario = db.Column(db.Float)
    unidades = db.Column(db.Integer)
    total = db.Column(db.Float)

class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizacion.id'))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    total = db.Column(db.Float)
    cotizacion = db.relationship('Cotizacion', backref=db.backref('factura', lazy=True))