import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    WAREHOUSE_STAFF = "WAREHOUSE_STAFF"

class UnitType(str, enum.Enum):
    PIECE = "Piece"
    BOX = "Box"
    KG = "Kg"
    LITRE = "Litre"

class MovementType(str, enum.Enum):
    PURCHASE_RECEIPT = "Purchase Receipt"
    SALE_DISPATCH = "Sale Dispatch"
    CUSTOMER_RETURN = "Customer Return"
    TRANSFER_OUT = "Transfer Out"
    TRANSFER_IN = "Transfer In"
    ADJUSTMENT = "Adjustment"

class POStatus(str, enum.Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    PARTIALLY_RECEIVED = "Partially Received"
    RECEIVED = "Received"
    CANCELLED = "Cancelled"

class SOStatus(str, enum.Enum):
    DRAFT = "Draft"
    CONFIRMED = "Confirmed"
    PICKED = "Picked"
    PACKED = "Packed"
    DISPATCHED = "Dispatched"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

class ReturnStatus(str, enum.Enum):
    REQUESTED = "Requested"
    INSPECTED = "Inspected"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REFUNDED = "Refunded"

class ReturnCondition(str, enum.Enum):
    GOOD = "Good"
    DAMAGED = "Damaged"

class TransferStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_TRANSIT = "In Transit"
    RECEIVED = "Received"
    CANCELLED = "Cancelled"

class AdjustmentReason(str, enum.Enum):
    DAMAGED = "Damaged"
    LOST = "Lost"
    EXPIRED = "Expired"
    FOUND = "Found"
    COUNT_CORRECTION = "Count Correction"

class AdjustmentStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
