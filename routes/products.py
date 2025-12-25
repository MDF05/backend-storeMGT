from flask import Blueprint, request, jsonify
from models import db, Product, Category

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@products_bp.route('/', methods=['POST'])
def add_product():
    data = request.json
    try:
        new_product = Product(
            name=data['name'],
            sku=data['sku'],
            price=data['price'],
            stock_quantity=data['stock_quantity'],
            category_id=data['category_id']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])

@products_bp.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    try:
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
