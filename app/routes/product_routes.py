from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..services.product_service import ProductService
from ..forms.product_forms import ProductForm
from datetime import datetime

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
            name=form.nombre.data,
            quantity=form.cantidad.data,
            unit=form.unidad_medida.data,
            expiry_date=form.vencimiento.data
        )
        flash(f'Producto "{form.nombre.data}" agregado.', 'success')
    else:
        # Si hay errores de validación, los mostramos mediante flash
        for fieldName, errorMessages in form.errors.items():
            for error in errorMessages:
                flash(f"Error en {form[fieldName].label.text}: {error}", 'danger')
                
    return redirect(url_for('products.index'))

@product_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle(id):
    if ProductService.toggle_product_status(id, current_user.id):
        return jsonify({"success": True, "message": "Estado actualizado"})
    return jsonify({"success": False, "message": "No tienes permiso"}), 403

@product_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    if ProductService.delete_product(id, current_user.id):
        flash('Producto eliminado.', 'success')
    else:
        flash('No tienes permiso.', 'danger')
    return redirect(url_for('products.index'))
