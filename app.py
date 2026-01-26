import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# =========================
# ENV VARIABLES
# =========================
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
IG_PAGE_ACCESS_TOKEN = os.environ.get("IG_PAGE_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("IG_USER_ID")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# HOME
# =========================
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running 🚀", 200


# =========================
# WEBHOOK VERIFY
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


# =========================
# WEBHOOK RECEIVE
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    # -------- Messenger --------
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event and not event["message"].get("is_echo"):
                    sender_id = event["sender"]["id"]
                    text = event["message"].get("text")

                    if text:
                        reply = generate_ai_reply(text)
                        send_facebook_message(sender_id, reply)

    # -------- Instagram --------
    elif data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event and not event["message"].get("is_echo"):
                    sender_id = event["sender"]["id"]
                    text = event["message"].get("text")

                    if text:
                        reply = generate_ai_reply(text)
                        send_instagram_message(sender_id, reply)

    return "ok", 200


# =========================
# OPENAI RESPONSE
# =========================
def generate_ai_reply(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "أنت مساعد ذكي احترافي يرد بأسلوب واثق وجذاب يعكس قوة شركة تقنية."
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


# =========================
# SEND MESSENGER
# =========================
def send_facebook_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v19.0/me/messages"

    params = {
        "access_token": FB_PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, params=params, json=payload)
    print("Messenger response:", response.text)


# =========================
# SEND INSTAGRAM
# =========================
def send_instagram_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/messages"

    params = {
        "access_token": IG_PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, params=params, json=payload)
    print("Instagram response:", response.text)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
