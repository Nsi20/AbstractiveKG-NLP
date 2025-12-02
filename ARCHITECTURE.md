# System Architecture

## Overview

AbstractiveKG-NLP is a modular system designed to transform unstructured text into structured knowledge graphs. It combines **Abstractive Summarization** (using Transformers) with **Knowledge Graph Extraction** (NER + Relation Extraction) and provides an interactive **GraphRAG** interface.

## High-Level Architecture

```mermaid
graph TD
    User[User / Streamlit UI] -->|Input Text/PDF/URL| Pipeline[AbstractiveKG Pipeline]
    User -->|Chat Query| GraphRAG[GraphRAG Engine]
    
    subgraph "Core Pipeline"
        Pipeline -->|Raw Text| Summarizer[Summarizer Module<br/>(BART/T5)]
        Summarizer -->|Summary| NER_RE[NER & Relation Extraction<br/>(spaCy)]
        NER_RE -->|Entities & Relations| GraphDB_Connector[Graph DB Connector]
    end
    
    subgraph "Storage"
        GraphDB_Connector -->|Write| Neo4j[(Neo4j Database)]
        GraphRAG -->|Read| Neo4j
    end
    
    subgraph "External Models"
        Summarizer -.->|Load| HuggingFace[Hugging Face Hub]
        NER_RE -.->|Load| SpaCy_Model[spaCy Model]
    end
```

## Component Details

### 1. Frontend (Streamlit UI)
- **File**: `app.py`
- **Responsibilities**:
    - User Input (Text, PDF, URL)
    - Visualization (Interactive Graph using `streamlit-agraph`)
    - Chat Interface (GraphRAG)
    - Session State Management

### 2. Summarization Module
- **File**: `src/summarizer.py`
- **Model**: `facebook/bart-large-cnn` (default)
- **Function**: Compresses long documents into concise summaries to improve graph quality and reduce noise.

### 3. Knowledge Extraction (NER & RE)
- **File**: `src/ner_re.py`
- **Model**: `en_core_web_sm` (spaCy)
- **Function**:
    - **NER**: Identifies entities (PERSON, ORG, GPE, etc.).
    - **Relation Extraction**: Uses dependency parsing to find Subject-Verb-Object triples.

### 4. Graph Database Connector
- **File**: `src/graph_db.py`
- **Technology**: Neo4j (Bolt Protocol)
- **Function**:
    - Manages connection pool.
    - Executes Cypher queries for `MERGE` operations (idempotent writes).
    - Handles connection failures gracefully.

### 5. GraphRAG Engine
- **File**: `src/graph_rag.py`
- **Function**:
    - Translates natural language questions into graph lookups.
    - Currently uses **Keyword-Based Retrieval** (extract entities -> find 1-hop neighbors).
    - Extensible to LLM-based Cypher generation.

## Data Flow

1.  **Ingestion**: Text is loaded from direct input, PDF, or URL.
2.  **Summarization**: BART generates a summary.
3.  **Extraction**: spaCy extracts entities and relations from the *summary*.
4.  **Storage**: Entities and relations are stored in Neo4j.
5.  **Retrieval**: GraphRAG queries Neo4j to answer user questions.

## Directory Structure

```
AbstractiveKG-NLP/
├── src/
│   ├── summarizer.py      # Transformer models
│   ├── ner_re.py          # Entity/Relation extraction
│   ├── graph_db.py        # Neo4j interface
│   ├── graph_rag.py       # Chat/QA logic
│   ├── pipeline.py        # Orchestrator
│   └── data_loader.py     # Utilities
├── app.py                 # Streamlit Frontend
├── demo.py                # CLI Entry point
├── docker-compose.yml     # Infrastructure
└── README.md              # Documentation
```
