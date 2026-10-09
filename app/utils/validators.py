import re
from fastapi import HTTPException, status

def validate_phone(phone: str) -> str:
    if not re.match(r"^\d{10}$", phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be exactly 10 digits"
        )
    return phone

def validate_gst(gst: str) -> str:
    if len(gst) != 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GST number must be exactly 15 characters"
        )
    return gst
