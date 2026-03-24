from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

def limpiar_usuarios():
    with app.app_context():
        print("Iniciando limpieza de usuarios...")
        
        # Contar cuántos usuarios hay antes
        total_antes = User.query.count()
        
        # Eliminar todos menos el 'admin'
        usuarios_a_eliminar = User.query.filter(User.username != 'admin').all()
        cantidad = len(usuarios_a_eliminar)
        
        for u in usuarios_a_eliminar:
            db.session.delete(u)
        
        db.session.commit()
        
        # Verificar si el admin existe
        admin = User.query.filter_by(username='admin').first()
        
        print(f"--- RESULTADO ---")
        print(f"Usuarios eliminados: {cantidad}")
        print(f"¿Admin conservado?: {'SÍ' if admin else 'NO'}")
        print(f"Total de usuarios ahora: {User.query.count()}")
        print("-----------------")

if __name__ == "__main__":
    limpiar_usuarios()
