from app import app
from models import db, Category, Product, User, Customer

def seed():
    with app.app_context():
        db.create_all()
        
        # Create Admin User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@store.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created Admin User (admin/admin123)")

        # Check if products exist
        if Product.query.first():
            print("Product data already exists.")
            # Commit users if added
            db.session.commit()
            return

        # Add Categories
        cats = ['Electronics', 'Clothing', 'Groceries', 'Books']
        cat_objs = []
        for c in cats:
            cat = Category(name=c)
            db.session.add(cat)
            cat_objs.append(cat)
        
        db.session.commit()
        
        # Add Products
        p1 = Product(name='Laptop Pro', sku='LP001', price=1299.99, stock_quantity=10, category_id=cat_objs[0].id)
        p2 = Product(name='Smartphone X', sku='SP001', price=999.99, stock_quantity=20, category_id=cat_objs[0].id)
        p3 = Product(name='T-Shirt', sku='TS001', price=19.99, stock_quantity=50, category_id=cat_objs[1].id)
        p4 = Product(name='Banana', sku='FR001', price=0.99, stock_quantity=100, category_id=cat_objs[2].id)
        
        db.session.add_all([p1, p2, p3, p4])

        # Add Customers
        c1 = Customer(name='John Doe', email='john@example.com', phone='555-0101', points=100)
        c2 = Customer(name='Jane Smith', email='jane@example.com', phone='555-0102', points=50)
        db.session.add_all([c1, c2])

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
