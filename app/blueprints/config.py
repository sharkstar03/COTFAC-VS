from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from ..models import db, Configuracion
from ..forms import ConfiguracionForm
from ..utils.helpers import save_file, delete_file

config_bp = Blueprint('config', __name__, url_prefix='/config')

@config_bp.route('/', methods=['GET', 'POST'])
@login_required
def configuracion():
    config = Configuracion.get_config()
    form = ConfiguracionForm(obj=config)
    
    if form.validate_on_submit():
        if not config:
            config = Configuracion()
        
        # Actualizar campos del formulario
        form.populate_obj(config)
        
        # Manejar el logo
        if form.logo.data:
            # Eliminar logo anterior si existe
            if config.logo:
                delete_file(config.logo, 'logos')
            
            # Guardar nuevo logo
            filename = save_file(form.logo.data, 'logos')
            if filename:
                config.logo = filename
        
        db.session.add(config)
        db.session.commit()
        
        flash('Configuración actualizada exitosamente', 'success')
        return redirect(url_for('config.configuracion'))
    
    return render_template('config/configuracion.html', form=form)