import os
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================================
# 🔐 Environment Variables
# =========================================
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")

GRAPH_URL = "https://graph.facebook.com/v24.0"

# =========================================
# 🧠 OpenAI Setup
# =========================================
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================
# 🏥 Health Check
# =========================================
@app.route("/", methods=["GET"])
def home():
    return "🔥 ReplyMindAI 24/7 Running", 200


# =========================================
# ✅ Webhook Verification
# =========================================
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        print("✅ Webhook verified")
        return challenge, 200

    print("❌ Verification failed")
    return "Invalid token", 403


# =========================================
# 📩 Webhook Receiver
# =========================================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("📥 Incoming webhook:", data)

    try:
        if data.get("object") != "page":
            return "OK", 200

        for entry in data.get("entry", []):
            if "messaging" in entry:
                for event in entry["messaging"]:

                    if event.get("message", {}).get("is_echo"):
                        continue

                    sender_id = event.get("sender", {}).get("id")
                    message = event.get("message", {})
                    text = message.get("text")

                    if sender_id and text:
                        print(f"💬 New DM: {text}")

                        reply = safe_generate_reply(text)
                        send_message(sender_id, reply)

        return "OK", 200

    except Exception as e:
        print("🔥 Webhook crash prevented:", str(e))
        return "OK", 200   # never return 500


# =========================================
# 🧠 AI Generator (Safe Version)
# =========================================
def safe_generate_reply(user_text):

    fallback = (
        "👋 أهلًا وسهلًا بك في خدمة العملاء\n\n"
        "📌 تم استلام رسالتك بنجاح.\n"
        "لو سمحت اكتب: (سعر / تفاصيل / طلب)\n"
        "وسنخدمك فورًا 🤝"
    )

    if not OPENAI_API_KEY:
        print("⚠️ No OpenAI key set")
        return fallback

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional business assistant."},
                {"role": "user", "content": user_text}
            ],
            timeout=20
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("⚠️ AI error:", str(e))

        # إذا 429 quota
        if "insufficient_quota" in str(e) or "429" in str(e):
            print("🚨 OpenAI quota exceeded")
            return (
                "⚠️ حالياً النظام الذكي غير متاح.\n"
                "يرجى المحاولة لاحقًا أو التواصل مع الإدارة مباشرة."
            )

        return fallback


# =========================================
# 📤 Send Messenger Message
# =========================================
def send_message(recipient_id, text):

    if not PAGE_ACCESS_TOKEN:
        print("❌ Missing PAGE_ACCESS_TOKEN")
        return False

    url = f"{GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "access_token": PAGE_ACCESS_TOKEN
    }

    try:
        r = requests.post(url, json=payload, timeout=15)
        print("📤 Messenger status:", r.status_code)
        print("📨 Messenger response:", r.text)
        return r.status_code == 200

    except Exception as e:
        print("❌ Messenger send error:", str(e))
        return False


# =========================================
# 🚀 Run
# =========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
