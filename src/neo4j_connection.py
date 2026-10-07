import sys
from pathlib import Path

# Ensure project root is in sys.path when running script directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from neo4j import GraphDatabase
from src.config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD
)


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def verify_connection():

    with driver.session() as session:

        result = session.run(
            "RETURN 'Neo4j connection successful' AS message"
        )

        record = result.single()

        print(record["message"])


if __name__ == "__main__":
    verify_connection()