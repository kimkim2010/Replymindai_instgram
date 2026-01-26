import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# ====== Environment Variables ======
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ====== Home ======
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI Messenger Bot Running 🚀"


# ====== Webhook Verification ======
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


# ====== Webhook Receiver ======
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")

                    if message_text:
                        reply = generate_ai_reply(message_text)
                        send_message(sender_id, reply)

    return "ok", 200


# ====== OpenAI Reply ======
def generate_ai_reply(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "أنت مساعد ذكي احترافي يرد بأسلوب واثق، مختصر، وجذاب."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI error:", e)
        return "حدث خطأ مؤقت، حاول لاحقاً."


# ====== Send Message to Messenger ======
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, json=payload)
    print("Send response:", response.text)


if __name__ == "__main__":
    app.run()
