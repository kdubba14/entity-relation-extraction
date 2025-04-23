from collections import defaultdict
import uuid
from langchain_core.runnables import Runnable
from fastapi import UploadFile, HTTPException
from langchain_core.runnables import Runnable
from typing import Optional, Union, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
import pdfplumber
import json

from app.database import driver
from app.models.api import ExtractionRequest, ExtractionResponse
from app.models.entity import Entity, MergedEntity
from app.models.relationship import Relationship
from app.services.entity import extract_entities_from_llm, extract_entities_from_spacy
from app.services.neo4j import add_data
from app.services.relationship import extract_relationships
from app.services.util import clean_text


class CleanInput(Runnable):
    def invoke(
        self,
        input: Dict[str, Union[UploadFile, str, float, None]],
        config=None,
        **kwargs,
    ) -> ExtractionRequest:
        file = input.get("file")
        text = input.get("text")
        configured_entities = input.get("configured_entities")
        threshold = input.get("threshold")
        print('Getting the clean input')

        if file and file.filename.endswith(".pdf"):
            with pdfplumber.open(file.file) as pdf:
                extracted_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif text:
            extracted_text = text
        else:
            raise HTTPException(status_code=400, detail="Must provide either text or PDF file.")

        try:
            entities_list = json.loads(configured_entities) if configured_entities else None
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="configured_entities must be a valid JSON array.")
        
        cleaned_text = clean_text(extracted_text)

        return ExtractionRequest(
            text=cleaned_text,
            configured_entities=entities_list,
            threshold=threshold,
        )

class EntityExtractor(Runnable):
    async def invoke(self, input: ExtractionRequest, config=None, **kwargs) -> dict:
        entity_map = defaultdict(set)

        spacy_splitter = RecursiveCharacterTextSplitter(
          chunk_size=700,
          chunk_overlap=150,
          separators=["\n\n", "\n", ".", " ", ""]
        )
        spacy_chunks = spacy_splitter.split_text(input.text)

        llm_splitter = RecursiveCharacterTextSplitter(
          chunk_size=10000,
          chunk_overlap=500,
          separators=["\n\n", "\n", ".", " ", ""]
        )
        llm_chunks = llm_splitter.split_text(input.text)

        spacy_ents: list[Entity] = []
        llm_ents: list[Entity] = []

        for chunk in spacy_chunks:
          print(f'Adding spacy chunk - total {len(spacy_chunks)}')
          spacy_ents.extend(extract_entities_from_spacy(chunk))
        
        for chunk in llm_chunks:
          print(f'Adding llm chunk - total {len(llm_chunks)}')
          temp_llm_ents = await extract_entities_from_llm(chunk, input.configured_entities, pre_found=spacy_ents)
          llm_ents.extend(temp_llm_ents)
        
        for ent in [*spacy_ents, *llm_ents]:
          entity_map[ent.text].add(ent.label)

        merged_entities: list[MergedEntity] = [MergedEntity(id=str(uuid.uuid4()), text=text, labels=list(labels)) for text, labels in entity_map.items()]
        return {**input.model_dump(), "text": input.text, "entities": merged_entities}
    
class RelationshipExtractor(Runnable):
    async def invoke(self, context: dict, config=None, **kwargs) -> dict:
        ctx = await context
        relationship_splitter = RecursiveCharacterTextSplitter(
          chunk_size=10000,
          chunk_overlap=400,
          separators=["\n\n", "\n", ".", " ", ""]
        )
        relationship_chunks = relationship_splitter.split_text(ctx["text"])

        relationships: list[Relationship] = []

        for chunk in relationship_chunks:
          temp_relationships = await extract_relationships(chunk, ctx["entities"], full_text=ctx["text"], threshold=ctx["threshold"])
          relationships.extend(temp_relationships)

        return {**ctx, "relationships": relationships}
    
class Visualizer(Runnable):
  async def invoke(self, context: dict, config=None, **kwargs) -> dict:
    ctx = await context
    with driver.session() as session:
      session.execute_write(add_data, ctx["entities"], ctx["relationships"])
    
    print('Data successfully added to the database')
    return { **ctx }
    
class ResponseBuilder(Runnable):
    async def invoke(self, context: dict, config=None, **kwargs) -> ExtractionResponse:
        ctx = await context
        return ExtractionResponse(
            entities=ctx["entities"],
            relationships=ctx["relationships"]
        )