from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff') # admin, staff

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_debt = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'points': self.points,
            'total_debt': self.total_debt
        }

class DebtRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False) # Change in debt (positive = added debt, negative = paid)
    type = db.Column(db.String(20), nullable=False) # 'credit' (add debt), 'payment' (pay debt)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat()
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10) # Custom warning limit
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'low_stock_threshold': self.low_stock_threshold,
            'category_name': self.category.name if self.category else None,
            'category_id': self.category_id
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(50), default='cash') # cash, debt
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    items = db.relationship('TransactionItem', backref='transaction', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'payment_method': self.payment_method,
            'customer_id': self.customer_id,
            'items': [item.to_dict() for item in self.items]
        }

class TransactionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product') # Add relationship
    quantity = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'quantity': self.quantity,
            'price_at_sale': self.price_at_sale
        }

class StoreConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), default="My Store")
    store_address = db.Column(db.String(255), default="Jakarta, Indonesia")
    default_low_stock_threshold = db.Column(db.Integer, default=10)

    def to_dict(self):
        return {
            'store_name': self.store_name,
            'store_address': self.store_address,
            'default_low_stock_threshold': self.default_low_stock_threshold
        }
