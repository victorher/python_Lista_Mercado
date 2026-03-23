# 🛒 Guía Maestra de Desarrollo: Mercado Inteligente (Full Stack)

Esta guía detalla cada paso, archivo y configuración necesaria para construir la aplicación desde cero hasta el estado actual.

---

## 📂 1. Estructura de Directorios

Primero, crea la siguiente estructura de carpetas en tu directorio raíz (`Mercado/`):

```powershell
Mercado/
├── app/                # Carpeta principal de la aplicación
│   ├── models/         # Modelos de Base de Datos (SQLAlchemy)
│   ├── routes/         # Controladores y Rutas (Blueprints)
│   ├── templates/      # Vistas HTML (Jinja2)
│   └── __init__.py     # Inicialización (Application Factory)
├── instance/           # Archivos locales (Base de datos SQLite)
├── tests/              # Pruebas automatizadas (Pytest)
├── .env                # Variables de entorno (Secretos)
├── run.py              # Punto de entrada del servidor
└── requirements.txt    # Dependencias del proyecto
```

---

## 🛠️ 2. Entorno y Dependencias

Ejecuta estos comandos en tu terminal (PowerShell en Windows):

```powershell
# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Crear el archivo de dependencias
New-Item requirements.txt -ItemType File
```

**Archivo: `requirements.txt`** (Contenido a copiar):
```text
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.2
Flask-Mail==0.10.0
python-dotenv==1.2.2
pytest==9.0.2
SQLAlchemy==2.0.48
itsdangerous==2.2.0
```

Instala todo con: `pip install -r requirements.txt`

---

## 🔐 3. Configuración y Seguridad

**Archivo: `.env`** (Crea este archivo en la raíz):
```ini
SECRET_KEY=clave_super_secreta_123
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_DEFAULT_SENDER=tu_correo@gmail.com
```

---

## 🏗️ 4. El Corazón: Modelos de Datos

**Archivo: `app/models/producto.py`**
Define cómo se guardan los datos usando SQLAlchemy 2.0.

```python
from datetime import datetime, date, timezone
from typing import Optional
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Date, DateTime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.app_context().app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
        except:
            return None
        return db.session.get(Usuario, data.get('user_id'))

class Producto(db.Model):
    __tablename__ = 'productos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    unidad_medida: Mapped[Optional[str]] = mapped_column(String(20))
    tengo_en_casa: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def dias_vencimiento(self) -> Optional[int]:
        if not self.fecha_vencimiento: return None
        return (self.fecha_vencimiento - datetime.now().date()).days

    @property
    def dias_vencimiento_texto(self) -> str:
        delta = self.dias_vencimiento
        if delta is None: return ""
        if delta < 0: return f"Vencido hace {abs(delta)} días"
        if delta == 0: return "Vence hoy"
        return f"Vence en {delta} días"

    @property
    def estado_vencimiento(self):
        delta = self.dias_vencimiento
        if delta is None: return 'ninguno'
        return 'vencido' if delta < 0 else 'por_vencer' if delta <= 3 else 'ok'
```

---

## 🚀 5. Inicialización de la App

**Archivo: `app/__init__.py`**
Aquí se configuran las extensiones y se crea la base de datos automáticamente.

```python
import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
from .models.producto import db, Usuario

csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()

def create_app(config_override=None):
    app = Flask(__name__)
    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mercado.db')
    if config_override: app.config.update(config_override)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    from .routes import mercado_routes
    app.register_blueprint(mercado_routes.bp)

    with app.app_context():
        db.create_all()
        # Crear admin por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', email='admin@ejemplo.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    return app
```

---

## 🛣️ 6. Rutas y Lógica de Negocio

**Archivo: `app/routes/mercado_routes.py`**
Controla el flujo de la aplicación.

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from ..models.producto import db, Producto, Usuario

bp = Blueprint('mercado', __name__)

@bp.route('/')
@login_required
def index():
    productos = Producto.query.order_by(Producto.tengo_en_casa).all()
    return render_template('index.html', productos=productos)

@bp.route('/agregar', methods=['POST'])
@login_required
def agregar():
    nombre = request.form.get('nombre', '').strip()
    cantidad = int(request.form.get('cantidad', 1))
    unidad_medida = request.form.get('unidad_medida')
    vencimiento_str = request.form.get('vencimiento')
    
    vencimiento = None
    if vencimiento_str:
        vencimiento = datetime.strptime(vencimiento_str, '%Y-%m-%d').date()
    
    nuevo_prod = Producto(nombre=nombre, cantidad=cantidad, unidad_medida=unidad_medida, fecha_vencimiento=vencimiento)
    db.session.add(nuevo_prod)
    db.session.commit()
    flash(f'"{nombre}" agregado.', 'success')
    return redirect(url_for('mercado.index'))

