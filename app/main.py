from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth, categories, products, warehouses, inventory,
    stock_movements, suppliers, purchase_orders, customers,
    sales_orders, returns, transfers, adjustments, audit_logs, reports
)

app = FastAPI(
    title="Smart Inventory & Warehouse Management System",
    version="1.0.0",
    description="Enterprise-grade Backend API with FEFO, Weighted Average Costing, and Multi-Warehouse Tracking"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(inventory.router)
app.include_router(stock_movements.router)
app.include_router(suppliers.router)
app.include_router(purchase_orders.router)
app.include_router(customers.router)
app.include_router(sales_orders.router)
app.include_router(returns.router)
app.include_router(transfers.router)
app.include_router(adjustments.router)
app.include_router(audit_logs.router)
app.include_router(reports.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Smart Inventory & Warehouse Management System"}
