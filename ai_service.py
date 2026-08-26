import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "config" / ".env")

SCORING_PROMPT = BASE_DIR / "ai" / "scoring_prompt.txt"

def score_lead(lead):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY_missing")

    client = OpenAI(api_key=api_key)
    system_prompt = SCORING_PROMPT.read_text(encoding="utf-8")

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=system_prompt,
        input=json.dumps(lead, ensure_ascii=False)
    )

    text = response.output_text

    score = 0
    priority = "FAIBLE"
    segment = "UNKNOWN"

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("SCORE:"):
            try:
                score = int(line.split(":", 1)[1].strip())
            except ValueError:
                score = 0
        elif line.startswith("PRIORITY"):
            priority = line.split(":", 1)[1].strip()
        elif line.startswith("SEGMENT:"):
            segment = line.split(":", 1)[1].strip()

    score = max(0, min(100, score))

    return {
        "score": score,
        "priority": priority,
        "segment": segment
    }