@bp.route('/toggle/<int:id>')
@login_required
def toggle_comprado(id):
    producto = db.get_or_404(Producto, id)
    producto.tengo_en_casa = not producto.tengo_en_casa
    db.session.commit()
    return redirect(url_for('mercado.index'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('mercado.index'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('mercado.login'))
```

---

## 🎨 7. Vistas (Templates HTML)

### 7.1 Estructura Base: `app/templates/base.html`
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Mercado{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>.producto-comprado { text-decoration: line-through; opacity: 0.6; }</style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary mb-4 shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">🛒 Mercado Inteligente</a>
            {% if current_user.is_authenticated %}
                <a class="btn btn-outline-light btn-sm" href="{{ url_for('mercado.logout') }}">Salir</a>
            {% endif %}
        </div>
    </nav>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for cat, msg in messages %}<div class="alert alert-{{cat}}">{{msg}}</div>{% endfor %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

### 7.2 Panel Principal: `app/templates/index.html`
Incluye el formulario de ingreso y la lista con indicadores de vencimiento.

```html
{% extends "base.html" %}
{% block content %}
<div class="card mb-4 shadow-sm">
    <div class="card-body">
        <form action="{{ url_for('mercado.agregar') }}" method="POST" class="row g-3">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <div class="col-md-4"><input type="text" name="nombre" class="form-control" placeholder="Producto" required></div>
            <div class="col-md-2"><input type="number" name="cantidad" class="form-control" value="1" min="1"></div>
            <div class="col-md-2">
                <select name="unidad_medida" class="form-select">
                    <option value="unidades">Unidades</option>
                    <option value="litros">Litros</option>
                    <option value="gramos">Gramos</option>
                </select>
            </div>
            <div class="col-md-2"><input type="date" name="vencimiento" class="form-control"></div>
            <div class="col-md-2"><button type="submit" class="btn btn-success w-100">+ Añadir</button></div>
        </form>
    </div>
</div>

<div class="list-group">
    {% for prod in productos %}
    <div class="list-group-item d-flex justify-content-between align-items-center {% if prod.tengo_en_casa %}bg-light{% endif %}">
        <a href="{{ url_for('mercado.toggle_comprado', id=prod.id) }}" class="text-decoration-none text-dark">
            <span class="fs-5 {% if prod.tengo_en_casa %}producto-comprado{% endif %}">
                {{ prod.nombre }} <small class="text-muted">(x{{ prod.cantidad }} {{ prod.unidad_medida or '' }})</small>
            </span>
        </a>
        {% if prod.fecha_vencimiento and not prod.tengo_en_casa %}
            <span class="badge rounded-pill bg-{{ 'danger' if prod.estado_vencimiento == 'vencido' else 'warning' if prod.estado_vencimiento == 'por_vencer' else 'success' }}">
                {{ prod.dias_vencimiento_texto }}
            </span>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}
```

### 7.3 Login: `app/templates/login.html`
```html
{% extends "base.html" %}
{% block content %}
<div class="mx-auto" style="max-width: 400px; margin-top: 50px;">
    <div class="card shadow-sm">
        <div class="card-body p-4">
            <h2 class="text-center mb-4">Ingresar</h2>
            <form method="POST">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <div class="mb-3"><label class="form-label">Usuario</label><input type="text" name="username" class="form-control" required></div>
                <div class="mb-3"><label class="form-label">Contraseña</label><input type="password" name="password" class="form-control" required></div>
                <button type="submit" class="btn btn-primary w-100">Entrar</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🧪 8. Pruebas de Calidad

**Archivo: `tests/test_mercado.py`**
```python
import pytest
from app import create_app
from app.models.producto import db, Producto, Usuario

@pytest.fixture
def client():
    app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True, 'WTF_CSRF_ENABLED': False})
    with app.test_client() as client:
        with app.app_context():
            user = Usuario(username='test', email='t@t.com'); user.set_password('pass')
            db.session.add(user); db.session.commit()
            yield client

def test_agregar(client):
    client.post('/login', data={'username':'test', 'password':'pass'})
    res = client.post('/agregar', data={'nombre':'Pan', 'cantidad':1, 'unidad_medida':'unidades'}, follow_redirects=True)
    assert b'Pan' in res.data
```

Ejecuta con: `$env:PYTHONPATH="."; pytest`

---

## ▶️ 9. Ejecución Final

**Archivo: `run.py`**
```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Comando:** `python run.py`
¡Listo! Abre `http://localhost:5000` y disfruta de tu app.
