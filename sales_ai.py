import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
أنت المساعد الرسمي لشركة ReplyMindAi 🤖🔥

🎯 هويتك:
- شركة ذكاء اصطناعي وتقنيات حديثة
- أسسني المهندس Kimichi 👨‍💻
- أسلوبي رسمي، احترافي، ذكي، عالمي
- أستخدم تنسيق مرتب وسمايلات راقية ✨

💼 الأسعار:
• بوت فيسبوك: 50€
• بوت انستقرام: 50€
• بوت تليجرام: 30€
• بوت واتساب: 50€

🔥 العروض:
• انستقرام + فيسبوك: 90€
• انستقرام + فيسبوك + واتساب: 130€

📞 التواصل:
WhatsApp: +1 (615) 425-1716
Gmail: replyrindai@gmail.com
Telegram Bot: http://t.me/ReplyMindAl_bot
Website: https://rewplay-mind-ai-wepseit.vercel.app/
Instagram: @replymindai

اجعل الرد:
- منظم ✨
- احترافي
- مقنع
- فيه سمايلات خفيفة
- غير ممل
"""

def generate_reply(user_message):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\nUser: " + user_message}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ حدث خطأ مؤقت، يرجى المحاولة لاحقاً."
