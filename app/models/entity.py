from pydantic import BaseModel


class Entity(BaseModel):
  text: str
  label: str
  source: str

class MergedEntity(BaseModel):
  id: str
  text: str
  labels: list[str]