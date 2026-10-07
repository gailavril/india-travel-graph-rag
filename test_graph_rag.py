from src.graph_rag import graph_rag


question = """
Which destinations in Karnataka
are good for trekking?
"""


result = graph_rag(question)

print("\n--- CYPHER ---")
print(result["cypher"])

print("\n--- RESULTS ---")
for item in result["results"]:
    print(item)

print("\n--- FINAL ANSWER ---")
print(result["answer"])