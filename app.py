import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# ========= ENV =========
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")   # EAAG... (Messenger/Page)
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")             # EAAG... (Instagram use case token)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

client = OpenAI(api_key=OPENAI_API_KEY)

GRAPH_VERSION = "v19.0"


@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running 🚀", 200


# ========= Webhook Verify =========
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


# ========= Webhook Receiver =========
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("Incoming:", data)

    obj = data.get("object")

    # ---- Messenger (Facebook Page) ----
    if obj == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    sender_id = messaging_event["sender"]["id"]
                    text = messaging_event["message"]["text"]
                    reply = generate_ai_reply(text)
                    send_messenger(sender_id, reply)

    # ---- Instagram ----
    elif obj == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    sender_id = messaging_event["sender"]["id"]
                    text = messaging_event["message"]["text"]
                    reply = generate_ai_reply(text)
                    send_instagram(sender_id, reply)

    return "ok", 200


# ========= OpenAI Reply =========
def generate_ai_reply(user_message: str) -> str:
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي احترافي يرد بأسلوب واثق، جذاب، ومقنع."},
                {"role": "user", "content": user_message},
            ],
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "صار خطأ مؤقت. جرّب بعد شوي."


# ========= Send to Messenger =========
def send_messenger(recipient_id: str, message_text: str):
    if not FB_PAGE_ACCESS_TOKEN:
        print("Messenger error: FB_PAGE_ACCESS_TOKEN is missing")
        return

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/me/messages"
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}

    r = requests.post(url, params=params, json=payload, timeout=20)
    print("Messenger response:", r.text)


# ========= Send to Instagram =========
def send_instagram(recipient_id: str, message_text: str):
    if not IG_ACCESS_TOKEN:
        print("Instagram error: IG_ACCESS_TOKEN is missing")
        return

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/me/messages"
    params = {"access_token": IG_ACCESS_TOKEN}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}

    r = requests.post(url, params=params, json=payload, timeout=20)
    print("Instagram response:", r.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
