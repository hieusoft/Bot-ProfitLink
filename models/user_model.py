from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    language: str = "en"
    ref_by: Optional[int] = None
    wallet_address: Optional[str] = None
    verified_kol: str ="not_submitted"
    commission_percent: float = 30.0
    is_banned: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
