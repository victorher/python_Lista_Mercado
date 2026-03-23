# 🛒 Guía de Desarrollo: Lista de Mercado Inteligente

¡Hola! Como Arquitecto de Software, te guiaré paso a paso en este proyecto. Es un proyecto excelente para consolidar tus conocimientos de desarrollo web en Python de forma escalable y profesional.

## Elección del Framework: Flask vs FastAPI
Para este caso en particular, **recomiendo Flask**. 
**¿Por qué?** FastAPI brilla al crear APIs REST (enviar y recibir JSON) y aplicaciones altamente asíncronas. Sin embargo, dado que utilizaremos **HTML, Jinja2 y Bootstrap** (renderizado del lado del servidor o SSR), Flask tiene integración nativa y un ecosistema clásico más robusto para renderizar plantillas web directamente sin complicar el frontend.

---

## 1. Preparación del entorno

1️⃣ **Explicación conceptual**
Necesitamos un espacio aislado ("entorno virtual") para que las librerías de este proyecto no interfieran con otras de tu computador. Luego, crearemos una estructura de carpetas profesional que separe la base de datos (modelos) de la vista (templates y rutas).

2️⃣ **Comandos exactos de terminal**
*(Ejecuta en tu terminal PowerShell dentro de `c:\MisProyectos\Python\Mercado`)*:

```powershell
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar el entorno virtual (PowerShell en Windows)
.\venv\Scripts\Activate.ps1

# 3. Crear estructura de carpetas y archivos base
mkdir app, app/templates, app/static, app/models, app/routes, tests
New-Item run.py, requirements.txt, app/__init__.py -ItemType File
```

3️⃣ **Código y Estructura resultante**
- `venv/`: Entorno virtual local (no se toca).
- `app/`: La carpeta principal de la aplicación.
  - `templates/`: Donde irán los archivos HTML.
  - `static/`: Para CSS propio, JS, imágenes.
  - `models/`: Dónde se define la base de datos (SQLite).
  - `routes/`: Las URLs y controladores.
- `run.py`: El punto de entrada para arrancar tu servidor.

5️⃣ **Buenas prácticas**
✅ Nunca subas la carpeta `venv/` a tu repositorio web (usa `.gitignore`).

---

## 2. Manejo de dependencias

1️⃣ **Explicación conceptual**
`requirements.txt` es la "lista de ingredientes" de tu proyecto. Anota exactamente qué librerías y versiones necesita el proyecto para funcionar en otro ordenador.

2️⃣ **Comandos exactos de terminal**
```powershell
# Instalar dependencias esenciales
pip install Flask Flask-SQLAlchemy pytest

# Guardar las dependencias actuales en tu archivo
pip freeze > requirements.txt

# Para reconstruir el entorno en el futuro o en otro PC:
pip install -r requirements.txt
```

---

## 3. Diseño de base de datos (SQLite)

1️⃣ **Explicación conceptual**
SQLite guarda los datos en un solo archivo local ligero, ideal para iniciar. Usaremos `Flask-SQLAlchemy` (ORM) que permite tratar las tablas de la base de datos como **clases de Python** normales.

3️⃣ **Código completo de ejemplo**
**Archivo:** `app/models/producto.py`:
```python
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    tengo_en_casa = db.Column(db.Boolean, default=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True) # Opcional
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Método para evaluar fechas (Punto 6)
    @property
    def estado_vencimiento(self):
        if not self.fecha_vencimiento:
            return 'ninguno'
        delta = (self.fecha_vencimiento - datetime.today().date()).days
        if delta < 0:
            return 'vencido'     # Rojo
        elif delta <= 3:
            return 'por_vencer'  # Amarillo
        return 'ok'              # Verde

    def __repr__(self):
        return f'<Producto {self.nombre}>'
```

**Archivo:** `app/__init__.py` (Inicialización central):
```python
from flask import Flask
from .models.producto import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mercado.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Pre-cargar rutas para que flask las sepa usar
    from .routes import mercado_routes
    app.register_blueprint(mercado_routes.bp)
    
    with app.app_context():
        db.create_all() # Crea sqlite:///mercado.db si no existe
        
    return app
```

5️⃣ **Buenas prácticas**
✅ Usar el patrón "Application Factory" (`create_app`) te permite conectar distintas bases de datos para Testeo y para Producción sin mezclar variables globales.

---

## 4. Desarrollo del backend

1️⃣ **Explicación conceptual**
Usaremos **Blueprints**, el sistema interno de Flask para organizar rutas de código sin saturar el archivo principal.

