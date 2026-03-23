# 🛒 Mercado Inteligente

Aplicación web profesional para gestionar tu lista de compras, con control de inventario, unidades de medida y alertas inteligentes de vencimiento.

## 🚀 Inicio Rápido

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/victorher/python_Lista_Mercado.git
   cd python_Lista_Mercado
   ```

2. **Configurar el entorno:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Variables de Entorno:**
   Crea un archivo `.env` en la raíz (ver `GUIA_DESARROLLO.md` para detalles).

4. **Ejecutar:**
   ```bash
   python run.py
   ```
   Accede a `http://localhost:5000`. Usuario por defecto: `admin` / `admin123`.

---

## 🛠️ Guía de Git (Flujo de Trabajo)

Sigue estos pasos para mantener tu proyecto sincronizado con el repositorio remoto.

### 1. Vincular por primera vez (Si no lo has hecho)
```bash
git init
git remote add origin https://github.com/victorher/python_Lista_Mercado.git
```

### 2. Subir cambios al servidor (Push)
Cada vez que termines una mejora o corrección:
```bash
# Ver qué archivos han cambiado
git status

# Añadir todos los cambios al área de preparación
git add .

# Crear un punto de guardado con un mensaje descriptivo
git commit -m "Descripción clara de lo que hiciste (ej: Añadida unidad de medida)"

# Subir los cambios a la rama principal (main o master)
git push -u origin main
```

### 3. Bajar cambios del servidor (Pull)
Si trabajas desde otro computador o quieres actualizar tu código local:
```bash
git pull origin main
```

---

## ✨ Características Principales
- 📦 **Gestión de Stock**: Añade, edita y marca productos como comprados.
- 📏 **Unidades de Medida**: Soporte para Litros, Gramos, Libras, Oz, Unidades, etc.
- ⚠️ **Alertas de Vencimiento**: Indicadores visuales automáticos (Vence hoy, Mañana, ¡Vencido!).
- 🔐 **Seguridad**: Autenticación de usuarios, protección CSRF y contraseñas seguras (hashes).
- 🧪 **Pruebas**: Suite de pruebas automatizadas con Pytest.

---
*Para una guía técnica detallada paso a paso, consulta [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md).*
