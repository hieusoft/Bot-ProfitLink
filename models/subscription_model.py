from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SubscriptionPlan:
    plan_id: Optional[int] = None
    name: str = ""
    price: float = 0.0
    duration_days: int = 0
    is_active: bool = True
    sale_percent: float = 0.0
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Subscription:
    sub_id: Optional[int] = None
    user_id: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    trial: bool = False
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SubscriptionDetail:
    detail_id: Optional[int] = None
    sub_id: int = 0
    plan_id: int = 0
    payment_id: Optional[int] = None
    activated_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    renewed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None