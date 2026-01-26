import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# =========================
# 🔐 Environment Variables
# =========================
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")   # EAAG
IG_PAGE_ACCESS_TOKEN = os.environ.get("IG_PAGE_ACCESS_TOKEN")   # IGAA

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

print("VERIFY_TOKEN:", VERIFY_TOKEN)
print("FB TOKEN:", "YES" if FB_PAGE_ACCESS_TOKEN else "NO")
print("IG TOKEN:", "YES" if IG_PAGE_ACCESS_TOKEN else "NO")


# =========================
# 🏠 Home
# =========================
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running 🔥"


# =========================
# 🔎 Webhook Verification
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403


# =========================
# 📩 Webhook Receiver
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    platform = None

    if data.get("object") == "instagram":
        platform = "instagram"

    elif data.get("object") == "page":
        platform = "facebook"

    if not platform:
        return "ignored", 200

    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):

            if "message" in messaging_event and not messaging_event["message"].get("is_echo"):

                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event["message"].get("text")

                if message_text:
                    reply = generate_ai_reply(message_text)
                    send_message(sender_id, reply, platform)

    return "ok", 200


# =========================
# 🤖 OpenAI Reply
# =========================
def generate_ai_reply(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "أنت مساعد ذكي احترافي يرد بأسلوب واثق وجذاب يمثل شركة قوية."
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
# 📤 Send Message
# =========================
def send_message(recipient_id, message_text, platform):

    if platform == "instagram":
        access_token = IG_PAGE_ACCESS_TOKEN
    else:
        access_token = FB_PAGE_ACCESS_TOKEN

    if not access_token:
        print("❌ Missing access token for", platform)
        return

    url = "https://graph.facebook.com/v19.0/me/messages"

    params = {
        "access_token": access_token
    }

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, params=params, json=payload)
    print("Send response:", response.text)


# =========================
# ▶ Run
# =========================
if __name__ == "__main__":
    app.run()
