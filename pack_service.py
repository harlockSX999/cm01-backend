import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

PACK_PROMPT = BASE_DIR / "pack_prompt.txt"


def generate_pack(order):
    """Genere le pack de contenu commercial via OpenAI a partir des infos de commande."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY_missing")

    client = OpenAI(api_key=api_key)
    system_prompt = PACK_PROMPT.read_text(encoding="utf-8")

    input_data = (
        f"Nom de l'offre : {order.get('offer_name', '')}\n"
        f"Client cible : {order.get('target_client', '')}\n"
        f"Probleme principal resolu : {order.get('problem', '')}\n"
        f"Prix : {order.get('price', '')}\n"
        f"Arguments cles : {order.get('key_arguments', '')}"
    )

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=system_prompt,
        input=input_data,
    )

    return response.output_text