3️⃣ **Código completo de ejemplo**
**Archivo:** `app/routes/mercado_routes.py`
```python
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from ..models.producto import db, Producto

bp = Blueprint('mercado', __name__)

@bp.route('/')
def index():
    productos = Producto.query.order_by(Producto.tengo_en_casa).all()
    # Enviamos los datos al HTML
    return render_template('index.html', productos=productos)

@bp.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get('nombre')
    cantidad = request.form.get('cantidad', 1)
    vencimiento_str = request.form.get('vencimiento')
    
    vencimiento = None
    if vencimiento_str:
        vencimiento = datetime.strptime(vencimiento_str, '%Y-%m-%d').date()
    
    nuevo_prod = Producto(nombre=nombre, cantidad=cantidad, fecha_vencimiento=vencimiento)
    db.session.add(nuevo_prod)
    db.session.commit()
    
    return redirect(url_for('mercado.index'))

@bp.route('/toggle/<int:id>')
def toggle_comprado(id):
    producto = Producto.query.get_or_404(id)
    producto.tengo_en_casa = not producto.tengo_en_casa
    db.session.commit()
    return redirect(url_for('mercado.index'))
```

---

## 5 & 6. Desarrollo del Frontend y Alerta de Vencimiento

1️⃣ **Explicación conceptual**
Usamos Bootstrap vía CDN que nos dará utilidades de estética modernas. La "Alerta de Vencimiento" la insertaremos basándonos en la propiedad `@property estado_vencimiento` de nuestro Modelo en Python (Jinja sabe leer clases de Python).

3️⃣ **Código completo de ejemplo**
**Archivo:** `app/templates/index.html`
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mercado Inteligente</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-dark bg-primary mb-4 shadow-sm">
    <div class="container">
        <span class="navbar-brand mb-0 h1">🛒 Mercado Inteligente</span>
    </div>
</nav>

<div class="container">
    <!-- Panel Agregar -->
    <div class="card mb-4 shadow-sm">
        <div class="card-body">
            <form action="{{ url_for('mercado.agregar') }}" method="POST" class="row g-3">
                <div class="col-md-5">
                    <input type="text" name="nombre" class="form-control" placeholder="Ej: Leche" required>
                </div>
                <div class="col-md-2">
                    <input type="number" name="cantidad" class="form-control" value="1" min="1">
                </div>
                <div class="col-md-3">
                    <input type="date" name="vencimiento" class="form-control" title="Fecha Vencimiento (Opcional)">
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-success w-100">+ Agregar</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Lista de Productos -->
    <div class="list-group shadow-sm">
        {% for prod in productos %}
        <div class="list-group-item d-flex justify-content-between align-items-center {% if prod.tengo_en_casa %}bg-light text-muted{% endif %}">
            
            <div>
                <!-- Toggle Formulario Oculto/Link -->
                <a href="{{ url_for('mercado.toggle_comprado', id=prod.id) }}" class="text-decoration-none {% if prod.tengo_en_casa %}text-muted{% else %}text-dark{% endif %}">
                    <span class="fs-5" style="{% if prod.tengo_en_casa %}text-decoration: line-through;{% endif %}">
                        {{ prod.nombre }} (x{{ prod.cantidad }})
                    </span>
                </a>
            </div>

            <!-- Etiquetas de Vencimiento Lógicas usando el @property de Python -->
            <div>
                {% if prod.fecha_vencimiento and not prod.tengo_en_casa %}
                    {% if prod.estado_vencimiento == 'vencido' %}
                        <span class="badge bg-danger rounded-pill">¡Vencido el {{ prod.fecha_vencimiento }}!</span>
                    {% elif prod.estado_vencimiento == 'por_vencer' %}
                        <span class="badge bg-warning text-dark rounded-pill">Vence pronto ({{ prod.fecha_vencimiento }})</span>
                    {% else %}
                        <span class="badge bg-success rounded-pill">Vence el {{ prod.fecha_vencimiento }}</span>
                    {% endif %}
                {% endif %}
            </div>
            
        </div>
        {% endfor %}
    </div>
</div>

</body>
</html>
```

---

## 7. Buenas prácticas Pythonistas Resumidas

- Cumplimiento estricto del formato HTML semántico.
- Toda lógica robusta y cálculos de fechas, debe estar en el **Modelo DB** (propiedad `estado_vencimiento`), NO en el HTML, para que el HTML sea "tonto" (solo pinta).
- Inyecciones `get_or_404()` previenen que la aplicación arroje errores en el servidor (500) devolviendo elegantemente errores "Página no encontrada" (404) si el usuario modifica índices a mano.

---

## 8. Pruebas Unitarias (testing) con pytest

1️⃣ **Explicación conceptual**
Escribimos un script (robot oculto) que levantará un `mini-clon` del programa con memoria RAM (no encriptado), interactuará con la página mandando botones y revisará las repuestas para asegurar que nadie arruinó la app.

3️⃣ **Código completo de ejemplo**
**Archivo:** `tests/test_mercado.py`
```python
import pytest
from app import create_app
from app.models.producto import db

