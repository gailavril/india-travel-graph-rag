from google import genai

from src.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(
    question,
    graph_results
):

    prompt = f"""
You are an Indian tourism assistant.

Answer the user's question using
the retrieved knowledge graph results.

User question:

{question}


Knowledge graph results:

{graph_results}


Rules:

- Use the retrieved information.
- Do not invent destinations.
- Do not add unsupported facts.
- Give a clear and concise answer.
"""
    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]
    last_err = None

    for model_name in models_to_try:
        try:
            chat = client.chats.create(model=model_name)
            response = chat.send_message(prompt)
            if response.text:
                return response.text.strip()
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"Failed to generate answer with Gemini models: {last_err}")