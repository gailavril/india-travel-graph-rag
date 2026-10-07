FORBIDDEN_KEYWORDS = [
    "CREATE",
    "MERGE",
    "DELETE",
    "DETACH DELETE",
    "SET",
    "REMOVE",
    "DROP"
]


def validate_cypher(query):

    upper_query = query.upper()

    for keyword in FORBIDDEN_KEYWORDS:

        if keyword in upper_query:

            raise ValueError(
                f"Unsafe Cypher detected: {keyword}"
            )

    return True