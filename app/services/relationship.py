import json
import numpy as np
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from app.models.relationship import Relationship
from app.models.entity import MergedEntity

def find_all_phrase_positions_np(text_words, phrase_words):
  text_array = np.array(text_words)
  phrase_array = np.array(phrase_words)

  matches = []
  window_size = len(phrase_array)

  for i in range(len(text_array) - window_size + 1):
    if np.array_equal(text_array[i:i+window_size], phrase_array):
      matches.append(i)

    return np.array(matches)

def compute_proximity_score_np(text, subject, object_):
  words = text.split()
  total_words = len(words)

  subj_indices = find_all_phrase_positions_np(words, subject.split())
  obj_indices = find_all_phrase_positions_np(words, object_.split())

  if len(subj_indices) == 0 or len(obj_indices) == 0:
    return 0.0

  # Efficient min pairwise distance calculation using broadcasting
  dist_matrix = np.abs(subj_indices[:, None] - obj_indices[None, :])
  min_dist = np.min(dist_matrix)

  # Normalize: closer = higher score
  return round(1 - (min_dist / total_words), 4)

async def extract_relationships(text: str, entities: list[MergedEntity], full_text: str, threshold: float = 0.6) -> list[Relationship]:
  system_prompt=f"""
      You are a full-context multi-entity multi-relationship recognizer.

      Your task is to extract multiple meaningful relationships from the provided text and list of entities and return a list.

      Text: {text}

      Entities: [{[
        entity.model_dump_json()
        for entity in entities
        if entity.text.lower() in text.lower()
      ]}]

      Use the following rules:

      1. Only include entities that are mentioned in the original text and have a relationship.
      2. Extract relationships between entity pairs from the text.
      3. Respond ONLY with a JSON ARRAY. Each item in the array must be a JSON object representing one relationship.
      4. If NO relationships are found, respond with an empty array: `[]`
      5. NEVER return a single object without wrapping it in an array.

      Respond ONLY with an ARRAY of JSON objects. Each object must include:
      - "subject": the relationship subject
      - "predicate": the relationship type
      - "object": the relationship object
      - "from_id": the subject entity's id
      - "to_id": the object entity's id
      - "confidence": the confidence score of the relationship inference

      If no valid relationships are found, return an empty array `[]`. Include all relationships in into an array.

      DO NOT:
      - Add commentary, formatting, or Markdown
      - Modify the provided entities

      Example output:
      [
        {{
          "subject": "Greenfield Tech",
          "predicate": "FOUNDED_IN",
          "from_id": "from-id-123",
          "to_id": "to-id-abc",
          "object": "Shell City",
          "confidence": 0.94
        }},
        {{
          "subject": "Thomas",
          "predicate": "FOUNDED",
          "from_id": "from-id-123abc",
          "to_id": "to-id-abc123",
          "object": "Pearl University",
          "confidence": 0.84
        }}
      ]

      REMEMBER: Output ONLY an ARRAY. DO NOT return commentary, Markdown, or plain text.
      """
  
  def get_entity_id_by_text(search: str) -> str:
    lowered = search.lower()

    for entity in entities:
      label = (entity.text or "").lower()
      if lowered in label:
        return entity.id
    
    return entities[0].id

  agent = Agent(
    'openai:gpt-4o', 
    system_prompt=system_prompt, 
    output_type=str,
    output_retries=2,
    retries=2,
  )
  
  print('getting relationship result')
  result = None
  try:
    result = await agent.run(text, usage_limits=UsageLimits(response_tokens_limit=32000))
  except Exception as e:
    print("Error:", e)

  relationships: list[Relationship] = []
  try:
    data = json.loads(result.output.replace('```', '').replace('```json', '').replace('json', '', 1).strip())
    for item in data:
      relationship = Relationship(**item)
      relationship.predicate = relationship.predicate.replace(' ', '_')
      if relationship.confidence >= (threshold or 0.5):
        relationships.append(relationship)
  except Exception as e:
    # TODO: handle retry
    print("Parsing failed:", e)

  response: list[Relationship] = [
    Relationship(**{
      **rel.model_dump(),
      "from_id": get_entity_id_by_text(rel.subject),
      "to_id": get_entity_id_by_text(rel.object),
      "confidence": (rel.confidence * 0.7) + (0.3 * compute_proximity_score_np(full_text, rel.subject, rel.object))
    })
    for rel in relationships
  ]
  
  return response