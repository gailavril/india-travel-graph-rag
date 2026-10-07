import re
import json
from pathlib import Path
from src.cypher_generator import generate_cypher
from src.cypher_validator import validate_cypher
from src.graph_retriever import retrieve_graph_data
from src.answer_generator import generate_answer

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "indian_tourism.json"
_DEST_CACHE = {}


def get_destination_cache():
    global _DEST_CACHE
    if not _DEST_CACHE and _DATA_PATH.exists():
        try:
            with open(_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    name = item.get("destination_name", "").strip().lower()
                    if name:
                        _DEST_CACHE[name] = item
        except Exception:
            pass
    return _DEST_CACHE


def clean_text(text):
    if not isinstance(text, str):
        return text
    # Remove raw web citation markers like [web:248]
    text = re.sub(r'\[web:\d+\]', '', text)
    return text.strip()


def normalize_and_enrich_records(results):
    """Normalize keys, remove citations, consolidate duplicates, and ensure descriptions exist."""
    if not results:
        return []

    cache = get_destination_cache()
    normalized = []

    for r in results:
        norm = {}
        for k, v in r.items():
            clean_k = k
            if "." in clean_k:
                clean_k = clean_k.split(".")[-1]

            if isinstance(v, str):
                v = clean_text(v)
            elif isinstance(v, list):
                v = [clean_text(x) if isinstance(x, str) else x for x in v if x is not None]

            if clean_k in ("destination_name", "name", "dest"):
                norm.setdefault("destination", v)
            elif clean_k in ("user_reviews_summary", "summary", "overview"):
                norm.setdefault("description", v)
            elif clean_k == "state_name":
                norm.setdefault("state", v)
            else:
                norm[clean_k] = v

        if "destination" not in norm and "destination_name" in norm:
            norm["destination"] = norm["destination_name"]
        if "description" not in norm and "user_reviews_summary" in norm:
            norm["description"] = norm["user_reviews_summary"]

        normalized.append(norm)

    # Deduplicate and consolidate records by destination
    merged_records = []
    seen = {}
    for rec in normalized:
        dname = rec.get("destination")
        if not dname:
            merged_records.append(rec)
            continue
        if dname in seen:
            existing = seen[dname]
            for k, v in rec.items():
                if k in ("activities", "cuisines", "attractions", "best_seasons", "traveler_types"):
                    cur = existing.setdefault(k, [])
                    if isinstance(cur, str):
                        cur = [cur]
                        existing[k] = cur
                    if isinstance(v, list):
                        for item in v:
                            if item and item not in cur:
                                cur.append(item)
                    elif isinstance(v, str) and v and v not in cur:
                        cur.append(v)
                elif not existing.get(k) and v:
                    existing[k] = v
        else:
            seen[dname] = rec
            merged_records.append(rec)

    # Enrich missing description or coordinates from cache
    for rec in merged_records:
        dname = rec.get("destination", "")
        if not dname:
            continue
        key = dname.strip().lower()
        cached = cache.get(key)
        if not cached:
            for ck, cv in cache.items():
                if ck in key or key in ck:
                    cached = cv
                    break

        if cached:
            if not rec.get("description"):
                rec["description"] = clean_text(cached.get("user_reviews_summary", ""))
            if not rec.get("state") and cached.get("state"):
                rec["state"] = cached["state"]
            if not rec.get("safety_rating") and cached.get("safety_rating"):
                rec["safety_rating"] = cached["safety_rating"]
            if not rec.get("popularity_score") and cached.get("popularity_score"):
                rec["popularity_score"] = cached["popularity_score"]
            if not rec.get("ideal_days") and cached.get("ideal_days"):
                rec["ideal_days"] = cached["ideal_days"]
            if rec.get("latitude") is None and "coordinates" in cached:
                rec["latitude"] = cached["coordinates"].get("latitude")
            if rec.get("longitude") is None and "coordinates" in cached:
                rec["longitude"] = cached["coordinates"].get("longitude")

    return merged_records


def graph_rag(question):

    # -------------------------
    # 1. Generate Cypher
    # -------------------------
    cypher = generate_cypher(question)

    # -------------------------
    # 2. Validate Cypher
    # -------------------------
    validate_cypher(cypher)

    # -------------------------
    # 3. Retrieve from Neo4j
    # -------------------------
    raw_results = retrieve_graph_data(cypher)
    results = normalize_and_enrich_records(raw_results)

    # -------------------------
    # 4. Generate answer
    # -------------------------
    answer = generate_answer(
        question,
        results
    )

    return {
        "question": question,
        "cypher": cypher,
        "results": results,
        "answer": answer
    }


# Backward-compatibility alias
retrieve_for_question = graph_rag