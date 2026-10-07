import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.neo4j_connection import driver


def run_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(
            query,
            parameters or {}
        )
        return [record.data() for record in result]


def get_destinations_by_state(state):
    query = """
    MATCH (d:Destination)-[:IN_STATE]->(s:State)
    WHERE toLower(s.name) = toLower($state)
    RETURN
        d.destination_name AS destination,
        s.name AS state,
        d.popularity_score AS popularity_score,
        d.safety_rating AS safety_rating
    ORDER BY d.popularity_score DESC
    """
    return run_query(
        query,
        {"state": state}
    )


def get_destinations_by_activity(activity):
    query = """
    MATCH (d:Destination)-[:HAS_ACTIVITY]->(a:Activity)
    OPTIONAL MATCH (d)-[:IN_STATE]->(s:State)
    WHERE toLower(a.name) CONTAINS toLower($activity)
    RETURN
        d.destination_name AS destination,
        s.name AS state,
        a.name AS activity,
        d.popularity_score AS popularity_score
    ORDER BY d.popularity_score DESC
    """
    return run_query(
        query,
        {"activity": activity}
    )


def get_destinations_by_traveler_type(traveler_type):
    query = """
    MATCH (d:Destination)-[:SUITABLE_FOR]->(t:TravelerType)
    OPTIONAL MATCH (d)-[:IN_STATE]->(s:State)
    WHERE toLower(t.name) CONTAINS toLower($traveler_type)
    RETURN
        d.destination_name AS destination,
        s.name AS state,
        t.name AS traveler_type,
        d.popularity_score AS popularity_score
    ORDER BY d.popularity_score DESC
    """
    return run_query(
        query,
        {"traveler_type": traveler_type}
    )


def get_destinations_by_attraction(attraction):
    query = """
    MATCH (d:Destination)-[:HAS_ATTRACTION]->(a:Attraction)
    OPTIONAL MATCH (d)-[:IN_STATE]->(s:State)
    WHERE toLower(a.name) CONTAINS toLower($attraction)
    RETURN
        d.destination_name AS destination,
        s.name AS state,
        a.name AS attraction
    ORDER BY d.popularity_score DESC
    """
    return run_query(
        query,
        {"attraction": attraction}
    )


def get_matching_destinations(
    state=None,
    activity=None,
    traveler_type=None
):
    query = """
    MATCH (d:Destination)
    WHERE (
        $state IS NULL
        OR EXISTS {
            MATCH (d)-[:IN_STATE]->(s:State)
            WHERE toLower(s.name) = toLower($state)
        }
    )
    AND (
        $activity IS NULL
        OR EXISTS {
            MATCH (d)-[:HAS_ACTIVITY]->(a:Activity)
            WHERE toLower(a.name) CONTAINS toLower($activity)
        }
    )
    AND (
        $traveler_type IS NULL
        OR EXISTS {
            MATCH (d)-[:SUITABLE_FOR]->(t:TravelerType)
            WHERE toLower(t.name) CONTAINS toLower($traveler_type)
        }
    )
    OPTIONAL MATCH (d)-[:IN_STATE]->(s:State)
    RETURN DISTINCT
        d.destination_name AS destination,
        s.name AS state,
        d.popularity_score AS popularity_score,
        d.safety_rating AS safety_rating,
        d.ideal_days AS ideal_days
    ORDER BY d.popularity_score DESC
    """
    return run_query(
        query,
        {
            "state": state,
            "activity": activity,
            "traveler_type": traveler_type
        }
    )
