import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

RESEND_API_URL = "https://api.resend.com/emails"


def send_pack_email(to_email, pack_content):
    """Envoie le pack de contenu genere par email via Resend."""
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

    if not api_key:
        raise RuntimeError("RESEND_API_KEY_missing")

    html_content = pack_content.replace("\n", "<br>")

    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": "Votre Pack Contenu Commercial CM01 est pret",
        "html": (
            "<p>Merci pour votre achat ! Voici votre pack de contenu commercial "
            "genere sur mesure :</p><hr>" + html_content
        ),
    }

    response = requests.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=30,
    )

    if response.status_code >= 300:
        raise RuntimeError(f"email_send_failed_{response.status_code}: {response.text}")

    return response.json()
