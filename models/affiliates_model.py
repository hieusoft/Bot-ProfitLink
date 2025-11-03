from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AffiliateReferral:
    ref_id: Optional[int] = None
    referrer_id: int = 0
    referred_id: int = 0
    commission_usd: float = 0.0
    status: str = "pending"  
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



@dataclass
class AffiliateWithdrawal:
    withdraw_id: Optional[int] = None
    user_id: int = 0
    amount: float = 0.0
    wallet_address: Optional[str] = None
    status: str = "pending"  # pending | approved | rejected
    tx_hash: Optional[str] = None
    approved_at:Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None