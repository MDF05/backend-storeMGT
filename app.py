from routes.customers import customers_bp
from routes.auth import auth_bp
from routes.analytics import analytics_bp
from routes.sales import sales_bp
from routes.products import products_bp
from routes.settings import settings_bp
from routes.history import history_bp
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from dotenv import load_dotenv
import os

# Load Environment Variables
load_dotenv()

# Create the app
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:consistent@localhost:5432/store_management'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret')


# Initialize Plugins
db.init_app(app)
jwt = JWTManager(app)

# Import and Register Blueprints

app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(sales_bp, url_prefix='/api/sales')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(settings_bp, url_prefix='/api/settings')
app.register_blueprint(history_bp, url_prefix='/api/history')

# Create tables (For dev purposes, usually use Flask-Migrate in prod)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
