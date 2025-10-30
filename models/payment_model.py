from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Payment:
    payment_id: Optional[int] = None
    user_id: int = 0
    plan_id: Optional[int] = None
    order_id: Optional[str] = None
    amount: float = 0.0
    currency: str = "USDT"
    method: str = "OxaPay"
    status: str = "pending"  # 'pending', 'success', 'failed'
    merchant_id: Optional[str] = None
    track_id: Optional[str] = None
    expired_at: Optional[int] = None       # lưu timestamp
    invoice_date: Optional[int] = None     # lưu timestamp
    completed_at: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
