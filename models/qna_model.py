from dataclasses import dataclass
from datetime import datetime
from typing import Optional
@dataclass
class QnA_Category:
    category_id: Optional[int] = None
    category_name: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
@dataclass
class QnA:
    qna_id: Optional[int] = None
    question: str = ""
    answer: str = ""
    category_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None