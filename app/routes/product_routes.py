from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..services.product_service import ProductService
from ..forms.product_forms import ProductForm

product_bp = Blueprint('products', __name__)

@product_bp.route('/')
@login_required
def index():
    form = ProductForm()
    products = ProductService.get_user_products(current_user.id)
    return render_template('index.html', productos=products, form=form)

@product_bp.route('/agregar', methods=['POST'])
@login_required
def agregar():
    form = ProductForm()
    if form.validate_on_submit():
        ProductService.create_product(
            user_id=current_user.id,
            name=form.nombre.data or "",
            quantity=int(form.cantidad.data) if form.cantidad.data is not None else 1,
            unit=form.unidad_medida.data,
            expiry_date=form.vencimiento.data
        )
        flash(f'Producto "{form.nombre.data}" agregado.', 'success')
    else:
        # Centralización de errores de validación
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{form[field].label.text}: {error}", 'danger')
                
    return redirect(url_for('products.index'))

@product_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle(id):
    new_state = ProductService.toggle_product_status(id, current_user.id)
    if new_state is not None:
        return jsonify({
            "success": True, 
            "new_state": new_state,
            "message": "Estado actualizado"
        })
    return jsonify({"success": False, "message": "Acceso denegado"}), 403

@product_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    if ProductService.delete_product(id, current_user.id):
        flash('Producto eliminado con éxito.', 'success')
    else:
        flash('Error: No se pudo eliminar el producto.', 'danger')
    return redirect(url_for('products.index'))
