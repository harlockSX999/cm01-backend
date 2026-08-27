import os
from pathlib import Path

import stripe
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRODUCT_NAME = "Pack Contenu Commercial IA"
PRICE_EUR = 3700  # 37.00 EUR en centimes


def create_checkout_session(order_data, success_url, cancel_url):
    """Cree une session Stripe Checkout et retourne son URL."""
    if not stripe.api_key:
        raise RuntimeError("STRIPE_SECRET_KEY_missing")

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        customer_email=order_data.get("email"),
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": PRODUCT_NAME,
                    "description": "Page de vente + 5 emails + 10 posts reseaux, generes par IA",
                },
                "unit_amount": PRICE_EUR,
            },
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "offer_name": order_data.get("offer_name", ""),
            "target_client": order_data.get("target_client", ""),
            "problem": order_data.get("problem", ""),
            "price": order_data.get("price", ""),
            "key_arguments": order_data.get("key_arguments", ""),
        },
    )

    return session


def verify_webhook(payload, sig_header):
    """Verifie la signature du webhook Stripe et retourne l'evenement."""
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET_missing")

    event = stripe.Webhook.construct_event(
        payload, sig_header, webhook_secret
    )

    return event
