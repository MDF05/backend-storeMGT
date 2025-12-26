from flask import Blueprint, request, jsonify
from models import db, Transaction, TransactionItem, Product, Customer, DebtRecord, StockHistory
from datetime import datetime

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/', methods=['POST'])
def create_sale():
    data = request.json
    items_data = data.get('items', [])
    customer_id = data.get('customer_id')
    payment_method = data.get('payment_method', 'cash')
    paid_amount = float(data.get('paid_amount', 0)) if data.get('paid_amount') is not None else None
    
    if not items_data:
        return jsonify({'error': 'No items in transaction'}), 400

    total_amount = 0
    transaction_items = []

    # Calculate total and verify stock
    for item in items_data:
        product = Product.query.get(item['product_id'])
        if not product:
            return jsonify({'error': f'Product {item["product_id"]} not found'}), 404
        
        if product.stock_quantity < item['quantity']:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
        
        item_total = product.price * item['quantity']
        total_amount += item_total
        
        # Deduct stock
        product.stock_quantity -= item['quantity']
        
        # Log Stock History
        history = StockHistory(
            product_id=product.id,
            change_amount=-item['quantity'],
            change_type='sale',
            note=f'Sold in Transaction'
        )
        db.session.add(history)
        
        # Create transaction item
        t_item = TransactionItem(
            product_id=product.id,
            quantity=item['quantity'],
            price_at_sale=product.price
        )
        transaction_items.append(t_item)

    # If paid_amount is not specified (e.g. simple cash sale), assume full payment unless logic dictates otherwise
    # But for debt, we need explicit logic.
    if paid_amount is None:
        paid_amount = total_amount

    # Handle Customer
    if customer_id:
        customer = Customer.query.get(customer_id)
        if customer:
            points_earned = int(total_amount / 10)
            customer.points += points_earned
            
            # Handle Debt
            if payment_method == 'debt':
                debt_amount = total_amount - paid_amount
                if debt_amount > 0:
                    customer.total_debt += debt_amount

    # Create Transaction
    new_transaction = Transaction(
        total_amount=total_amount,
        paid_amount=paid_amount,
        payment_method=payment_method,
        items=transaction_items,
        customer_id=customer_id
    )
    
    db.session.add(new_transaction)
    db.session.flush() # Generate ID

    # Create Debt Record if needed
    if customer_id and payment_method == 'debt':
        debt_amount = total_amount - paid_amount
        if debt_amount > 0:
            debt_record = DebtRecord(
                customer_id=customer_id,
                transaction_id=new_transaction.id,
                amount=debt_amount,
                type='debt',
                description=f'Debt from Transaction #{new_transaction.id}'
            )
            db.session.add(debt_record)

    db.session.commit()
    
    return jsonify(new_transaction.to_dict()), 201

@sales_bp.route('/', methods=['GET'])
def get_sales():
    sales = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify([s.to_dict() for s in sales])
