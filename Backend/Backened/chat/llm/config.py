# Centralised Settings for LLM operations
# Written by Vishay Chotai

import os

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_EXTRACTION = os.getenv("OPENAI_MODEL_EXTRACTION", "gpt-4o-mini")
OPENAI_MODEL_CHAT = os.getenv("OPENAI_MODEL_CHAT", "gpt-4o-mini")
REQUEST_TIMEOUT_S = float(os.getenv("LLM_TIMEOUT", "20"))  # timeout in 20 seconds of LLM not responding to chat queries

# API Team to update @suhas
API_BASE_URL = os.getenv("API_BASE_URL", "https://localhost:8000")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT", "/api/search")