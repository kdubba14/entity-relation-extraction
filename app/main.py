from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from contextlib import asynccontextmanager

from app.config import settings
from app.models.api import ExtractionResponse
from app.routers.health import router as health_router
from app.services.langchain import CleanInput, EntityExtractor, RelationshipExtractor, ResponseBuilder, Visualizer

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
  """Setup resources on startup and clean up on shutdown."""

  # Set Anthropic API Key
  app.state.anthropic_key = settings.ANTHROPIC_API_KEY

  yield  # Application runs here

  print("Shutting down app...")

app = FastAPI(title="Entity-Relationship Extractor Service", lifespan=lifespan)

app.include_router(health_router, prefix="/health")

@app.get("/")
def root():
    return {"message": "Service Running!"}

@app.post("/extract", response_model=ExtractionResponse)
async def extract_entities_and_relationships(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    configured_entities: Optional[str] = Form(None),  # Send as JSON string
    threshold: Optional[float] = Form(None),
):
  context = {
      "file": file,
      "text": text,
      "configured_entities": configured_entities,
      "threshold": threshold,
  }

  pipeline = (
    CleanInput()
    | EntityExtractor()
    | RelationshipExtractor()
    | Visualizer()
    | ResponseBuilder()
  )
  
  response = await pipeline.invoke(context)
  
  return response

