import secrets
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from ..models.producto import db, Producto, Usuario
from .. import mail

bp = Blueprint('mercado', __name__)

@bp.before_app_request
def check_temp_password():
    if current_user.is_authenticated:
        # Lista de rutas permitidas cuando se tiene contraseña temporal
        allowed_routes = ['mercado.change_password', 'mercado.logout', 'static']
        if current_user.is_temporary_password and request.endpoint not in allowed_routes:
            flash('Debes cambiar tu contraseña temporal antes de continuar.', 'warning')
            return redirect(url_for('mercado.change_password'))

def generate_random_password(length=12):
    """Genera una contraseña aleatoria que cumple con los requisitos."""
    # Conjunto de caracteres especiales solicitado: { , . * / \ @ }
    special_chars = r"{,.*\/@}"
    alphabet = string.ascii_letters + string.digits + special_chars
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        is_valid, _ = Usuario.validate_password_complexity(password)
        if is_valid:
            return password

def send_temp_password_email(user, temp_password):
    msg = Message('Nueva Contraseña Temporal',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''Se ha generado una contraseña temporal para tu cuenta.
Tu contraseña temporal es: {temp_password}

Inicia sesión con esta contraseña y se te pedirá que la cambies inmediatamente.
'''
    mail.send(msg)

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('mercado.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = Usuario.query.filter_by(email=email).first()
        if user:
            try:
                temp_pass = generate_random_password()
                user.set_password(temp_pass, is_temporary=True)
                db.session.commit()
                send_temp_password_email(user, temp_pass)
                flash('Se ha enviado una contraseña temporal a tu correo electrónico.', 'info')
                return redirect(url_for('mercado.login'))
            except Exception as e:
                db.session.rollback()
                # Imprimir el error real en la consola para diagnóstico (SMTP error, etc.)
                print(f"DEBUG ERROR ENVÍO CORREO: {str(e)}")
                flash('Error al procesar la solicitud. Por favor, intenta más tarde.', 'danger')
        else:
            flash('No existe una cuenta con ese correo electrónico.', 'warning')
    return render_template('reset_request.html')

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if not current_user.is_temporary_password:
        return redirect(url_for('mercado.index'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password:
            flash('La nueva contraseña es obligatoria.', 'danger')
            return render_template('reset_token.html', title='Cambiar Contraseña')
            
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset_token.html', title='Cambiar Contraseña')

        is_valid, message = Usuario.validate_password_complexity(new_password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('reset_token.html', title='Cambiar Contraseña')

        current_user.set_password(new_password, is_temporary=False)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada correctamente.', 'success')
        return redirect(url_for('mercado.index'))
    
    return render_template('reset_token.html', title='Cambiar Contraseña')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('mercado.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password')
        
        if not username:
            flash('El nombre de usuario es obligatorio.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')
            
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template('register.html')

        if email and Usuario.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'danger')
            return render_template('register.html')

        is_valid, message = Usuario.validate_password_complexity(password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('register.html')
            
        user = Usuario(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Cuenta creada exitosamente. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('mercado.login'))
        
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_temporary_password:
             return redirect(url_for('mercado.change_password'))
        return redirect(url_for('mercado.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        user = Usuario.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('mercado.login'))
            
        login_user(user, remember=remember)
        
        if user.is_temporary_password:
            flash('Debes cambiar tu contraseña temporal.', 'warning')
            return redirect(url_for('mercado.change_password'))

        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('mercado.index'))
        
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('mercado.login'))

@bp.route('/')
@login_required
def index():
    # Ordenamos por estado de compra (los comprados al final)
    productos = Producto.query.order_by(Producto.tengo_en_casa).all()
    return render_template('index.html', productos=productos)

@bp.route('/agregar', methods=['POST'])
@login_required
def agregar():
    nombre = request.form.get('nombre', '').strip()
    
    # Validación: no agregar si el nombre está vacío o es muy largo
    if not nombre:
        flash('El nombre del producto no puede estar vacío.', 'danger')
        return redirect(url_for('mercado.index'))
    
    if len(nombre) > 100:
        flash('El nombre del producto es demasiado largo (máx 100 caracteres).', 'danger')
        return redirect(url_for('mercado.index'))

    # Conversión segura a entero y validación de rango
    try:
        cantidad = int(request.form.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
    except (ValueError, TypeError):
        cantidad = 1
        
    unidad_medida = request.form.get('unidad_medida')
    vencimiento_str = request.form.get('vencimiento')
    
    vencimiento = None
    if vencimiento_str:
        try:
            vencimiento = datetime.strptime(vencimiento_str, '%Y-%m-%d').date()
        except ValueError:
            vencimiento = None
            flash('Formato de fecha de vencimiento inválido.', 'warning')
    
    try:
        nuevo_prod = Producto(
            nombre=nombre, 
            cantidad=cantidad, 
            unidad_medida=unidad_medida, 
            fecha_vencimiento=vencimiento
        )
        db.session.add(nuevo_prod)
        db.session.commit()
        flash(f'Producto "{nombre}" agregado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al guardar el producto.', 'danger')
    
    return redirect(url_for('mercado.index'))

@bp.route('/toggle/<int:id>')
@login_required
def toggle_comprado(id):
    # Uso moderno de Flask-SQLAlchemy 3.x
    producto = db.get_or_404(Producto, id)
    producto.tengo_en_casa = not producto.tengo_en_casa
    db.session.commit()
    estado = "marcado como comprado" if producto.tengo_en_casa else "devuelto a la lista"
    flash(f'"{producto.nombre}" {estado}.', 'info')
    return redirect(url_for('mercado.index'))
