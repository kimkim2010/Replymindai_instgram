import os
import requests
from flask import Flask, request, jsonify
from sales_ai import sales_ai

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

# ======================================
# Webhook Verification
# ======================================
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Verification token mismatch", 403


# ======================================
# Handle Incoming Messages
# ======================================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for message_event in entry["messaging"]:
                    if "message" in message_event and "text" in message_event["message"]:

                        sender_id = message_event["sender"]["id"]
                        user_message = message_event["message"]["text"]

                        response_text = sales_ai(user_message)
                        send_message(sender_id, response_text)

    return "ok", 200


# ======================================
# Send Message Function
# ======================================
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)


# ======================================
# Keep Alive Route (لمنع النوم)
# ======================================
@app.route("/")
def home():
    return "ReplyMindAI is running 24/7 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
