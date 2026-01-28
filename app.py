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
# 🔥 منع النوم - Self Ping
# ===============================
def keep_alive():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL)
                print("🔥 Self-Ping Sent")
        except Exception as e:
            print("⚠️ Ping Error:", e)
        time.sleep(300)


# ===============================
# 🏠 Home Route
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
        print("✅ Webhook Verified")
        return challenge, 200

    return "Verification Failed", 403


# ===============================
# 📩 Messenger Webhook
# ===============================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging in entry.get("messaging", []):
                    sender_id = messaging["sender"]["id"]

                    if "message" in messaging and "text" in messaging["message"]:
                        user_message = messaging["message"]["text"]
                        print("📩 Incoming:", user_message)

                        ai_reply = generate_reply(user_message)

                        send_message(sender_id, ai_reply)

        return "OK", 200

    except Exception as e:
        print("🔥 Webhook Fatal Error:", e)
        return "OK", 200  # مهم جداً حتى ما يصير 500


# ===============================
# 🚀 Send Message
# ===============================
def send_message(recipient_id, message_text):
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }

        requests.post(url, json=payload)
        print("💬 Reply Sent")

    except Exception as e:
        print("❌ Facebook Send Error:", e)


# ===============================
# 🏁 Run Server
# ===============================
if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=10000)
