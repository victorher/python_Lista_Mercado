import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Usar variables de entorno para mayor seguridad y flexibilidad
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

    # Nota: host='0.0.0.0' hace que la app sea accesible en tu red local.
    # En producción, se recomienda usar un servidor WSGI como Gunicorn o Waitress.
    app.run(host=host, port=port, debug=debug)