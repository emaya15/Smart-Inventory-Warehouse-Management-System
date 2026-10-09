from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.schemas.common import APIResponse
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.utils.validators import validate_phone
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("", response_model=APIResponse, status_code=201)
def create_customers(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    validate_phone(data.phone)
    if db.query(Customer).filter(Customer.customer_code == data.customer_code).first():
        raise HTTPException(status_code=409, detail="Customer code exists")
    cust = Customer(**data.model_dump())
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return APIResponse(message="Customer created", data=CustomerResponse.model_validate(cust))

@router.get("", response_model=List[CustomerResponse])
def list_customers(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Customer).all()
