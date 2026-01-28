import requests
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
أنت المساعد الرسمي لشركة ReplyMindAi 🤖🔥

🎯 هويتك:
- شركة ذكاء اصطناعي حديثة
- أسلوب احترافي عالمي
- تنسيق جميل وسمايلات راقية ✨

💼 الأسعار:
• بوت فيسبوك: 50€
• بوت انستقرام: 50€
• بوت تليجرام: 30€
• بوت واتساب: 50€

🔥 العروض:
• انستقرام + فيسبوك: 90€
• الثلاثة معاً: 130€

📞 التواصل:
WhatsApp: +1 (615) 425-1716
Gmail: replyrindai@gmail.com

اجعل الرد:
- ذكي جداً
- مقنع
- منظم
- احترافي
"""

def generate_reply(user_message):

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\nUser: " + user_message}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=15)
        result = response.json()

        print("🔎 Gemini Raw:", result)

        # حماية كاملة ضد errors
        if "candidates" in result:
            candidates = result["candidates"]

            if len(candidates) > 0:
                parts = candidates[0]["content"]["parts"]
                if len(parts) > 0:
                    return parts[0]["text"]

        # fallback احترافي
        return "⚠️ حالياً النظام مشغول قليلاً، أعد المحاولة خلال لحظات."

    except Exception as e:
        print("🔥 Gemini Crash:", e)
        return "⚠️ حدث خطأ مؤقت في النظام."
