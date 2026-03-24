from datetime import datetime, date, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey
from ..extensions import db

if TYPE_CHECKING:
    from .user import User

class Product(db.Model):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # kg, litros, etc.
    in_stock: Mapped[bool] = mapped_column(Boolean, default=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación con el usuario: a quién pertenece este producto
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="products")

    @property
    def days_until_expiry(self) -> Optional[int]:
        if not self.expiry_date:
            return None
        today = datetime.now().date()
        return (self.expiry_date - today).days

    @property
    def expiry_text(self) -> str:
        delta = self.days_until_expiry
        if delta is None: return ""
        if delta < 0: return f"Vencido hace {abs(delta)} días"
        if delta == 0: return "Vence hoy"
        if delta == 1: return "Vence mañana"
        return f"Vence en {delta} días"

    @property
    def expiry_status(self) -> str:
        delta = self.days_until_expiry
        if delta is None: return 'none'
        if delta < 0: return 'expired'
        if delta <= 3: return 'warning'
        return 'ok'

    def __repr__(self) -> str:
        return f'<Product {self.name} (User: {self.user_id})>'
