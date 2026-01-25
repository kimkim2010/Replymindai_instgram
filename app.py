from flask import Flask, request
import os
import requests
from openai import OpenAI

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running 😈🔥"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]

                if "message" in messaging_event:
                    message_text = messaging_event["message"].get("text")

                    if message_text:
                        ai_reply = generate_ai_reply(message_text)
                        send_message(sender_id, ai_reply)

    return "EVENT_RECEIVED", 200


def generate_ai_reply(user_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "انت موظف مبيعات ذكي جدا لشركة ReplyMindAI. رد بطريقة احترافية ومقنعة."},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content


def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
