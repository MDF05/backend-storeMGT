from flask import Blueprint, request, jsonify
from models import db, Transaction, TransactionItem, Product, Customer, DebtRecord, StockHistory
from datetime import datetime

sales_bp = Blueprint('sales', __name__)


def _remove_transaction(transaction):
    """Helper to safely remove a transaction:
    - revert product stock quantities
    - add stock history entries describing the revert
    - adjust customer points and total_debt
    - delete associated DebtRecord entries
    - delete the transaction
    """
    try:
        # Revert stock and add history
        for item in list(transaction.items):
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity = (product.stock_quantity or 0) + (item.quantity or 0)
                history = StockHistory(
                    product_id=product.id,
                    change_amount=item.quantity,
                    change_type='revert_delete',
                    note=f'Reverted by deletion of Transaction #{transaction.id}'
                )
                db.session.add(history)

        # Adjust customer points and debt
        if transaction.customer_id:
            customer = Customer.query.get(transaction.customer_id)
            if customer:
                # Remove points earned from this transaction (best-effort)
                try:
                    points = int(transaction.total_amount / 10)
                    customer.points = max(0, (customer.points or 0) - points)
                except Exception:
                    pass

                # Remove debt records linked to this transaction
                debt_records = DebtRecord.query.filter_by(transaction_id=transaction.id).all()
                for dr in debt_records:
                    try:
                        customer.total_debt = (customer.total_debt or 0) - (dr.amount or 0)
                    except Exception:
                        pass
                    db.session.delete(dr)

        # Finally delete transaction (TransactionItem rows have cascade delete)
        db.session.delete(transaction)
        db.session.flush()
        return True, None
    except Exception as e:
        return False, str(e)

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


@sales_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_sale(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    ok, err = _remove_transaction(transaction)
    if not ok:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete transaction: {err}'}), 500

    db.session.commit()
    return jsonify({'status': 'deleted', 'transaction_id': transaction_id}), 200


@sales_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete_sales():
    data = request.json or {}
    ids = data.get('ids', [])
    if not isinstance(ids, list) or not ids:
        return jsonify({'error': 'Provide a non-empty "ids" list in JSON body'}), 400

    results = {'deleted': [], 'failed': {}}
    for tid in ids:
        transaction = Transaction.query.get(tid)
        if not transaction:
            results['failed'][str(tid)] = 'not found'
            continue
        ok, err = _remove_transaction(transaction)
        if ok:
            results['deleted'].append(tid)
        else:
            results['failed'][str(tid)] = err

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Commit failed: {e}'}), 500

    return jsonify(results), 200


@sales_bp.route('/delete-by-filter', methods=['POST'])
def delete_sales_by_filter():
    """Delete transactions matching a filter.
    Accepts JSON body with one of:
      - product_id: delete transactions that contain this product
      - category_id: delete transactions that contain any product in this category
    """
    data = request.json or {}
    product_id = data.get('product_id')
    category_id = data.get('category_id')

    if not product_id and not category_id:
        return jsonify({'error': 'Provide product_id or category_id in JSON body'}), 400

    query = Transaction.query.join(TransactionItem)
    if product_id:
        query = query.filter(TransactionItem.product_id == int(product_id))
    elif category_id:
        query = query.join(Product).filter(Product.category_id == int(category_id))

    transactions = query.distinct().all()
    if not transactions:
        return jsonify({'deleted_count': 0, 'message': 'No matching transactions found'}), 200

    deleted = []
    failed = {}
    for t in transactions:
        ok, err = _remove_transaction(t)
        if ok:
            deleted.append(t.id)
        else:
            failed[str(t.id)] = err

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Commit failed: {e}'}), 500

    return jsonify({'deleted_count': len(deleted), 'deleted': deleted, 'failed': failed}), 200
