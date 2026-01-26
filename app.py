from flask import Flask, request
import os
import requests
import threading
import time
from sales_ai import generate_reply

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# منع تكرار معالجة نفس الحدث
SEEN = {}
SEEN_TTL = 120  # ثواني

def remember(key: str) -> bool:
    """يرجع True إذا هذه أول مرة نشوف الحدث، False إذا مكرر"""
    now = time.time()
    # تنظيف قديم
    for k, ts in list(SEEN.items()):
        if now - ts > SEEN_TTL:
            SEEN.pop(k, None)
    if key in SEEN:
        return False
    SEEN[key] = now
    return True


# ===============================
# 🛡️ Keep Alive (Self Ping)
# ===============================
def keep_alive():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL, timeout=10)
        except:
            pass
        time.sleep(300)  # كل 5 دقائق


# ===============================
# 🏠 Home (لتفادي 404 + صحة السيرفر)
# ===============================
@app.route("/", methods=["GET"])
def home():
    return "ReplyMindAI running ✅", 200


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
# 📩 Webhook Receiver (DM + Comments)
# ===============================
print("🔥 WEBHOOK DATA:", data)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    if data.get("object") != "page":
        return "OK", 200

    for entry in data.get("entry", []):

        # ====== DM (Messenger Inbox) ======
        if "messaging" in entry:
            for event in entry.get("messaging", []):

                # تجاهل echoes
                if event.get("message", {}).get("is_echo"):
                    continue

                msg = event.get("message", {})
                text = msg.get("text")
                if not text:
                    continue

                sender_id = event.get("sender", {}).get("id")
                mid = msg.get("mid", f"{sender_id}:{hash(text)}")

                if not sender_id:
                    continue

                if not remember(f"dm:{mid}"):
                    continue

                ai_reply = generate_reply(text, channel="dm")
                send_message(sender_id, ai_reply)

        # ====== Comments (Feed) ======
        if "changes" in entry:
            for change in entry.get("changes", []):
                if change.get("field") != "feed":
                    continue

                value = change.get("value", {})
                item = value.get("item")

                # نرد فقط على التعليقات
                if item != "comment":
                    continue

                comment_id = value.get("comment_id")
                comment_text = value.get("message")

                if not comment_id or not comment_text:
                    continue

                if not remember(f"comment:{comment_id}"):
                    continue

                ai_reply = generate_reply(comment_text, channel="comment")
                reply_to_comment(comment_id, ai_reply)

    return "OK", 200


# ===============================
# 📤 Send DM (Messenger)
# ===============================
def send_message(recipient_id: str, text: str):
    if not PAGE_ACCESS_TOKEN:
        return

    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}

    try:
        requests.post(url, params=params, json=payload, timeout=20)
    except:
        pass


# ===============================
# 💬 Reply to Comment (Facebook)
# ===============================
def reply_to_comment(comment_id: str, message_text: str):
    if not PAGE_ACCESS_TOKEN:
        return

    url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"message": message_text}

    try:
        requests.post(url, params=params, json=payload, timeout=20)
    except:
        pass


# ===============================
# ▶ Run
# ===============================
if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
