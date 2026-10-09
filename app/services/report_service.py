from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime
from io import BytesIO
import openpyxl
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.batch import Batch
from app.utils.enums import POStatus, SOStatus

def get_dashboard_metrics(db: Session):
    total_products = db.query(Product).filter(Product.is_active == True).count()
    inv_data = db.query(Inventory.quantity_on_hand, Product.cost_price).join(Product, Inventory.product_id == Product.id).all()
    total_val = sum(q * float(c) for q, c in inv_data)
    low_stock = db.query(Inventory).join(Product, Inventory.product_id == Product.id).filter(
        (Inventory.quantity_on_hand - Inventory.quantity_reserved) < Product.reorder_level
    ).count()
    pending_pos = db.query(PurchaseOrder).filter(PurchaseOrder.status.in_([POStatus.DRAFT, POStatus.APPROVED])).count()
    pending_sos = db.query(SalesOrder).filter(SalesOrder.status.in_([SOStatus.CONFIRMED, SOStatus.PICKED, SOStatus.PACKED])).count()
    
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_dispatches = db.query(SalesOrder).filter(SalesOrder.status == SOStatus.DISPATCHED, SalesOrder.dispatched_at >= today_start).count()

    return {
        "total_products": total_products,
        "total_stock_value": round(total_val, 2),
        "low_stock_count": low_stock,
        "pending_purchase_orders": pending_pos,
        "pending_sales_orders": pending_sos,
        "today_dispatches": today_dispatches
    }

def get_low_stock_report(db: Session):
    results = db.query(Product, Inventory).join(Inventory, Product.id == Inventory.product_id).filter(
        (Inventory.quantity_on_hand - Inventory.quantity_reserved) < Product.reorder_level
    ).all()
    report = []
    for prod, inv in results:
        report.append({
            "product_id": prod.id,
            "sku": prod.sku,
            "name": prod.name,
            "available_stock": inv.quantity_on_hand - inv.quantity_reserved,
            "reorder_level": prod.reorder_level,
            "suggested_reorder_quantity": prod.reorder_quantity,
            "preferred_supplier": prod.preferred_supplier.name if prod.preferred_supplier else None
        })
    return report

def generate_stock_excel(db: Session) -> BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Stock Valuation"
    ws.append(["Product SKU", "Product Name", "Warehouse ID", "On Hand", "Reserved", "Available", "Unit Cost", "Valuation"])

    records = db.query(Product, Inventory).join(Inventory, Product.id == Inventory.product_id).all()
    total_val = 0.0
    for prod, inv in records:
        val = inv.quantity_on_hand * float(prod.cost_price)
        total_val += val
        ws.append([
            prod.sku, prod.name, inv.warehouse_id, inv.quantity_on_hand,
            inv.quantity_reserved, (inv.quantity_on_hand - inv.quantity_reserved),
            float(prod.cost_price), val
        ])
    ws.append(["", "", "", "", "", "", "Total:", total_val])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
