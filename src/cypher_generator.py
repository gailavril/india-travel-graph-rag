GRAPH_SCHEMA = """
Nodes:
- Destination (properties: destination_name, altitude_m, popularity_score, safety_rating, minimum_days, ideal_days, maximum_days, permits_required, accessibility, road_connectivity, mobile_network, internet_connectivity, atm_availability, food_scene, local_culture, local_customs, safety_notes, sustainability_notes, special_considerations, user_reviews_summary, latitude, longitude, winter_temperature, summer_temperature, monsoon_temperature)
- State (property: name)
- District (property: name)
- Region (property: name)
- Activity (property: name)
- Attraction (property: name)
- TripType (property: name)
- TravelerType (property: name)
- Cuisine (property: name)
- Season (property: name)

Relationships:
(Destination)-[:IN_STATE]->(State)
(Destination)-[:IN_DISTRICT]->(District)
(Destination)-[:IN_REGION]->(Region)
(Destination)-[:HAS_ACTIVITY]->(Activity)
(Destination)-[:HAS_ATTRACTION]->(Attraction)
(Destination)-[:HAS_TRIP_TYPE]->(TripType)
(Destination)-[:SUITABLE_FOR]->(TravelerType)
(Destination)-[:HAS_CUISINE]->(Cuisine)
(Destination)-[:BEST_IN]->(Season)
(Destination)-[:AVOID_IN]->(Season)

Note: Connected nodes (State, Activity, Attraction, TravelerType, Cuisine, Season) have their name stored in property `name` (e.g. s.name, a.name, c.name). State name is retrieved via `(d)-[:IN_STATE]->(s:State)` -> `s.name`.
`d.user_reviews_summary` provides a concise short description / overview of what makes the destination unique.
"""
import re
from google import genai
from src.config import GEMINI_API_KEY


def clean_cypher(query: str) -> str:
    """Removes markdown code blocks (e.g. ```cypher ... ```) from the LLM output."""
    query = query.strip()
    match = re.search(r"```(?:cypher)?\s*([\s\S]*?)\s*```", query, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return query


def generate_cypher(question):
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add GEMINI_API_KEY=<your-key> to your .env file."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are an expert Cypher query generator for an Indian tourism knowledge graph.

Graph schema:
{GRAPH_SCHEMA}

User question:
{question}

Rules:

1. Generate only a READ-ONLY Cypher query.

2. Do not use mutating keywords:
   CREATE, MERGE, DELETE, DETACH DELETE, SET, REMOVE, DROP

3. Use only the nodes, relationships, and properties provided in the schema.
   Connected nodes (State, Activity, Attraction, TravelerType, Cuisine, Season) have the property `name`.
   Always use `toLower(...)` with `CONTAINS` or `=` for filtering string matches.

4. Return useful fields for each destination card:
   - Always return:
     d.destination_name AS destination,
     s.name AS state,
     d.safety_rating AS safety_rating,
     d.popularity_score AS popularity_score,
     d.ideal_days AS ideal_days,
     d.user_reviews_summary AS description,
     d.latitude AS latitude,
     d.longitude AS longitude
   - Intelligently retrieve contextual fields tailored to what the user asked:
     * If asking about food / dining / cuisine: include d.food_scene AS food_scene, and optionally collect(DISTINCT c.name)[0..3] AS cuisines
     * If asking about activities / trekking / adventure / sports: include collect(DISTINCT a.name)[0..3] AS activities
     * If asking about sightseeing / attractions: include collect(DISTINCT att.name)[0..3] AS attractions
     * If asking about culture / heritage / history: include d.local_culture AS local_culture
     * If asking about safety / solo travel: include d.safety_notes AS safety_notes
     * If asking about season / weather / timing / monsoon / winter: include collect(DISTINCT season.name) AS best_seasons
     * If asking about tips / crowds / peak time: include d.special_considerations AS special_considerations
     * If asking about traveler type (family, couple, solo, friends): include collect(DISTINCT t.name) AS traveler_types
   - Use `collect(DISTINCT ...)` when joining one-to-many child nodes (e.g. activities, attractions, cuisines) to return one consolidated record per destination.
   - Order by d.popularity_score DESC where appropriate.
   - Limit the results to at most 6 to 8 destinations (e.g. LIMIT 6).

5. Return ONLY the Cypher query. No explanations, no markdown formatting.
"""

    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
    last_err = None

    for model_name in models_to_try:
        try:
            chat = client.chats.create(model=model_name)
            response = chat.send_message(prompt)
            if response.text:
                return clean_cypher(response.text)
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"Failed to generate Cypher with Gemini models: {last_err}")