from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables for credentials
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")  # Default to local
USERNAME = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "recommendation")

# Connect to Neo4j
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters={}):
        with self._driver.session() as session:
            return session.run(query, parameters)


# Initialize database connection
db = Neo4jConnection(URI, USERNAME, PASSWORD)