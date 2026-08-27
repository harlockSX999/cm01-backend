import os

from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

from lead_service import create_lead
from order_service import start_checkout, handle_payment_success
from checkout_service import verify_webhook

app = Flask(__name__)
CORS(app)


def get_base_url():
    return os.getenv("PUBLIC_BASE_URL", request.host_url.rstrip("/"))


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "CM01"
    })


@app.post("/lead")
def new_lead():
    data = request.get_json(silent=True) or {}

    try:
        result = create_lead(data)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "internal_error"}), 500


@app.post("/checkout")
def checkout():
    data = request.get_json(silent=True) or {}
    base_url = get_base_url()

    try:
        checkout_url = start_checkout(
            data,
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/cancel",
        )
        return jsonify({"checkout_url": checkout_url}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "checkout_error", "details": str(exc)}), 500


@app.post("/webhook/stripe")
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = verify_webhook(payload, sig_header)
    except Exception:
        return jsonify({"error": "invalid_webhook"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        try:
            handle_payment_success(session["id"])
        except Exception as exc:
            # On repond 200 quand meme pour eviter que Stripe ne retente en boucle
            # sur une erreur non-transitoire ; l'echec est journalise en base
            # (colonne delivery_error) pour investigation/retry manuel.
            return jsonify({"status": "logged_error", "details": str(exc)}), 200

    return jsonify({"status": "ok"}), 200


@app.get("/success")
def success():
    return send_from_directory(".", "success.html")


@app.get("/cancel")
def cancel():
    return send_from_directory(".", "cancel.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
