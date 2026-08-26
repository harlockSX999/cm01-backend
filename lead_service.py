from db import get_connection, init_database
from ai_service import score_lead

def create_lead(data):
    email = str(data.get("email", "")).strip().lower()

    if not email:
        raise ValueError("email_required")

    init_database()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM leads WHERE email = ? AND converted = 0",
            (email,)
        ).fetchone()

        if existing:
            return {
                "status": "duplicate",
                "lead_id": existing["id"]
            }

        scoring = score_lead(data)

        cursor = connection.execute(
            """
            INSERT INTO leads (
                first_name, last_name, email, phone,
                company, source, message, status,
                score, segment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("first_name"),
                data.get("last_name"),
                email,
                data.get("phone"),
                data.get("company"),
                data.get("source"),
                data.get("message"),
                "new",
                scoring["score"],
                scoring["segment"]
            )
        )

        lead_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO events (lead_id, event_type, details)
            VALUES (?, ?, ?)
            """,
            (lead_id, "lead_created", "CM01 new lead")
        )

        return {
            "status": "created",
            "lead_id": lead_id,
            "score": scoring["score"],
            "priority": scoring["priority"],
            "segment": scoring["segment"]
        }