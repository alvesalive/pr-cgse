from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: UUID
    product_id: str
    product_name: str
    unit_price: float
    quantity: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: UUID
    user_uuid: str
    status: str
    risk_level: Optional[str]
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
