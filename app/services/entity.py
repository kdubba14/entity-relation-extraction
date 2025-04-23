import spacy
from pydantic_ai import Agent

from app.models.entity import Entity

nlp = spacy.load("en_core_web_lg")

def extract_entities_from_spacy(text: str) -> list[Entity]:
  doc = nlp(text)
  return [
    Entity(text=ent.text, label=ent.label_, source="spacy")
    for ent in doc.ents
  ]

async def extract_entities_from_llm(text: str, labels: list[str], pre_found: list[Entity]) -> list[Entity]:
  system_prompt = f"""
    You are a full-context strict named entity recognizer.

    Your task is to extract every entity from the provided text. You are also given a list of pre-found entities from another extractor.

    Use the following rules:

    1. Only include entities with a label that exactly matches one of these allowed labels: {labels}

    2. From the original text, extract any new entities that match those labels.

    3. Also if they could be additionally labeled by the allowed labels, include any of the provided pre-found entities: {pre_found}

    Respond ONLY with a JSON array of objects. Each object must include:
    - "text": the entity span
    - "label": one of the allowed labels
    - "source": must be either `"document"` (for newly extracted) or `"pre_found"` (for reused ones)

    If no valid entities are found, return an empty list `[]`.

    DO NOT:
    - Add entities with labels not in the allowed list
    - Add commentary, formatting, or Markdown
    - Modify the provided pre_found entities

    Example output:
    [
      {{"text": "Apple", "label": "ORG", "source": "document"}},
      {{"text": "iPhone 15", "label": "PRODUCT", "source": "document"}}
    ]
  """

  agent = Agent(
    'anthropic:claude-3-5-haiku-latest', 
    system_prompt=system_prompt, 
    output_type=list[Entity],
    retries=2
  )
  
  result = await agent.run(text)
  return result.output
