from src.neo4j_connection import driver


def retrieve_graph_data(
    cypher_query,
    parameters=None
):

    with driver.session() as session:

        result = session.run(
            cypher_query,
            parameters or {}
        )

        records = [
            record.data()
            for record in result
        ]

    return records