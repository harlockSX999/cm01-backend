from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from lead_service import create_lead

app = Flask(__name__)
CORS(app)

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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)