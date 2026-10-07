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

from src.graph_queries import (
    get_destinations_by_state,
    get_destinations_by_activity,
    get_destinations_by_traveler_type,
    get_matching_destinations
)


print("\n--- GOA ---")
print(get_destinations_by_state("Goa"))

print("\n--- TREKKING ---")
print(get_destinations_by_activity("trekk"))

print("\n--- PHOTOGRAPHERS ---")
print(get_destinations_by_traveler_type("photographer"))

print("\n--- COMBINED ---")
print(
    get_matching_destinations(
        state="Karnataka",
        activity="trekk",
        traveler_type="photographer"
    )
)
