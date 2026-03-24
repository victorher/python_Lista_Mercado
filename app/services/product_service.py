from ..extensions import db
from ..models.product import Product

class ProductService:
    @staticmethod
    def get_user_products(user_id):
        """Obtiene todos los productos de un usuario específico."""
        return Product.query.filter_by(user_id=user_id).order_by(Product.in_stock).all()

    @staticmethod
    def create_product(user_id, name, quantity=1, unit=None, expiry_date=None):
        """Crea un nuevo producto vinculado a un usuario."""
        product = Product(
            name=name,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date,
            user_id=user_id
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def toggle_product_status(product_id, user_id):
        """Cambia el estado de stock (comprado/no comprado).
        Incluye validación de propiedad (Security Check).
        """
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if product:
            product.in_stock = not product.in_stock
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_product(product_id, user_id):
        """Elimina un producto asegurando que pertenece al usuario."""
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False
