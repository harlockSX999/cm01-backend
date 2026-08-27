from db import get_connection, init_database
from checkout_service import create_checkout_session
from pack_service import generate_pack
from email_service import send_pack_email


def start_checkout(data, success_url, cancel_url):
    """Cree une commande en attente et une session de paiement Stripe."""
    email = str(data.get("email", "")).strip().lower()

    if not email:
        raise ValueError("email_required")

    init_database()

    order_data = {
        "email": email,
        "offer_name": data.get("offer_name", ""),
        "target_client": data.get("target_client", ""),
        "problem": data.get("problem", ""),
        "price": data.get("price", ""),
        "key_arguments": data.get("key_arguments", ""),
    }

    session = create_checkout_session(order_data, success_url, cancel_url)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO orders (
                stripe_session_id, email, offer_name, target_client,
                problem, price, key_arguments, amount_paid, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.id,
                email,
                order_data["offer_name"],
                order_data["target_client"],
                order_data["problem"],
                order_data["price"],
                order_data["key_arguments"],
                3700,
                "pending",
            ),
        )

    return session.url


def handle_payment_success(stripe_session_id):
    """Marque la commande payee, genere le pack, et l'envoie par email.

    Concu pour etre appele plusieurs fois sans effet de bord (idempotent) :
    si la commande est deja livree, ne refait rien.
    """
    with get_connection() as connection:
        order = connection.execute(
            "SELECT * FROM orders WHERE stripe_session_id = ?",
            (stripe_session_id,),
        ).fetchone()

        if not order:
            raise ValueError("order_not_found")

        if order["delivered"]:
            return {"status": "already_delivered", "order_id": order["id"]}

        connection.execute(
            """
            UPDATE orders
            SET status = 'paid', paid_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (order["id"],),
        )

    # La generation IA et l'envoi email se font hors transaction DB
    # pour ne pas bloquer la connexion pendant l'appel reseau.
    try:
        pack_content = generate_pack(dict(order))
        send_pack_email(order["email"], pack_content)

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE orders
                SET delivered = 1, delivered_at = CURRENT_TIMESTAMP, delivery_error = NULL
                WHERE id = ?
                """,
                (order["id"],),
            )

        return {"status": "delivered", "order_id": order["id"]}

    except Exception as exc:
        # Journalisation de l'echec : la commande reste "paid" mais non livree,
        # consultable pour relance manuelle ou retry automatique ulterieur.
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE orders
                SET delivery_error = ?
                WHERE id = ?
                """,
                (str(exc), order["id"]),
            )
        raise
