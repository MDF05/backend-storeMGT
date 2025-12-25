from app import app
from models import db, Category, Customer

with app.app_context():
    print("--- Categories ---")
    cats = Category.query.all()
    for c in cats:
        print(f"{c.id}: {c.name}")
    
    print("\n--- Customers ---")
    custs = Customer.query.all()
    for c in custs:
        print(f"{c.id}: {c.name} (Debt: {c.total_debt})")
