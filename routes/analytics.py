from flask import Blueprint, jsonify
from models import Transaction, TransactionItem, Product, Category
import pandas as pd
from sqlalchemy import func
from models import db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
def get_summary():
    # Total Revenue
    total_revenue = db.session.query(func.sum(Transaction.total_amount)).scalar() or 0
    
    # Total Sales Count
    total_sales = db.session.query(func.count(Transaction.id)).scalar() or 0
    
    # Total Products
    total_products = db.session.query(func.count(Product.id)).scalar() or 0

    return jsonify({
        'total_revenue': total_revenue,
        'total_sales_count': total_sales,
        'total_products': total_products
    })

@analytics_bp.route('/daily-sales', methods=['GET'])
def get_daily_sales():
    # Use pandas for easier time-series grouping if dataset gets large, 
    # but for now running SQL query is efficient enough or we can load into DF
    
    query = db.session.query(Transaction.date, Transaction.total_amount).statement
    df = pd.read_sql(query, db.session.bind)
    
    if df.empty:
        return jsonify([])

    df['date'] = pd.to_datetime(df['date']).dt.date
    daily_sales = df.groupby('date')['total_amount'].sum().reset_index()
    
    return jsonify(daily_sales.to_dict(orient='records'))

@analytics_bp.route('/top-products', methods=['GET'])
def get_top_products():
    query = db.session.query(
        Product.name, 
        func.sum(TransactionItem.quantity).label('total_sold')
    ).join(TransactionItem).group_by(Product.id).order_by(func.sum(TransactionItem.quantity).desc()).limit(5).statement
    
    df = pd.read_sql(query, db.session.bind)
    
    if df.empty:
        return jsonify([])
        
    return jsonify(df.to_dict(orient='records'))
