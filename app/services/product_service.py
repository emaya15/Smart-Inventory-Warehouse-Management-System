from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.audit_service import log_audit

def create_product(db: Session, data: ProductCreate, user_id: int) -> Product:
    if data.selling_price < data.cost_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selling price cannot be less than cost price")
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product SKU already exists")
    if data.barcode and db.query(Product).filter(Product.barcode == data.barcode).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product Barcode already exists")
    cat = db.query(Category).filter(Category.id == data.category_id, Category.is_active == True).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid active category id")
    
    prod = Product(**data.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    log_audit(db, user_id, "CREATE", "Product", prod.id, None, data.model_dump())
    db.commit()
    return prod

def update_product(db: Session, product_id: int, data: ProductUpdate, user_id: int) -> Product:
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    update_data = data.model_dump(exclude_unset=True)
    if "selling_price" in update_data or "cost_price" in update_data:
        cost = update_data.get("cost_price", float(prod.cost_price))
        selling = update_data.get("selling_price", float(prod.selling_price))
        if selling < cost:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selling price cannot be less than cost price")
    
    if "is_active" in update_data and update_data["is_active"] is False:
        total_stock = sum([inv.quantity_on_hand for inv in prod.inventories])
        if total_stock > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate product with existing stock")

    old_val = {"name": prod.name, "cost_price": float(prod.cost_price), "selling_price": float(prod.selling_price)}
    for k, v in update_data.items():
        setattr(prod, k, v)
    
    log_audit(db, user_id, "UPDATE", "Product", prod.id, old_val, update_data)
    db.commit()
    db.refresh(prod)
    return prod

def soft_delete_product(db: Session, product_id: int, user_id: int):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    total_stock = sum([inv.quantity_on_hand for inv in prod.inventories])
    if total_stock > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete product with existing inventory")
    prod.is_active = False
    log_audit(db, user_id, "DELETE", "Product", prod.id)
    db.commit()
