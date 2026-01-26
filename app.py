from flask import Flask, request
import requests
import os
from sales_ai import generate_reply

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")


@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAi is running 🚀🔥"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"].get("text")

                    if user_message:
                        reply = generate_reply(user_message)
                        send_message(sender_id, reply)

    return "OK", 200


def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
