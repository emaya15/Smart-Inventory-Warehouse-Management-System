import datetime
from app.database import SessionLocal
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.auth.password import get_password_hash
from app.utils.enums import UserRole, UnitType

def seed():
    db = SessionLocal()
    print("Seeding database...")
    try:
        # 1. Warehouses
        wh1 = db.query(Warehouse).filter_by(warehouse_code="WH-CHN-01").first()
        if not wh1:
            wh1 = Warehouse(warehouse_code="WH-CHN-01", name="Chennai Central DC", city="Chennai", address="Ambattur Industrial Estate", capacity=50000)
            db.add(wh1)
            db.commit()
            db.refresh(wh1)

        wh2 = db.query(Warehouse).filter_by(warehouse_code="WH-BLR-01").first()
        if not wh2:
            wh2 = Warehouse(warehouse_code="WH-BLR-01", name="Bangalore Hub", city="Bangalore", address="Peenya Industrial Area", capacity=40000)
            db.add(wh2)
            db.commit()
            db.refresh(wh2)

        # 2. Users
        users = [
            ("admin@example.com", "Admin User", UserRole.ADMIN, None),
            ("manager@example.com", "Inventory Lead", UserRole.INVENTORY_MANAGER, None),
            ("staff@example.com", "Warehouse Associate", UserRole.WAREHOUSE_STAFF, wh1.id),
        ]
        for email, name, role, wid in users:
            if not db.query(User).filter_by(email=email).first():
                u = User(email=email, hashed_password=get_password_hash("Password123!"), full_name=name, role=role, assigned_warehouse_id=wid)
                db.add(u)
        db.commit()

        # 3. Categories
        cat = db.query(Category).filter_by(name="Electronics").first()
        if not cat:
            cat = Category(name="Electronics", description="Gadgets and accessories")
            db.add(cat)
            db.commit()
            db.refresh(cat)

        # 4. Supplier
        sup = db.query(Supplier).filter_by(supplier_code="SUP-001").first()
        if not sup:
            sup = Supplier(supplier_code="SUP-001", name="Apex Tech Components", email="apex@supplier.com", phone="9876543210", gst_number="33AAAAA0000A1Z5", address="Chennai, TN", lead_time_days=4)
            db.add(sup)
            db.commit()
            db.refresh(sup)

        # 5. Customer
        cust = db.query(Customer).filter_by(customer_code="CUST-001").first()
        if not cust:
            cust = Customer(customer_code="CUST-001", name="Apex Retail Group", email="procurement@apexretail.com", phone="9123456780", address="Bangalore, KA", credit_limit=500000.0)
            db.add(cust)
            db.commit()
            db.refresh(cust)

        # 6. Product
        prod = db.query(Product).filter_by(sku="SKU-HEADPHONE-01").first()
        if not prod:
            prod = Product(sku="SKU-HEADPHONE-01", barcode="8901234567890", name="Wireless ANC Headphones", category_id=cat.id, unit=UnitType.PIECE, cost_price=2500.0, selling_price=4999.0, reorder_level=20, reorder_quantity=100, preferred_supplier_id=sup.id)
            db.add(prod)
            db.commit()
            db.refresh(prod)

        # 7. Inventory & Batches
        inv = db.query(Inventory).filter_by(product_id=prod.id, warehouse_id=wh1.id).first()
        if not inv:
            inv = Inventory(product_id=prod.id, warehouse_id=wh1.id, quantity_on_hand=50, quantity_reserved=0)
            db.add(inv)
            b1 = Batch(batch_number="BATCH-2026A", product_id=prod.id, warehouse_id=wh1.id, quantity=30, manufacturing_date=datetime.date(2026, 1, 1), expiry_date=datetime.date(2026, 11, 1), unit_cost=2500.0)
            b2 = Batch(batch_number="BATCH-2026B", product_id=prod.id, warehouse_id=wh1.id, quantity=20, manufacturing_date=datetime.date(2026, 2, 1), expiry_date=datetime.date(2026, 12, 1), unit_cost=2500.0)
            db.add_all([b1, b2])
            db.commit()

        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
