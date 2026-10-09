"""add missing inventory tables

Revision ID: 42e55e95a5fd
Revises: ac69745edc46
Create Date: 2026-10-08 15:00:53.942899
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "42e55e95a5fd"
down_revision: Union[str, Sequence[str], None] = "ac69745edc46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "ADMIN",
                "INVENTORY_MANAGER",
                "WAREHOUSE_STAFF",
                name="userrole",
            ),
            nullable=False,
        ),
        sa.Column("assigned_warehouse_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    # Warehouses table
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("warehouse_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_warehouses_id", "warehouses", ["id"], unique=False)
    op.create_index(
        "ix_warehouses_warehouse_code",
        "warehouses",
        ["warehouse_code"],
        unique=True,
    )

    # Add circular foreign keys after both tables exist
    op.create_foreign_key(
        "fk_users_assigned_warehouse",
        "users",
        "warehouses",
        ["assigned_warehouse_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_warehouses_manager",
        "warehouses",
        "users",
        ["manager_id"],
        ["id"],
    )

    # Audit logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=50), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)

    # Products
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("barcode", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column(
            "unit",
            sa.Enum("PIECE", "BOX", "KG", "LITRE", name="unittype"),
            nullable=False,
        ),
        sa.Column("cost_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("selling_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("reorder_level", sa.Integer(), nullable=False),
        sa.Column("reorder_quantity", sa.Integer(), nullable=False),
        sa.Column("preferred_supplier_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["preferred_supplier_id"], ["suppliers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barcode"),
    )

    op.create_index("ix_products_id", "products", ["id"], unique=False)
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    # Purchase orders
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("po_number", sa.String(length=50), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "APPROVED",
                "PARTIALLY_RECEIVED",
                "RECEIVED",
                "CANCELLED",
                name="postatus",
            ),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_purchase_orders_id", "purchase_orders", ["id"], unique=False)
    op.create_index(
        "ix_purchase_orders_po_number",
        "purchase_orders",
        ["po_number"],
        unique=True,
    )

    # Sales orders
    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("so_number", sa.String(length=50), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("grand_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "CONFIRMED",
                "PICKED",
                "PACKED",
                "DISPATCHED",
                "DELIVERED",
                "CANCELLED",
                name="sostatus",
            ),
            nullable=False,
        ),
        sa.Column("courier_name", sa.String(length=100), nullable=True),
        sa.Column("tracking_number", sa.String(length=100), nullable=True),
        sa.Column("dispatched_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tracking_number"),
    )

    op.create_index("ix_sales_orders_id", "sales_orders", ["id"], unique=False)
    op.create_index(
        "ix_sales_orders_so_number",
        "sales_orders",
        ["so_number"],
        unique=True,
    )

    # Transfers
    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transfer_number", sa.String(length=50), nullable=False),
        sa.Column("source_warehouse_id", sa.Integer(), nullable=False),
        sa.Column("destination_warehouse_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "IN_TRANSIT",
                "RECEIVED",
                "CANCELLED",
                name="transferstatus",
            ),
            nullable=False,
        ),
        sa.Column("dispatched_at", sa.DateTime(), nullable=True),
        sa.Column("received_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["destination_warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["source_warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_transfers_id", "transfers", ["id"], unique=False)
    op.create_index(
        "ix_transfers_transfer_number",
        "transfers",
        ["transfer_number"],
        unique=True,
    )

    # Adjustments
    op.create_table(
        "adjustments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("adjustment_number", sa.String(length=50), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity_delta", sa.Integer(), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "DAMAGED",
                "LOST",
                "EXPIRED",
                "FOUND",
                "COUNT_CORRECTION",
                name="adjustmentreason",
            ),
            nullable=False,
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="adjustmentstatus"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_adjustments_adjustment_number",
        "adjustments",
        ["adjustment_number"],
        unique=True,
    )
    op.create_index("ix_adjustments_id", "adjustments", ["id"], unique=False)

    # Batches
    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_number", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("manufacturing_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "batch_number", name="uq_batch_prod"),
    )

    op.create_index("ix_batches_expiry_date", "batches", ["expiry_date"], unique=False)
    op.create_index("ix_batches_id", "batches", ["id"], unique=False)

    # Inventory
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=False),
        sa.Column("quantity_reserved", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "warehouse_id", name="uq_prod_warehouse"),
    )

    op.create_index("ix_inventory_id", "inventory", ["id"], unique=False)

    # Purchase order items
    op.create_table(
        "purchase_order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity_ordered", sa.Integer(), nullable=False),
        sa.Column("quantity_received", sa.Integer(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_purchase_order_items_id",
        "purchase_order_items",
        ["id"],
        unique=False,
    )

    # Returns
    op.create_table(
        "returns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("return_number", sa.String(length=50), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "REQUESTED",
                "INSPECTED",
                "APPROVED",
                "REJECTED",
                "REFUNDED",
                name="returnstatus",
            ),
            nullable=False,
        ),
        sa.Column("refund_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_returns_id", "returns", ["id"], unique=False)
    op.create_index(
        "ix_returns_return_number",
        "returns",
        ["return_number"],
        unique=True,
    )

    # Sales order items
    op.create_table(
        "sales_order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_sales_order_items_id",
        "sales_order_items",
        ["id"],
        unique=False,
    )

    # Stock movements
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column(
            "movement_type",
            sa.Enum(
                "PURCHASE_RECEIPT",
                "SALE_DISPATCH",
                "CUSTOMER_RETURN",
                "TRANSFER_OUT",
                "TRANSFER_IN",
                "ADJUSTMENT",
                name="movementtype",
            ),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("performed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["performed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_stock_movements_id", "stock_movements", ["id"], unique=False)

    # Transfer items
    op.create_table(
        "transfer_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("received_quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_transfer_items_id",
        "transfer_items",
        ["id"],
        unique=False,
    )

    # Return items
    op.create_table(
        "return_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("return_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column(
            "condition_type",
            sa.Enum("GOOD", "DAMAGED", name="returncondition"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["return_id"], ["returns.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_return_items_id",
        "return_items",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_return_items_id", table_name="return_items")
    op.drop_table("return_items")

    op.drop_index("ix_transfer_items_id", table_name="transfer_items")
    op.drop_table("transfer_items")

    op.drop_index("ix_stock_movements_id", table_name="stock_movements")
    op.drop_table("stock_movements")

    op.drop_index("ix_sales_order_items_id", table_name="sales_order_items")
    op.drop_table("sales_order_items")

    op.drop_index("ix_returns_return_number", table_name="returns")
    op.drop_index("ix_returns_id", table_name="returns")
    op.drop_table("returns")

    op.drop_index("ix_purchase_order_items_id", table_name="purchase_order_items")
    op.drop_table("purchase_order_items")

    op.drop_index("ix_inventory_id", table_name="inventory")
    op.drop_table("inventory")

    op.drop_index("ix_batches_id", table_name="batches")
    op.drop_index("ix_batches_expiry_date", table_name="batches")
    op.drop_table("batches")

    op.drop_index("ix_adjustments_id", table_name="adjustments")
    op.drop_index("ix_adjustments_adjustment_number", table_name="adjustments")
    op.drop_table("adjustments")

    op.drop_index("ix_transfers_transfer_number", table_name="transfers")
    op.drop_index("ix_transfers_id", table_name="transfers")
    op.drop_table("transfers")

    op.drop_index("ix_sales_orders_so_number", table_name="sales_orders")
    op.drop_index("ix_sales_orders_id", table_name="sales_orders")
    op.drop_table("sales_orders")

    op.drop_index("ix_purchase_orders_po_number", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_id", table_name="purchase_orders")
    op.drop_table("purchase_orders")

    op.drop_index("ix_products_sku", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    # Remove circular foreign keys first
    op.drop_constraint(
        "fk_warehouses_manager",
        "warehouses",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_users_assigned_warehouse",
        "users",
        type_="foreignkey",
    )

    op.drop_index("ix_warehouses_warehouse_code", table_name="warehouses")
    op.drop_index("ix_warehouses_id", table_name="warehouses")
    op.drop_table("warehouses")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")