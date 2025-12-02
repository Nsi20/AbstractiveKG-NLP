from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnector:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not uri or not user or not password:
            raise ValueError("Neo4j configuration missing in .env")

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify connection immediately to fail fast
        try:
            self.driver.verify_connectivity()
        except Exception as e:
            self.driver.close()
            raise ConnectionError(f"Failed to connect to Neo4j at {uri}: {e}")

    def close(self):
        self.driver.close()

    def add_entity(self, name, label):
        """
        Add an entity node to the graph.
        """
        with self.driver.session() as session:
            session.execute_write(self._create_and_return_entity, name, label)

    @staticmethod
    def _create_and_return_entity(tx, name, label):
        query = (
            f"MERGE (e:Entity {{name: $name}}) "
            f"ON CREATE SET e.label = $label "
            "RETURN e.name"
        )
        result = tx.run(query, name=name, label=label)
        return result.single()[0]

    def add_relation(self, head, relation, tail):
        """
        Add a relationship between two entities.
        """
        with self.driver.session() as session:
            session.execute_write(self._create_and_return_relation, head, relation, tail)

    @staticmethod
    def _create_and_return_relation(tx, head, relation, tail):
        # Sanitize relation type (Neo4j relationship types cannot have spaces/special chars usually)
        rel_type = relation.upper().replace(" ", "_").replace("-", "_")
        
        query = (
            "MERGE (h:Entity {name: $head}) "
            "MERGE (t:Entity {name: $tail}) "
            f"MERGE (h)-[r:{rel_type}]->(t) "
            "RETURN type(r)"
        )
        result = tx.run(query, head=head, tail=tail)
        return result.single()[0]

    def populate_kg(self, kg_data):
        """
        Populate the graph from extracted KG data.
        kg_data: {'entities': [...], 'relations': [...]}
        """
        # Add entities first (optional, as relations will MERGE them, but good for setting labels)
        for ent in kg_data.get("entities", []):
            self.add_entity(ent["text"], ent["label"])

        # Add relations
        for rel in kg_data.get("relations", []):
            self.add_relation(rel["head"], rel["type"], rel["tail"])
