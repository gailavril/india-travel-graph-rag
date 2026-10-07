import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


def load_dataset():
    file_path = ROOT_DIR / "data" / "indian_tourism.json"
    if not file_path.exists():
        file_path = ROOT_DIR / "data" / "india_tourism_dataset.json"

    with open(file_path, "r", encoding="utf-8") as file:
        destinations = json.load(file)

    print(f"Loaded {len(destinations)} destinations.")
    return destinations


def create_constraints():
    queries = [
        """
        CREATE CONSTRAINT destination_id_unique IF NOT EXISTS
        FOR (d:Destination)
        REQUIRE d.id IS UNIQUE
        """,
        """
        CREATE CONSTRAINT state_name_unique IF NOT EXISTS
        FOR (s:State)
        REQUIRE s.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT district_name_unique IF NOT EXISTS
        FOR (d:District)
        REQUIRE d.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT region_name_unique IF NOT EXISTS
        FOR (r:Region)
        REQUIRE r.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT activity_name_unique IF NOT EXISTS
        FOR (a:Activity)
        REQUIRE a.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT attraction_name_unique IF NOT EXISTS
        FOR (a:Attraction)
        REQUIRE a.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT trip_type_name_unique IF NOT EXISTS
        FOR (t:TripType)
        REQUIRE t.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT traveler_type_name_unique IF NOT EXISTS
        FOR (t:TravelerType)
        REQUIRE t.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT cuisine_name_unique IF NOT EXISTS
        FOR (c:Cuisine)
        REQUIRE c.name IS UNIQUE
        """,
        """
        CREATE CONSTRAINT season_name_unique IF NOT EXISTS
        FOR (s:Season)
        REQUIRE s.name IS UNIQUE
        """
    ]

    with driver.session() as session:
        for query in queries:
            session.run(query)

    print("Constraints created.")


def create_destination(tx, destination):
    query = """
    MERGE (d:Destination {
        id: $id
    })
    SET
        d.destination_name = $destination_name,
        d.altitude_m = $altitude_m,
        d.popularity_score = $popularity_score,
        d.safety_rating = $safety_rating,
        d.permits_required = $permits_required,
        d.minimum_days = $minimum_days,
        d.ideal_days = $ideal_days,
        d.maximum_days = $maximum_days,

        d.accessibility = $accessibility,
        d.road_connectivity = $road_connectivity,
        d.mobile_network = $mobile_network,
        d.internet_connectivity = $internet_connectivity,
        d.atm_availability = $atm_availability,

        d.food_scene = $food_scene,
        d.local_culture = $local_culture,
        d.local_customs = $local_customs,

        d.safety_notes = $safety_notes,
        d.sustainability_notes = $sustainability_notes,

        d.latitude = $latitude,
        d.longitude = $longitude,

        d.winter_temperature = $winter_temperature,
        d.summer_temperature = $summer_temperature,
        d.monsoon_temperature = $monsoon_temperature,

        d.nearest_airport_name = $nearest_airport_name,
        d.nearest_airport_distance_km = $nearest_airport_distance_km,

        d.nearest_major_city_name = $nearest_major_city_name,
        d.nearest_major_city_distance_km = $nearest_major_city_distance_km,

        d.nearest_railway_station_name = $nearest_railway_station_name,
        d.nearest_railway_station_distance_km = $nearest_railway_station_distance_km,

        d.permits_details = $permits_details,
        d.recent_developments = $recent_developments,
        d.special_considerations = $special_considerations,
        d.user_reviews_summary = $user_reviews_summary,
        d.last_updated = $last_updated
    """

    tx.run(
        query,
        id=destination["id"],
        destination_name=destination["destination_name"],
        altitude_m=destination["altitude_m"],
        popularity_score=destination["popularity_score"],
        safety_rating=destination["safety_rating"],
        permits_required=destination["permits_required"],
        minimum_days=destination["minimum_days"],
        ideal_days=destination["ideal_days"],
        maximum_days=destination["maximum_days"],
        accessibility=destination["accessibility"],
        road_connectivity=destination["road_connectivity"],
        mobile_network=destination["mobile_network"],
        internet_connectivity=destination["internet_connectivity"],
        atm_availability=destination["atm_availability"],
        food_scene=destination["food_scene"],
        local_culture=destination["local_culture"],
        local_customs=destination["local_customs"],
        safety_notes=destination["safety_notes"],
        sustainability_notes=destination["sustainability_notes"],
        latitude=destination["coordinates"]["latitude"],
        longitude=destination["coordinates"]["longitude"],
        winter_temperature=destination["average_temperature"]["winter"],
        summer_temperature=destination["average_temperature"]["summer"],
        monsoon_temperature=destination["average_temperature"]["monsoon"],
        nearest_airport_name=destination["nearest_airport"]["name"],
        nearest_airport_distance_km=destination["nearest_airport"]["distance_km"],
        nearest_major_city_name=destination["nearest_major_city"]["name"],
        nearest_major_city_distance_km=destination["nearest_major_city"]["distance_km"],
        nearest_railway_station_name=destination["nearest_railway_station"]["name"],
        nearest_railway_station_distance_km=destination["nearest_railway_station"]["distance_km"],
        permits_details=destination["permits_details"],
        recent_developments=destination["recent_developments"],
        special_considerations=destination["special_considerations"],
        user_reviews_summary=destination["user_reviews_summary"],
        last_updated=destination["last_updated"]
    )


