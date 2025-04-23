from neo4j import ManagedTransaction

from app.models.entity import MergedEntity
from app.models.relationship import Relationship


def add_data(tx: ManagedTransaction, entities: list[MergedEntity], relationships: list[Relationship]):
    tx.run("MATCH (n) DETACH DELETE n")  # wipe [FOR DEMO PURPOSES]
    print('cleared db')

    for entity in entities:
      tx.run(
        f"MERGE (n:{entity.labels[-1]} {{id: $id, name: $name}})",
        id=entity.id,
        name=entity.text
      )
        
    print('added entities in db')

    for rel in relationships:
      tx.run(
        f"""
          MATCH (a {{id: $from}}), (b {{id: $to}})
          MERGE (a)-[r:{rel.predicate}]->(b)
          SET r += $props
        """, 
        {
          "from": rel.from_id, 
          "to": rel.to_id, 
          "props": {"subject": rel.subject, "object": rel.object, "confidence": rel.confidence},
        }
      )

    print('added relationships to db')