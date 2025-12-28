from flask import Blueprint, request, jsonify
from models import db, Product, Category, StockHistory, TransactionItem

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@products_bp.route('/bulk', methods=['POST'])
def add_products_bulk():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Input must be a list of products'}), 400
    
    added_products = []
    try:
        for item in data:
            new_product = Product(
                name=item['name'],
                sku=item['sku'],
                price=item['price'],
                stock_quantity=item['stock_quantity'],
                low_stock_threshold=int(item.get('low_stock_threshold', 10)),
                category_id=item['category_id']
            )
            db.session.add(new_product)
            db.session.flush() # Get ID for history
            
            # Initial Stock History
            if new_product.stock_quantity > 0:
                history = StockHistory(
                    product_id=new_product.id,
                    change_amount=new_product.stock_quantity,
                    change_type='initial',
                    note='Bulk Import'
                )
                db.session.add(history)
            
            added_products.append(new_product)

        db.session.commit()
        return jsonify([p.to_dict() for p in added_products]), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@products_bp.route('/', methods=['POST'])
def add_product():
    data = request.json
    try:
        new_product = Product(
            name=data['name'],
            sku=data['sku'],
            price=data['price'],
            stock_quantity=data['stock_quantity'],
            low_stock_threshold=int(data.get('low_stock_threshold', 10)),
            category_id=data['category_id']
        )
        db.session.add(new_product)
        db.session.flush() # Get ID
        
        # Initial Stock History
        if new_product.stock_quantity > 0:
            history = StockHistory(
                product_id=new_product.id,
                change_amount=new_product.stock_quantity,
                change_type='initial',
                note='Initial Stock'
            )
            db.session.add(history)

        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # Check if product has sales history
    sales_count = TransactionItem.query.filter_by(product_id=id).count()
    if sales_count > 0:
        return jsonify({'error': 'Cannot delete product that has sales history. Archive it instead.'}), 400

    # Delete related stock history first (CASCADE behavior simulation)
    StockHistory.query.filter_by(product_id=id).delete()
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@products_bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    
    if 'name' in data: product.name = data['name']
    if 'sku' in data: product.sku = data['sku']
    if 'price' in data: product.price = data['price']
    
    # Handle Stock Change History
    if 'stock_quantity' in data:
        old_stock = product.stock_quantity
        new_stock = int(data['stock_quantity'])
        diff = new_stock - old_stock
        
        if diff != 0:
            change_type = data.get('change_type', 'manual_update')
            # If no explicit type, guess based on context or just use manual
            if change_type == 'manual_update' and diff > 0:
                change_type = 'restock' # Optimistic guess
            
            note = data.get('note', 'Manual update via Inventory')
            
            history = StockHistory(
                product_id=product.id,
                change_amount=diff,
                change_type=change_type,
                note=note
            )
            db.session.add(history)
            
        product.stock_quantity = new_stock

    if 'low_stock_threshold' in data: product.low_stock_threshold = int(data['low_stock_threshold'])
    if 'category_id' in data: product.category_id = data['category_id']
    
    db.session.commit()
    return jsonify(product.to_dict())

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
