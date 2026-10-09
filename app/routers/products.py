from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse
from app.schemas.common import APIResponse
from app.services.product_service import create_product, update_product, soft_delete_product
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("", response_model=APIResponse, status_code=201)
def create_products(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    prod = create_product(db, data, user.id)
    return APIResponse(message="Product created", data=ProductResponse.model_validate(prod))

@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 50,
    sku: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    q = db.query(Product).filter(Product.is_active == True)
    if sku:
        q = q.filter(Product.sku.contains(sku))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    return q.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_details(product_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    total_on_hand = sum(i.quantity_on_hand for i in prod.inventories)
    total_avail = sum((i.quantity_on_hand - i.quantity_reserved) for i in prod.inventories)
    wh_stock = [{"warehouse_id": i.warehouse_id, "on_hand": i.quantity_on_hand, "reserved": i.quantity_reserved} for i in prod.inventories]
    resp = ProductDetailResponse.model_validate(prod)
    resp.total_stock_on_hand = total_on_hand
    resp.total_stock_available = total_avail
    resp.warehouse_stock = wh_stock
    return resp

@router.put("/{product_id}", response_model=APIResponse)
def update_products(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    prod = update_product(db, product_id, data, user.id)
    return APIResponse(message="Product updated", data=ProductResponse.model_validate(prod))

@router.delete("/{product_id}", response_model=APIResponse)
def delete_products(
    product_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    soft_delete_product(db, product_id, user.id)
    return APIResponse(message="Product deactivated successfully")
