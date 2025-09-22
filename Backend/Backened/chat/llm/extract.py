from typing import Dict, Any
from .types import ExtractionResult, Location
from .config import OPENAI_API_KEY, OPENAI_MODEL_EXTRACTION, REQUEST_TIMEOUT_S

import json
import requests  # fallback if you’re calling a gateway; otherwise use the SDK

SYSTEM = """You extract structured fields from short user queries for AU mental-health provider search.
Rules:
- intent is "search" if the user seems to look for providers; otherwise "guide and chat".
- specialisation must be one of the controlled set if obvious; else null.
- location: prefer suburb + state if present; else null.
- radius_km: integer; default 15 if missing.
Return ONLY JSON.
Controlled specialisations (sample): ["CBT","Trauma","EMDR","Child Psychology","Anxiety","Depression","ADHD","Autism","Couples Therapy","Psychiatrist","Psychologist"]
"""

USER_TEMPLATE = """Query: {q}
Output JSON schema:
{{
  "intent": "search|chat",
  "specialisation": "string|null",
  "location": {{"suburb":"string|null","state":"string|null","lat":null,"lon":null}} | null,
  "radius_km": 5|10|15|20|25|50,
  "flags": ["telehealth?","urgent?","youth?"]  // optional hints
}}
"""

def extract(q: str) -> ExtractionResult:
    # Minimal robust JSON-mode style prompting via SDK (pseudo). Replace with client.chat.completions if you prefer.
    # Here we'll simulate a local rule-based fallback + LLM hook point.
    # ---- SIMPLE heuristic fallback (works offline) ----
    s = None
    ql = q.lower()
    spec_map = {
        "cbt": "CBT", "trauma": "Trauma", "emdr": "EMDR",
        "child": "Child Psychology", "autism": "Autism",
        "adhd": "ADHD", "anxiety": "Anxiety", "depression": "Depression",
        "couple": "Couples Therapy", "psychiat": "Psychiatrist", "psycholog": "Psychologist"
    }
    for k, v in spec_map.items():
        if k in ql:
            s = v
            break

    # crude AU suburb/state detection; API team can later supply a /locations endpoint for canonicalisation
    state_candidates = ["VIC","NSW","QLD","WA","SA","TAS","ACT","NT"]
    found_state = next((st for st in state_candidates if f" {st.lower()}" in f" {ql} "), None)
    # tiny suburb heuristic
    loc = None
    for token in ["carlton", "brunswick", "fitzroy", "geelong", "st kilda", "richmond", "melbourne"]:
        if token in ql:
            loc = Location(suburb=token.title(), state="VIC" if not found_state else found_state)
            break

    intent = "search" if any(w in ql for w in ["near", "in ", "around", "find", "looking for", "therap", "psych"]) else "chat"

    return ExtractionResult(
        intent=intent,
        specialisation=s,
        location=loc,
        radius_km=15,
        flags=["telehealth"] if "telehealth" in ql or "online" in ql else []
    )