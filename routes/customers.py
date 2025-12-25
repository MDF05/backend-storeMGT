from flask import Blueprint, request, jsonify
from models import db, Customer, DebtRecord

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@customers_bp.route('/', methods=['POST'])
def add_customer():
    data = request.json
    try:
        new_customer = Customer(
            name=data['name'],
            email=data.get('email', ''),
            phone=data.get('phone', '')
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify(new_customer.to_dict()), 201
    except Exception as e:
        print(f"ERROR ADDING CUSTOMER: {e}") # Debugging
        return jsonify({'error': str(e)}), 400

@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'})

@customers_bp.route('/<int:id>/debt_history', methods=['GET'])
def get_debt_history(id):
    records = DebtRecord.query.filter_by(customer_id=id).order_by(DebtRecord.date.desc()).all()
    return jsonify([r.to_dict() for r in records])

@customers_bp.route('/<int:id>/pay_debt', methods=['POST'])
def pay_debt(id):
    customer = Customer.query.get_or_404(id)
    data = request.json
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
        
    if amount > customer.total_debt:
        return jsonify({'error': 'Payment exceeds total debt'}), 400

    customer.total_debt -= amount
    
    record = DebtRecord(
        customer_id=id,
        amount=-amount, # Negative for payment
        type='payment',
        description=data.get('description', 'Debt Payment')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'message': 'Payment successful', 'new_debt': customer.total_debt})
