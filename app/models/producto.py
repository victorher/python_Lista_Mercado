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
    email: Mapped[Optional[str]] = mapped_column(String(120), unique=True, nullable=True) 
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_temporary_password: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(self, username: str, email: Optional[str] = None):
        self.username = username
        self.email = email
        self.is_temporary_password = False

    def set_password(self, password, is_temporary=False):
        self.password_hash = generate_password_hash(password)
        self.is_temporary_password = is_temporary

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_password_complexity(password):
        """Valida que la contraseña cumpla con los requisitos de seguridad."""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        
        import re
        if not re.search(r"[a-z]", password):
            return False, "La contraseña debe contener al menos una letra minúscula."
        if not re.search(r"[A-Z]", password):
            return False, "La contraseña debe contener al menos una letra mayúscula."
        if not re.search(r"\d", password):
            return False, "La contraseña debe contener al menos un número."
        if not re.search(r"[{,.\*/\\@}]", password):
            return False, "La contraseña debe contener al menos un carácter especial del conjunto {, . * / \ @}."
        
        return True, ""

    def get_reset_token(self):
        """Genera un token seguro que expira en 30 minutos."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verifica el token y devuelve el usuario si es válido."""
        s = Serializer(current_app.app_context().app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
        except:
            return None
        return db.session.get(Usuario, data.get('user_id'))

class Producto(db.Model):
    __tablename__ = 'productos'
    
    # Definición moderna con Mapped para tipado estático
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    unidad_medida: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # Litros, gramos, etc.
    tengo_en_casa: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, nombre: str, cantidad: int = 1, unidad_medida: Optional[str] = None, fecha_vencimiento: Optional[date] = None, tengo_en_casa: bool = False):
        """Constructor explícito para que Pylance reconozca los parámetros."""
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad_medida = unidad_medida
        self.fecha_vencimiento = fecha_vencimiento
        self.tengo_en_casa = tengo_en_casa

    @property
    def dias_vencimiento(self) -> Optional[int]:
        if not self.fecha_vencimiento:
            return None
        hoy = datetime.now().date()
        return (self.fecha_vencimiento - hoy).days

    @property
    def dias_vencimiento_texto(self) -> str:
        delta = self.dias_vencimiento
        if delta is None:
            return ""
        
        if delta < 0:
            return f"Vencido hace {abs(delta)} días"
        elif delta == 0:
            return "Vence hoy"
        elif delta == 1:
            return "Vence mañana"
        else:
            return f"Vence en {delta} días"

    @property
    def estado_vencimiento(self):
        delta = self.dias_vencimiento
        if delta is None:
            return 'ninguno'
        
        if delta < 0:
            return 'vencido'     # Rojo
        elif delta <= 3:
            return 'por_vencer'  # Amarillo
        return 'ok'              # Verde

    def __repr__(self) -> str:
        return f'<Producto {self.nombre}>'
