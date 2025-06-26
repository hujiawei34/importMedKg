# importMedKg

A Python-based system that imports structured Chinese medical knowledge from JSON files into a Neo4j graph database, creating a comprehensive medical knowledge graph with diseases, symptoms, treatments, and their relationships.

## Features

- Import Chinese medical knowledge (orthopedic diseases) from JSON into Neo4j
- Create structured graph relationships between medical entities
- Containerized Neo4j deployment with custom configuration
- Support for complex medical terminology and relationships
- Batch processing with error handling and logging

## Project Structure

```
├── src/
│   ├── import_knowledge_graph.py  # Main import script
│   └── requirements.txt           # Python dependencies
├── kg/
│   └── 骨科学ks.json             # Sample orthopedic knowledge data
├── docker-compose.yml             # Neo4j service definition
├── Dockerfile                     # Neo4j container setup
├── neo4j.conf                    # Database configuration
├── start.sh                      # Start Neo4j container
└── stop.sh                       # Stop Neo4j container
```

## Quick Start

1. **Start Neo4j database:**
   ```bash
   ./start.sh
   ```

2. **Install Python dependencies:**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

3. **Import knowledge graph:**
   ```bash
   python import_knowledge_graph.py
   ```

4. **Access Neo4j browser:**
   Open http://localhost:37474 in your browser
   - Username: `neo4j`
   - Password: `neo4j@gkry`

5. **Stop the database:**
   ```bash
   ./stop.sh
   ```

## Data Model

The system creates the following node types:
- **Disease** - Medical conditions
- **Symptom/Sign** - Clinical manifestations
- **Medication** - Drug treatments
- **Surgery** - Surgical procedures
- **Department** - Medical departments
- **Location** - Body parts/regions

And relationships such as:
- `HAS_SYMPTOM` - Disease to symptoms
- `TREATED_WITH_MEDICATION` - Disease to medications
- `HAS_CAUSE` - Disease to causes
- `REQUIRES_EXAMINATION` - Disease to diagnostic methods

## Requirements

- Docker and Docker Compose
- Python 3.x
- Neo4j Python driver (see requirements.txt)

## Configuration

Neo4j runs on:
- **Browser**: http://localhost:37474
- **Bolt**: bolt://localhost:37687
- **Admin**: http://localhost:36362