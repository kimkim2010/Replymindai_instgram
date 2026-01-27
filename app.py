import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ====== ENV ======
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# ====== KEEP ALIVE ROUTE ======
@app.route("/")
def home():
    return "🔥 ReplyMind AI is running 24/7"

# ====== FACEBOOK WEBHOOK VERIFY ======
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

# ====== WEBHOOK RECEIVE ======
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):

                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"].get("text")

                    if user_message:
                        print("📩 Incoming:", user_message)

                        ai_reply = generate_reply(user_message)
                        send_message(sender_id, ai_reply)

    return "OK", 200

# ====== AI GENERATOR ======
def generate_reply(user_message):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }

    prompt = f"""
أنت مساعد ذكي احترافي لشركة فاخرة.
رد بأسلوب راقي، مختصر، احترافي.
رسالة العميل: {user_message}
الرد:
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        result = response.json()

        if isinstance(result, list):
            return result[0]["generated_text"].split("الرد:")[-1].strip()

        return "✨ نشكرك على تواصلك، سنعود إليك حالاً."

    except Exception as e:
        print("AI Error:", e)
        return "⚠️ النظام الذكي مشغول حالياً، يرجى المحاولة لاحقاً."

# ====== SEND TO MESSENGER ======
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    requests.post(url, json=payload)

# ====== RUN ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
