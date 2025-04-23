# 🧠 Entity & Relationship Extraction API

This project exposes an NLP pipeline via a FastAPI server that extracts entities and relationships from text using a hybrid architecture of `spaCy`, `LangChain`, and `pydantic-ai`. Relationship visualizations are available in Neo4j.

---

## 🚀 Project Setup

This project uses [Poetry](https://python-poetry.org/) for dependency and environment management.

### 1. Clone and Setup Environment

```bash
git clone https://github.com/kdubba14/entity-relationship-api.git
cd entity-relationship-api

# Initialize poetry environment
poetry install

# Activate environment
poetry shell
```

### 2. Start FastAPI Server

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

---

## 🔪 How to Test the API

**Base URL:** `http://localhost:8000/`

### Endpoint to Use

```
POST /extract
```

### Content Type

Use `multipart/form-data`

### Example `form-data` Fields:

| Key                   | Type  | Example Value                    |
| --------------------- | ----- | -------------------------------- |
| `file`                | File  | (Upload a `.txt` or `.pdf` file) |
| `configured_entities` | JSON  | `["PERSON", "ORG", "PRODUCT"]`   |
| `threshold`           | Float | `0.65`                           |

You can test this using [Hoppscotch](https://hoppscotch.io) or [Postman](https://www.postman.com).

---

## 🔸 Where to See Data in Neo4j

Once the API extracts relationships, they are pushed to your local or cloud-hosted Neo4j instance.

### Neo4j URL:

```
https://console-preview.neo4j.io/tools/explore
```

### Default Credentials (update if needed):

```
Username: neo4j
Password: password
```

You can use [Neo4j Bloom](https://neo4j.com/bloom/) or Neo4j Desktop to visualize entities and relationships.

---

## ⚙️ Architecture Overview

| Component       | Role                                                              |
| --------------- | ----------------------------------------------------------------- |
| **FastAPI**     | Serves the API endpoints                                          |
| **spaCy**       | Performs Named Entity Recognition with configurable EntityRuler   |
| **LangChain**   | Provides fallback LLM logic for complex or missed relationships   |
| **pydantic-ai** | Ensures structured I/O and validation of model responses          |
| **Neo4j**       | Graph database for storing and visualizing entities/relationships |

---

## 🔧 Optimizations & Future Enhancements

### Current Optimizations:

- 🧍‍♂️ **Fallback LLM Only When Needed**  
  Default to spaCy’s lightweight NER and relationship rules. Only invoke LangChain when spaCy misses or confidence is low.

- ⚡ **Use of pydantic-ai**  
  Validates responses from LLMs to avoid malformed or hallucinated outputs.

### Future Improvements:

- 🧠 **Use REBEL (Relation Extraction By End-to-End Language generation)**  
  Leverage [REBEL model](https://huggingface.co/Babelscape/rebel-large) for faster triple extraction for relationships and define types using LangChain.

- 🛠️ **Parallel Processing & Caching**  
  Use background tasks and intermediate result caching for PDF processing and long texts.

---
