"""Flask server for the AppleSupport AI agent website."""

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from src.pipeline import classify_baseline, escalation_baseline


ROOT = Path(__file__).parent
app = Flask(__name__, template_folder="templates", static_folder="static")


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


@app.get("/api/analyze")
def analyze_help():
    return jsonify({
        "message": "Use POST /api/analyze with JSON containing a message.",
        "example": {"message": "My Apple ID is locked"},
    })


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    intent = classify_baseline(message)
    escalate, reason = escalation_baseline(message)
    return jsonify({
        "intent": intent,
        "escalate": escalate,
        "reason": reason,
        "reply": draft_reply(intent, escalate),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
