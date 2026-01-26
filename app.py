import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")


# 🔹 الصفحة الرئيسية
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running 🚀"


# 🔹 التحقق من الويبهوك (Meta verification)
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


# 🔹 استقبال الرسائل
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")

                    if message_text:
                        reply = generate_ai_reply(message_text)
                        send_message(sender_id, reply)

    return "ok", 200


# 🔹 توليد رد من OpenAI
def generate_ai_reply(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "أنت مساعد ذكي احترافي يرد بأسلوب واثق، جذاب، ومقنع ويعكس عقلية شركة قوية."
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
        return "حدث خطأ مؤقت، حاول مرة أخرى لاحقاً."


# 🔹 إرسال الرسالة للانستغرام
def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, params=params, json=payload)
    print("Send response:", response.text)


if __name__ == "__main__":
    app.run()
