import spacy
from src.graph_db import Neo4jConnector

class GraphRAG:
    def __init__(self):
        self.db = Neo4jConnector()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def query(self, question):
        """
        Simple GraphRAG: Extract entities from question -> Query Graph -> Return Context
        """
        # 1. Extract entities from the question
        doc = self.nlp(question)
        entities = [ent.text for ent in doc.ents]
        
        # Fallback: If no named entities, try noun chunks
        if not entities:
            entities = [chunk.text for chunk in doc.noun_chunks]

        if not entities:
            return "I couldn't identify any specific entities in your question. Try asking about a person, organization, or location."

        results = []
        
        # 2. Query Neo4j for each entity
        for entity in entities:
            # Search for the entity (case-insensitive partial match)
            # Find 1-hop connections
            cypher = """
            MATCH (n:Entity)-[r]-(m:Entity)
            WHERE toLower(n.name) CONTAINS toLower($name)
            RETURN n.name, type(r), m.name
            LIMIT 10
            """
            try:
                with self.db.driver.session() as session:
                    records = session.run(cypher, name=entity)
                    for record in records:
                        results.append(f"{record['n.name']} --[{record['type(r)']}]--> {record['m.name']}")
            except Exception as e:
                return f"Error querying database: {e}"

        # 3. Format Answer
        if not results:
            return f"I found no information about '{', '.join(entities)}' in the knowledge graph."
        
        # Deduplicate results
        unique_results = list(set(results))
        
        response = f"Here is what I found for **{', '.join(entities)}**:\n\n"
        for res in unique_results:
            response += f"- {res}\n"
            
        return response

    def close(self):
        self.db.close()
