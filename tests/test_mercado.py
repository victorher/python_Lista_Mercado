import pytest
from app import create_app
from app.models.producto import db, Producto, Usuario

@pytest.fixture
def client():
    app = create_app()
    # Forzar base de datos en RAM para no tocar base datos producción
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False 

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Crear usuario de prueba
            user = Usuario(username='testuser', email='test@test.com')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            yield client
            db.drop_all()

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_agregar_producto(client):
    login(client, 'testuser', 'testpass')
    # Enviar datos simulando un formulario de HTML
    response = client.post('/agregar', data={
        'nombre': 'Leche',
        'cantidad': 2,
        'vencimiento': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Leche' in response.data

def test_agregar_producto_invalido(client):
    login(client, 'testuser', 'testpass')
    # Probar nombre vacío
    response = client.post('/agregar', data={
        'nombre': '',
        'cantidad': 1
    }, follow_redirects=True)
    assert b'El nombre del producto no puede estar vac\xc3\xado.' in response.data

def test_toggle_producto(client):
    login(client, 'testuser', 'testpass')
    # Primero agregamos un producto
    client.post('/agregar', data={'nombre': 'Pan', 'cantidad': 1}, follow_redirects=True)
    
    # Obtenemos el producto de la DB (en memoria)
    with client.application.app_context():
        prod = Producto.query.filter_by(nombre='Pan').first()
        assert prod is not None
        assert prod.tengo_en_casa is False
        prod_id = prod.id

    # Toggle
    response = client.get(f'/toggle/{prod_id}', follow_redirects=True)
    assert response.status_code == 200
    
    with client.application.app_context():
        prod = db.session.get(Producto, prod_id)
        assert prod.tengo_en_casa is True
