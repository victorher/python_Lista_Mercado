from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ProductForm(FlaskForm):
    nombre = StringField('Producto', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(max=100, message="Máximo 100 caracteres")
    ])
    cantidad = IntegerField('Cantidad', default=1, validators=[
        DataRequired(),
        NumberRange(min=1, message="Mínimo 1 unidad")
    ])
    unidad_medida = SelectField('Unidad', choices=[
        ('unidades', 'Unidades'),
        ('litros', 'L'),
        ('mililitros', 'ml'),
        ('gramos', 'g'),
        ('kilogramos', 'Kg'),
        ('libras', 'Lb'),
        ('onzas', 'Oz'),
        ('paca', 'Pk')
    ])
    vencimiento = DateField('Vencimiento', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Agregar')
