from flask import Blueprint, request, jsonify
from models import db, StoreConfig

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET'])
def get_settings():
    config = StoreConfig.query.first()
    if not config:
        config = StoreConfig()
        db.session.add(config)
        db.session.commit()
    return jsonify(config.to_dict())

@settings_bp.route('/', methods=['PUT'])
def update_settings():
    config = StoreConfig.query.first()
    if not config:
        config = StoreConfig()
        db.session.add(config)
    
    data = request.json
    if 'store_name' in data:
        config.store_name = data['store_name']
    if 'store_address' in data:
        config.store_address = data['store_address']
    if 'default_low_stock_threshold' in data:
        config.default_low_stock_threshold = int(data['default_low_stock_threshold'])
    if 'pic_name' in data:
        config.pic_name = data['pic_name']
        
    db.session.commit()
    return jsonify(config.to_dict())
