from flask import Blueprint, jsonify
from models import StockHistory

history_bp = Blueprint('history', __name__)

@history_bp.route('/product/<int:id>', methods=['GET'])
def get_product_history(id):
    history = StockHistory.query.filter_by(product_id=id).order_by(StockHistory.timestamp.desc()).all()
    return jsonify([h.to_dict() for h in history])

@history_bp.route('/restocks', methods=['GET'])
def get_restock_history():
    # Fetch all positive stock changes (Restocks, Corrections, Initial)
    history = StockHistory.query.filter(StockHistory.change_amount > 0).order_by(StockHistory.timestamp.desc()).all()
    return jsonify([h.to_dict() for h in history])
