from typing import List, Optional
from datetime import date
from ..extensions import db
from ..models.product import Product

class ProductService:
    """Capa de servicios para la gestión de productos. 
    Totalmente desacoplada de la capa web (sin Flask).
    """
    
    @staticmethod
    def get_user_products(user_id: int) -> List[Product]:
        return Product.query.filter_by(user_id=user_id).order_by(Product.in_stock, Product.name).all()

    @staticmethod
    def create_product(user_id: int, name: str, quantity: int = 1, 
                       unit: Optional[str] = None, expiry_date: Optional[date] = None) -> Product:
        product = Product(
            name=name,
            user_id=user_id,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def toggle_product_status(product_id: int, user_id: int) -> Optional[bool]:
        """Devuelve True si cambió el estado, False si no encontró el producto."""
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if product:
            product.in_stock = not product.in_stock
            db.session.commit()
            return product.in_stock
        return None

    @staticmethod
    def delete_product(product_id: int, user_id: int) -> bool:
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False
