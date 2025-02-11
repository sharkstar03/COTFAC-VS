from flask import render_template, current_app
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os

def generar_pdf_cotizacion(cotizacion):
    """Genera PDF de cotización usando WeasyPrint"""
    font_config = FontConfiguration()
    html_content = render_template(
        'pdf/cotizacion_template.html',
        cotizacion=cotizacion
    )
    
    css = get_pdf_styles()
    
    # Crear PDF en memoria
    pdf = HTML(string=html_content).write_pdf(
        stylesheets=[css],
        font_config=font_config
    )
    
    # Guardar temporalmente si es necesario
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', f'cotizacion_{cotizacion.numero}.pdf')
    with open(temp_path, 'wb') as f:
        f.write(pdf)
    
    return pdf

def generar_pdf_factura(factura):
    """Genera PDF de factura usando WeasyPrint"""
    font_config = FontConfiguration()
    html_content = render_template(
        'pdf/factura_template.html',
        factura=factura
    )
    
    css = get_pdf_styles()
    
    pdf = HTML(string=html_content).write_pdf(
        stylesheets=[css],
        font_config=font_config
    )
    
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', f'factura_{factura.numero}.pdf')
    with open(temp_path, 'wb') as f:
        f.write(pdf)
    
    return pdf

def get_pdf_styles():
    """Retorna los estilos CSS para los PDFs"""
    return CSS(string='''
        @page {
            size: letter;
            margin: 2.5cm;
            @top-right {
                content: "Página " counter(page) " de " counter(pages);
            }
        }
        @font-face {
            font-family: 'Roboto';
            src: url('static/fonts/Roboto-Regular.ttf');
        }
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
        }
        .header {
            margin-bottom: 2cm;
        }
        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 100px;
            color: rgba(0,0,0,0.1);
            z-index: -1;
        }
    ''')