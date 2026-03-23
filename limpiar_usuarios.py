from app import create_app
from app.models.producto import db, Usuario

app = create_app()

def limpiar_usuarios():
    with app.app_context():
        print("Iniciando limpieza de usuarios...")
        
        # Contar cuántos usuarios hay antes
        total_antes = Usuario.query.count()
        
        # Eliminar todos menos el 'admin'
        usuarios_a_eliminar = Usuario.query.filter(Usuario.username != 'admin').all()
        cantidad = len(usuarios_a_eliminar)
        
        for u in usuarios_a_eliminar:
            db.session.delete(u)
        
        db.session.commit()
        
        # Verificar si el admin existe, si no, lo creará create_app() automáticamente al reiniciar
        # o podemos asegurarnos aquí.
        admin = Usuario.query.filter_by(username='admin').first()
        
        print(f"--- RESULTADO ---")
        print(f"Usuarios eliminados: {cantidad}")
        print(f"¿Admin conservado?: {'SÍ' if admin else 'NO (se recreará al iniciar la app)'}")
        print(f"Total de usuarios ahora: {Usuario.query.count()}")
        print("-----------------")

if __name__ == "__main__":
    limpiar_usuarios()
