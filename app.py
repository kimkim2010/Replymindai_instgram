import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# ====== ENV VARIABLES ======
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

print("VERIFY_TOKEN:", VERIFY_TOKEN)
print("PAGE_ACCESS_TOKEN موجود؟", "YES" if PAGE_ACCESS_TOKEN else "NO")

# ====== OpenAI ======
client = OpenAI(api_key=OPENAI_API_KEY)


# ====== HOME ======
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running 🚀"


# ====== WEBHOOK VERIFICATION ======
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


# ====== RECEIVE MESSAGES ======
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):

                # تجاهل الرسائل المرتدة من البوت نفسه
                if (
                    "message" in messaging_event
                    and not messaging_event["message"].get("is_echo")
                ):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")

                    if message_text:
                        reply = generate_ai_reply(message_text)
                        send_message(sender_id, reply)

    return "ok", 200


# ====== OPENAI REPLY ======
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


# ====== SEND MESSAGE TO INSTAGRAM ======
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


# ====== RUN ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
