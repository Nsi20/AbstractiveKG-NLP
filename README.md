# AbstractiveKG-NLP

**LLM Fine-Tuning & Knowledge Graph Builder**

Transform unstructured text into structured knowledge using state-of-the-art NLP. Now featuring an **Interactive UI** and **GraphRAG** capabilities.

![Architecture](ARCHITECTURE.md)

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

## Features

### 🌟 New in v2.0
- **Interactive Web UI**: Visualize graphs, upload PDFs, and scrape URLs.
- **GraphRAG Chat**: Ask questions to your knowledge graph (e.g., *"What is Elon connected to?"*).
- **Document Support**: Process PDFs and Web URLs directly.

### Core Capabilities
- 📝 **Abstractive Summarization** (BART/T5)
- 🔍 **Named Entity Recognition** (spaCy)
- 🔗 **Relation Extraction** (Dependency Parsing)
- 📊 **Neo4j Integration** (Graph Storage)

## Quick Start

### 1. Prerequisites
- Python 3.9+
- Docker (for Neo4j)

### 2. Installation

```bash
git clone <repo-url>
cd AbstractiveKG-NLP
pip install -e .
python -m spacy download en_core_web_sm
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

### 4. Run the App

**Interactive UI (Recommended)**
```bash
streamlit run app.py
```
*Opens http://localhost:8501*

**CLI Demo**
```bash
python demo.py
```

## Documentation

- **[System Architecture](ARCHITECTURE.md)**: Detailed diagrams and component breakdown.
- **[Docker Troubleshooting](DOCKER_TROUBLESHOOTING.md)**: Fix connection issues.

## Usage Guide

### 1. Explorer Tab
Paste text or upload a document. Click **Process** to generate the graph.
- **Blue Nodes**: Organizations
- **Red Nodes**: People
- **Green Nodes**: Locations/Other

### 2. Chat Tab (GraphRAG)
Ask questions like:
- *"Who is the CEO of Tesla?"*
- *"What missions is NASA working on?"*

### 3. Upload Tab
- **PDF**: Upload any text-heavy PDF.
- **URL**: Paste a link to a news article or blog post.

## Project Structure

```
AbstractiveKG-NLP/
├── src/
│   ├── graph_rag.py       # GraphRAG Engine
│   ├── summarizer.py      # BART/T5
│   ├── ner_re.py          # spaCy Extraction
│   ├── graph_db.py        # Neo4j Connector
│   └── pipeline.py        # Core Logic
├── app.py                 # Streamlit Frontend
├── ARCHITECTURE.md        # System Design
└── docker-compose.yml     # Neo4j Config
```

## License
MIT License

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## Citation

If you use this project, please cite:
```bibtex
@software{abstractivekg_nlp,
  title={AbstractiveKG-NLP: LLM Fine-Tuning \& Knowledge Graph Builder},
  author={Your Name},
  year={2025}
}
```
