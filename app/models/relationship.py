from typing import Optional
from pydantic import BaseModel


class Relationship(BaseModel):
  subject: Optional[str] = None
  predicate: Optional[str] = None
  object: Optional[str] = None
  from_id: Optional[str] = None
  to_id: Optional[str] = None
  confidence: Optional[float] = None  # optional scoring