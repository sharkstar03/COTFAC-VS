from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')

class CotizacionEmpresaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    empresa = StringField('Empresa', validators=[DataRequired()])
    ubicacion = StringField('Ubicación', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    correo = StringField('Correo', validators=[Email()])
    ruc = StringField('RUC')
    dv = StringField('DV')
    itbms = BooleanField('Incluir ITBMS')

class CotizacionNaturalForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    ubicacion = StringField('Ubicación', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    correo = StringField('Correo', validators=[Email()])
    itbms = BooleanField('Incluir ITBMS')

class ItemForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired()])
    precio_unitario = FloatField('Precio Unitario', validators=[DataRequired()])
    unidades = IntegerField('Unidades', validators=[DataRequired()])