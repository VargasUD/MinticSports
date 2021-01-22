from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class FormLog(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(message='Email, esta vacio')])
    password = PasswordField('Contraseña', validators=[DataRequired(message='password, esta vacia')])
    
    enviar = SubmitField('Ingresar')


class FormForgot(FlaskForm):
    email = StringField('email', validators=[DataRequired(message='Email, esta vacio')])
    enviar2 = SubmitField('Enviar Email')