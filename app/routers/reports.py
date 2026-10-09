from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.report import DashboardResponse, LowStockItem
from app.services.report_service import get_dashboard_metrics, get_low_stock_report, generate_stock_excel
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from typing import List

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return get_dashboard_metrics(db)

@router.get("/low-stock", response_model=List[LowStockItem])
def get_low_stock(
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return get_low_stock_report(db)

@router.get("/export/stock")
def export_stock(
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    excel_stream = generate_stock_excel(db)
    return Response(
        content=excel_stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stock_valuation.xlsx"}
    )
