from typing import Optional
from pydantic import BaseModel

from app.models.entity import MergedEntity
from app.services.relationship import Relationship


class ExtractionRequest(BaseModel):
  text: str
  configured_entities: Optional[list[str]] = ["PRODUCT", "FEATURE", "CUSTOM_BRAND", "JOB", "TECHNOLOGY"]
  threshold: Optional[float]

class ExtractionResponse(BaseModel):
  entities: list[MergedEntity]
  relationships: list[Relationship]