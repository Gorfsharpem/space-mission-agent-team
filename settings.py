# We will most probably move to Pydantic soon
import os

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", 2048))
NO_THINK = os.environ.get("NO_THINK", "0").strip().lower() in ("1", "true", "yes")
