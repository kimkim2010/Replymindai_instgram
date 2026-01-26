from flask import Flask, request
import os
import requests
import time
from sales_ai import generate_reply

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

# منع تكرار الأحداث
SEEN = {}
SEEN_TTL = 120


def remember(key):
    now = time.time()
    for k in list(SEEN.keys()):
        if now - SEEN[k] > SEEN_TTL:
            del SEEN[k]

    if key in SEEN:
        return False

    SEEN[key] = now
    return True


# ===============================
# 🏠 Health check
# ===============================
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI Running ✅", 200


# ===============================
# ✅ Webhook Verification
# ===============================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# ===============================
# 📩 Webhook Receiver
# ===============================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True)
    print("🔥 WEBHOOK DATA:", data)

    if not data:
        return "OK", 200

    if data.get("object") != "page":
        return "OK", 200

    for entry in data.get("entry", []):

        # ====== رسائل خاصة ======
        if "messaging" in entry:
            for event in entry["messaging"]:

                if event.get("message", {}).get("is_echo"):
                    continue

                text = event.get("message", {}).get("text")
                sender_id = event.get("sender", {}).get("id")

                if not text or not sender_id:
                    continue

                if not remember(f"dm:{sender_id}:{text}"):
                    continue

                reply = generate_reply(text, channel="dm")
                send_message(sender_id, reply)

        # ====== تعليقات ======
        if "changes" in entry:
            for change in entry["changes"]:

                if change.get("field") != "feed":
                    continue

                value = change.get("value", {})

                comment_id = value.get("comment_id")
                comment_text = value.get("message")
                item = value.get("item")

                # نتأكد أنه تعليق حقيقي
                if item != "comment":
                    continue

                if not comment_id or not comment_text:
                    continue

                if not remember(f"comment:{comment_id}"):
                    continue

                reply = generate_reply(comment_text, channel="comment")
                reply_to_comment(comment_id, reply)

    return "OK", 200


# ===============================
# 📤 Send DM
# ===============================
def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    requests.post(url, params=params, json=payload)


# ===============================
# 💬 Reply to Comment
# ===============================
def reply_to_comment(comment_id, text):
    url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"message": text}

    requests.post(url, params=params, json=payload)
