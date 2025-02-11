from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from .. import mail
import os

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error enviando email: {e}")

def enviar_email(subject, recipient, template, attachments=None, **kwargs):
    """Envía un email de forma asíncrona"""
    msg = Message(
        subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.html = render_template(f"email/{template}.html", **kwargs)
    
    # Agregar adjuntos si existen
    if attachments:
        for filename, content_type, data in attachments:
            msg.attach(
                filename=filename,
                content_type=content_type,
                data=data
            )
    
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def enviar_cotizacion(cotizacion, pdf):
    """Envía cotización por email"""
    enviar_email(
        subject=f'Cotización #{cotizacion.numero}',
        recipient=cotizacion.correo,
        template='cotizacion',
        attachments=[('cotizacion.pdf', 'application/pdf', pdf)],
        cotizacion=cotizacion
    )

def enviar_factura(factura, pdf):
    """Envía factura por email"""
    enviar_email(
        subject=f'Factura #{factura.numero}',
        recipient=factura.cotizacion.correo,
        template='factura',
        attachments=[('factura.pdf', 'application/pdf', pdf)],
        factura=factura
    )