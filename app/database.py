from app.config import settings
from neo4j import GraphDatabase

# Connect to Neo4j
driver = GraphDatabase.driver(settings.DATABASE_URL, auth=(settings.DATABASE_USER, settings.DATABASE_PASSWORD))

