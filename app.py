import os
from collections import defaultdict

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/analytics": {"origins": "*"}}, allow_headers=["Content-Type", "X-API-Key"], methods=["POST", "OPTIONS"])

API_KEY = os.environ.get("API_KEY", "")
USER_EMAIL = os.environ.get("USER_EMAIL", "")

@app.route("/analytics", methods=["POST", "OPTIONS"])
def analytics():
    if request.method == "OPTIONS":
        return ("", 204)

    supplied_key = request.headers.get("X-API-Key", "")
    if not API_KEY or supplied_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        return jsonify({"error": "Request body must contain an events array"}), 400

    events = payload["events"]
    users = set()
    positive_totals = defaultdict(float)
    revenue = 0.0

    for event in events:
        if not isinstance(event, dict):
            continue
        user = event.get("user")
        if user is not None:
            users.add(user)
        amount = event.get("amount", 0)
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0.0
        if amount > 0:
            revenue += amount
            if user is not None:
                positive_totals[user] += amount

    top_user = max(positive_totals, key=positive_totals.get) if positive_totals else None

    return jsonify({
        "email": USER_EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": revenue,
        "top_user": top_user
    })

@app.get("/")
def health():
    return "Analytics API is running. Send POST requests to /analytics.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
