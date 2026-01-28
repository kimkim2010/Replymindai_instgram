from flask import Flask, request
import requests
import os
import threading
import time
from sales_ai import generate_reply

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")


# ===============================
# 🛡️ منع النوم - Self Ping
# ===============================
def keep_alive():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL)
                print("🔥 Self-Ping Sent Successfully")
        except Exception as e:
            print("⚠️ Self-Ping Failed:", e)
        time.sleep(300)


# ===============================
# 🏠 Home (عشان ما يعطي 404)
# ===============================
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI Running 🔥", 200


# ===============================
# ✅ Webhook Verification
# ===============================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook Verified Successfully")
        return challenge, 200
    return "❌ Verification Failed", 403


# ===============================
# 📩 استقبال رسائل Messenger
# ===============================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging in entry.get("messaging", []):
                sender_id = messaging["sender"]["id"]

                if "message" in messaging and "text" in messaging["message"]:
                    user_message = messaging["message"]["text"]
                    print("📩 Incoming Message:", user_message)

                    ai_reply = generate_reply(user_message)
                    send_message(sender_id, ai_reply)

    return "OK", 200


# ===============================
# 🚀 إرسال الرد إلى فيسبوك
# ===============================
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    requests.post(url, json=payload)
    print("💬 Reply Sent Successfully")


# ===============================
# 🏁 تشغيل السيرفر
# ===============================
if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=10000)
