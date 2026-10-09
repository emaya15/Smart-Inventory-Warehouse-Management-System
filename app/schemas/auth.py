from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, Any
from app.utils.enums import UserRole

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.WAREHOUSE_STAFF
    assigned_warehouse_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def handle_name_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            name_val = values.get("full_name") or values.get("name")
            if name_val:
                values["full_name"] = name_val
                values["name"] = name_val
        return values

    @model_validator(mode="after")
    def validate_name(self) -> "UserRegister":
        name = getattr(self, "name", None)
        full_name = getattr(self, "full_name", None)

        if not full_name and not name:
            raise ValueError("Name is required")

        if not full_name and name:
            self.full_name = name

        return self

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    name: Optional[str] = None
    role: str
    assigned_warehouse_id: Optional[int] = None
    is_active: bool

    @model_validator(mode="before")
    @classmethod
    def populate_user_fields(cls, data: Any) -> Any:
        if hasattr(data, "full_name"):
            # SQLAlchemy model instance
            return {
                "id": data.id,
                "email": data.email,
                "full_name": data.full_name,
                "name": data.full_name,
                "role": data.role.value if hasattr(data.role, "value") else str(data.role),
                "assigned_warehouse_id": data.assigned_warehouse_id,
                "is_active": data.is_active,
            }
        elif isinstance(data, dict):
            if "full_name" in data and not data.get("name"):
                data["name"] = data["full_name"]
            elif "name" in data and not data.get("full_name"):
                data["full_name"] = data["name"]
        return data

    class Config:
        from_attributes = True