@pytest.fixture
def client():
    app = create_app()
    # Forzar base de datos en RAM para no tocar base datos producción
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_agregar_producto(client):
    # Enviar datos simulando un formulario de HTML y decirle a flask que siga flechas (redirect)
    response = client.post('/agregar', data={
        'nombre': 'Leche',
        'cantidad': 2,
        'vencimiento': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Leche' in response.data
```

2️⃣ **Comando de Ejecución:** `pytest tests/`

---

## 9. Ejecutar servidor local

3️⃣ **Código completo de ejemplo**
**Archivo:** `run.py` (En la raíz del proyecto)
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0' publicará el socket a toda tu red LAN, no solo interno.
    app.run(host='0.0.0.0', port=5000, debug=True)
```

2️⃣ **Comando para iniciar:**
```powershell
python run.py
```

---

## 10. Convertir mi computador en servidor LAN

1️⃣ **Explicación conceptual**
Al correrlo con 0.0.0.0, Flask avisa "Todos son bienvenidos". Sin embargo, **Windows Firewall** es un muro físico. Debemos abrir un hueco en la pared para el puerto 5000.

2️⃣ **Terminal (Abre PowerShell en modo Administrador!)**:
```powershell
New-NetFirewallRule -DisplayName "App Mercado Interno" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```
4️⃣ **Explicación del uso diario**:
Averigua tu IP en casa corriendo en terminal `ipconfig` (Ejemplo: `192.168.1.15`). 
Desde tu teléfono, estando en el mismo WiFi, entra en un navegador a `http://192.168.1.15:5000`. ¡Boom!, App funcionando!

---

## 11. Acceso desde internet global

1️⃣ **Explicación conceptual**
Recomiendo evitar la compleja ruta de meterse al router de tu operador (Port Forwarding), y usar Software de Túneles seguros como `Cloudflare Tunnels`. El túnel hace que Cloudflare asigne un link público `https` gratis y desvíe sus visitas de forma súper sellada hacia tu `localhost:5000`.

2️⃣ **Comandos exactos de terminal (usando npm, si lo tienes)**
```powershell
npx localtunnel --port 5000
# o su equivalente cloudflared:
cloudflared tunnel url http://localhost:5000
```
Te dará una dirección global para abrir desde el viaje.

---

## 12. Seguridad básica

- **Validación Entradas**: Evitamos peticiones fraudulentas si los requerimientos de la UI (`required`) no concuerdan con la app. Es importante validar en la ruta de guardado si `nombre` está vacío (`if not nombre: abort(400)`).
- **Protección CSRF**: En el futuro, instalarías `Flask-WTF` que automáticamente incrusta llave invisible temporal `{{ form.csrf_token }}` en el HTML, evitando ataques mediante envío de códigos maliciosos externos.
- **Evitar Inyección SQL**: Ya la estás evitando al usar `Flask-SQLAlchemy (db.Model)`. SQLAlchemy limpia variables hostiles intrínsecamente.

---

## 13. Deploy local profesional (Para mantener encendido)

1️⃣ **Explicación conceptual**
Para estar activo 24/7 sin abrir terminal, lo apropiado de Arquitectura es instalar un Servidor WSGI en WSL/Linux (`Gunicorn` en Mac/Linux o `Waitress` en Windows nativo). Flask nativo avisa que es un "development server" inestable sin carga pesada.

2️⃣ **En Linux/WSL (Gunicorn con Systemd)**:
```bash
pip install gunicorn
# Inicia la web asignándole 3 núcleos lógicos de trabajador:
gunicorn -w 3 -b 0.0.0.0:5000 "app:create_app()"
```

Creas `/etc/systemd/system/mercado.service`:
```ini
[Unit]
Description=Gunicorn mercado Flask
After=network.target

[Service]
User=tu_usuario_linux
WorkingDirectory=/home/tu_usuario/Mercado
Environment="PATH=/home/tu_usuario/Mercado/venv/bin"
ExecStart=/home/tu_usuario/Mercado/venv/bin/gunicorn -w 3 -b 0.0.0.0:5000 "app:create_app()"

[Install]
WantedBy=multi-user.target
```
Ejecutar `sudo systemctl enable mercado --now`.

---

## 14. Mejoras futuras a la Arquitectura

Como arquitecto de Software te reto a integrar las siguientes misiones:
- **Convertirla a PWA (Progressive Web App):** Generando un `manifest.json` y Service-worker de JavaScript. Tu teléfono pondrá el app en tu pantalla de inicio y se sentirá nativa sin depender del navegador visible.
- **Dockerización**: Aprender a encapsular la App con un `Dockerfile` base, garantizando compatibilidad en la nube universal sin problemas en Windows vs Mac.
- **Paginación & Búsqueda**: Añadir botones de "ver más", o busqueda Ajax mediante una pequeña API en Python que arroje `jsonify()`.
- **Implementar OAuth/Login:** Añadir manejo de usuarios, de este modo la lista podrá sincronizar entre varios familiares y no combinarse globalmente con la de un amigo ingresando desde el exterior.
