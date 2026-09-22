"""Flask server for the AppleSupport AI agent website."""

from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from src.agent import AppleSupportAgent
from src.database import get_metrics, list_escalations, list_interactions, save_interaction
from src.pipeline import classify_baseline, escalation_baseline
from src.twitter_client import XAPIError, fetch_recent_applesupport_tweets


ROOT = Path(__file__).parent
app = Flask(__name__, template_folder="templates", static_folder="static")
RETRIEVAL_DATA = ROOT / "data" / "apple_support_sample.csv"
retrieval_agent = AppleSupportAgent.from_csv(RETRIEVAL_DATA) if RETRIEVAL_DATA.exists() else None


@app.after_request
def disable_browser_cache(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


def draft_reply(intent: str, escalate: bool) -> str:
    if escalate:
        return (
            "Thanks for letting us know. A specialist should review this securely. "
            "Please do not share passwords, verification codes, or full payment details here."
        )
    replies = {
        "account_access": "Hi there, please visit iforgot.apple.com and follow the account recovery steps. Reply here if you get stuck and we will take a closer look.",
        "billing_refund": "Hi there, please check your purchase history and reply with the date and amount of the charge. For your security, do not share full payment details here.",
        "device_setup": "Hi there, we can help with setup. Please check that your device is connected to Wi-Fi and updated to the latest iOS version, then try the setup steps again.",
        "repair_warranty": "Hi there, please check your coverage at checkcoverage.apple.com, then choose an Apple Store or Apple Authorized Service Provider for an inspection.",
        "order_delivery": "Hi there, please check your order confirmation for the latest tracking link. Reply with your order number if the delivery status has not updated.",
        "store_support": "Hi there, you can find the nearest Apple Store and available appointments at apple.com/retail. Reply here if you need help finding a location.",
        "software_troubleshooting": "Hi there, please check Settings for the relevant device status and make sure your iPhone is updated to the latest iOS version. If the issue continues, reply here and we will take a closer look.",
    }
    return replies.get(intent, "Hi there, thanks for reaching out. Please share a little more detail about the issue and we will help with the next step.")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/support")
def support():
    return render_template("support.html")


@app.get("/questions")
def questions():
    return send_from_directory(ROOT, "customer_questions.md", as_attachment=False)


@app.get("/data/<path:filename>")
def data_file(filename):
    return send_from_directory(ROOT / "data", filename, as_attachment=True)


@app.get("/api/analyze")
def analyze_help():
    return jsonify({
        "message": "Use POST /api/analyze with JSON containing a message.",
        "example": {"message": "My Apple ID is locked"},
    })


@app.get("/api/history")
def history():
    limit = request.args.get("limit", default=50, type=int)
    return jsonify({"interactions": list_interactions(limit)})


@app.get("/api/escalations")
def escalations():
    limit = request.args.get("limit", default=20, type=int)
    return jsonify({"escalations": list_escalations(limit)})


@app.get("/api/metrics")
def metrics():
    return jsonify(get_metrics())


@app.get("/api/live-tweets")
def live_tweets():
    limit = request.args.get("limit", default=10, type=int)
    try:
        return jsonify({"tweets": fetch_recent_applesupport_tweets(limit)})
    except XAPIError as error:
        if error.status_code in (401, 403):
            setup = "Check that the Bearer Token is valid and the X app has Read access to the recent-search endpoint."
        elif error.status_code == 429:
            setup = "X API rate limit reached. Wait and try again later."
        else:
            setup = "Check the X Developer dashboard and API availability."
        return jsonify({"error": str(error), "x_status": error.status_code, "setup": setup}), 502
    except RuntimeError as error:
        return jsonify({"error": str(error), "setup": "Add X_BEARER_TOKEN to the server environment."}), 503
    except Exception:
        return jsonify({"error": "X API request failed"}), 502


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    intent = classify_baseline(message)
    escalate, reason = escalation_baseline(message)
    analysis = retrieval_agent.analyze(message) if retrieval_agent else {
        "reply": draft_reply(intent, escalate),
        "evidence": [],
    }
    reply = analysis["reply"]
    interaction_id = save_interaction(message, intent, escalate, reason, reply)
    return jsonify({
        "id": interaction_id,
        "intent": intent,
        "escalate": escalate,
        "reason": reason,
        "reply": reply,
        "evidence": analysis["evidence"],
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
