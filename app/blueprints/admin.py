from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import db, User, Configuracion
from ..forms import UserForm, ConfiguracionForm
from ..utils.helpers import save_file
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acceso no autorizado', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = User.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuario/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_usuario():
    form = UserForm()
    if form.validate_on_submit():
        usuario = User()
        form.populate_obj(usuario)
        usuario.set_password(form.password.data)
        db.session.add(usuario)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin.usuarios'))
    return render_template('admin/usuario_form.html', form=form)

@admin_bp.route('/usuario/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    usuario = User.query.get_or_404(id)
    form = UserForm(obj=usuario)
    if form.validate_on_submit():
        form.populate_obj(usuario)
        if form.password.data:
            usuario.set_password(form.password.data)
        db.session.commit()
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('admin.usuarios'))
    return render_template('admin/usuario_form.html', form=form, usuario=usuario)

@admin_bp.route('/usuario/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    if current_user.id == id:
        flash('No puede eliminar su propio usuario', 'error')
        return redirect(url_for('admin.usuarios'))
    
    usuario = User.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('admin.usuarios'))