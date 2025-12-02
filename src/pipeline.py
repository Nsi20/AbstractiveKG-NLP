from src.summarizer import Summarizer
from src.ner_re import KGExtractor
from src.graph_db import Neo4jConnector

class AbstractiveKGPipeline:
    def __init__(self):
        print("Initializing Pipeline...")
        self.summarizer = Summarizer()
        self.kg_extractor = KGExtractor()
        try:
            self.db_connector = Neo4jConnector()
            self.db_connected = True
        except Exception as e:
            print(f"Warning: Could not connect to Neo4j: {e}")
            self.db_connected = False

    def process(self, text):
        print("\n--- Step 1: Abstractive Summarization ---")
        summary = self.summarizer.generate_summary(text)
        print(f"Summary: {summary}")

        print("\n--- Step 2: Knowledge Graph Extraction ---")
        # Extract from the original text OR the summary. 
        # Using summary might be cleaner for the graph, using original text gives more detail.
        # Let's use the Summary for the KG to keep it 'Abstractive' and concise.
        kg_data = self.kg_extractor.extract_kg(summary)
        print(f"Extracted {len(kg_data['entities'])} entities and {len(kg_data['relations'])} relations.")

        if self.db_connected:
            print("\n--- Step 3: Graph Database Storage ---")
            self.db_connector.populate_kg(kg_data)
            print("Data stored in Neo4j.")
        else:
            print("\n--- Step 3: Skipped (No DB Connection) ---")

        return summary, kg_data

    def close(self):
        if self.db_connected:
            self.db_connector.close()
