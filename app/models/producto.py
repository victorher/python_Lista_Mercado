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

    def __init__(self, username: str, email: Optional[str] = None):
        self.username = username
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    tengo_en_casa: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, nombre: str, cantidad: int = 1, fecha_vencimiento: Optional[date] = None, tengo_en_casa: bool = False):
        """Constructor explícito para que Pylance reconozca los parámetros."""
        self.nombre = nombre
        self.cantidad = cantidad
        self.fecha_vencimiento = fecha_vencimiento
        self.tengo_en_casa = tengo_en_casa

    @property
    def estado_vencimiento(self):
        if not self.fecha_vencimiento:
            return 'ninguno'
        hoy = datetime.now().date()
        delta = (self.fecha_vencimiento - hoy).days
        if delta < 0:
            return 'vencido'     # Rojo
        elif delta <= 3:
            return 'por_vencer'  # Amarillo
        return 'ok'              # Verde

    def __repr__(self) -> str:
        return f'<Producto {self.nombre}>'