def create_state(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    MERGE (s:State {name: $state})
    MERGE (d)-[:IN_STATE]->(s)
    """
    tx.run(query, id=destination["id"], state=destination["state"])


def create_district(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    MERGE (district:District {name: $district})
    MERGE (d)-[:IN_DISTRICT]->(district)
    """
    tx.run(query, id=destination["id"], district=destination["district"])


def create_region(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    MERGE (r:Region {name: $region})
    MERGE (d)-[:IN_REGION]->(r)
    """
    tx.run(query, id=destination["id"], region=destination["region"])


def create_activities(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $activities AS activity_name
    MERGE (a:Activity {name: activity_name})
    MERGE (d)-[:HAS_ACTIVITY]->(a)
    """
    tx.run(
        query,
        id=destination["id"],
        activities=destination["activities_available"]
    )


def create_attractions(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $attractions AS attraction_name
    MERGE (a:Attraction {name: attraction_name})
    MERGE (d)-[:HAS_ATTRACTION]->(a)
    """
    tx.run(
        query,
        id=destination["id"],
        attractions=destination["primary_attractions"]
    )


def create_trip_types(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $trip_types AS trip_type
    MERGE (t:TripType {name: trip_type})
    MERGE (d)-[:HAS_TRIP_TYPE]->(t)
    """
    tx.run(
        query,
        id=destination["id"],
        trip_types=destination["trip_types"]
    )


def create_traveler_types(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $traveler_types AS traveler_type
    MERGE (t:TravelerType {name: traveler_type})
    MERGE (d)-[:SUITABLE_FOR]->(t)
    """
    tx.run(
        query,
        id=destination["id"],
        traveler_types=destination["ideal_for"]
    )


def create_cuisines(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $cuisines AS cuisine
    MERGE (c:Cuisine {name: cuisine})
    MERGE (d)-[:HAS_CUISINE]->(c)
    """
    tx.run(
        query,
        id=destination["id"],
        cuisines=destination["local_cuisine_must_try"]
    )


def create_best_seasons(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $seasons AS season_name
    MERGE (s:Season {name: season_name})
    MERGE (d)-[:BEST_IN]->(s)
    """
    tx.run(
        query,
        id=destination["id"],
        seasons=destination["best_seasons"]
    )


def create_avoid_seasons(tx, destination):
    query = """
    MATCH (d:Destination {id: $id})
    UNWIND $seasons AS season_name
    MERGE (s:Season {name: season_name})
    MERGE (d)-[:AVOID_IN]->(s)
    """
    tx.run(
        query,
        id=destination["id"],
        seasons=destination["avoid_seasons"]
    )


def build_graph():
    destinations = load_dataset()
    create_constraints()

    with driver.session() as session:
        for index, destination in enumerate(destinations, start=1):
            print(
                f"Processing {index}/{len(destinations)}: "
                f"{destination['destination_name']}"
            )

            session.execute_write(create_destination, destination)
            session.execute_write(create_state, destination)
            session.execute_write(create_district, destination)
            session.execute_write(create_region, destination)
            session.execute_write(create_activities, destination)
            session.execute_write(create_attractions, destination)
            session.execute_write(create_trip_types, destination)
            session.execute_write(create_traveler_types, destination)
            session.execute_write(create_cuisines, destination)
            session.execute_write(create_best_seasons, destination)
            session.execute_write(create_avoid_seasons, destination)

    print("\nGraph creation completed.")


if __name__ == "__main__":
    try:
        build_graph()
    finally:
        driver.close()