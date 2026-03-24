import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product

@pytest.fixture
def app():
    # Usamos configuración de desarrollo pero deshabilitamos CSRF para los tests
    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        # Crear usuario de prueba inicial
        user = User(username='testuser', email='test@test.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, username, password):
    return client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_login_success(client):
    """Prueba el inicio de sesión exitoso."""
    response = login(client, 'testuser', 'testpass')
    assert response.status_code == 200
    assert b'Mi Lista' in response.data

def test_agregar_producto(client):
    """Prueba agregar un producto con el nuevo sistema de servicios."""
    login(client, 'testuser', 'testpass')
    
    response = client.post('/agregar', data={
        'nombre': 'Leche',
        'cantidad': 2,
        'unidad_medida': 'litros'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Leche' in response.data
    
    # Verificar en la base de datos
    with client.application.app_context():
        prod = Product.query.filter_by(name='Leche').first()
        assert prod is not None  # Silencia el aviso del editor
        assert prod.quantity == 2
        assert prod.unit == 'litros'

def test_toggle_producto_ajax(client):
    """Prueba el cambio de estado mediante la nueva ruta JSON."""
    login(client, 'testuser', 'testpass')
    
    # 1. Agregamos un producto manualmente en la DB del test
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None  # Silencia el aviso del editor (user.id)
        prod = Product(name='Pan', user_id=user.id, quantity=1)
        db.session.add(prod)
        db.session.commit()
        prod_id = prod.id

    # 2. Llamamos a la nueva ruta AJAX (POST)
    response = client.post(f'/toggle/{prod_id}')
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    
    # 3. Verificamos cambio en DB
    with client.application.app_context():
        prod = db.session.get(Product, prod_id)
        assert prod is not None  # Silencia el aviso del editor (prod.in_stock)
        assert prod.in_stock is True

def test_security_isolation(client):
    """PRUEBA CRÍTICA: Un usuario no puede ver/editar productos de otro."""
    # 1. Crear un segundo usuario
    with client.application.app_context():
        user2 = User(username='hacker', email='hacker@test.com')
        user2.set_password('hacker123')
        db.session.add(user2)
        db.session.commit()
        
        # El testuser (ya logueado) crea un producto
        u1 = User.query.filter_by(username='testuser').first()
        assert u1 is not None  # Silencia el aviso del editor (u1.id)
        p1 = Product(name='Tesoro', user_id=u1.id)
        db.session.add(p1)
        db.session.commit()
        p1_id = p1.id

    # 2. Cerramos sesión de testuser y entramos como hacker
    client.get('/auth/logout')
    login(client, 'hacker', 'hacker123')
    
    # 3. Intentamos ver la lista (el producto 'Tesoro' no debe aparecer)
    response = client.get('/')
    assert b'Tesoro' not in response.data
    
    # 4. Intentamos hacer toggle al producto del otro usuario
    response = client.post(f'/toggle/{p1_id}')
    assert response.status_code == 403 # Acceso denegado
