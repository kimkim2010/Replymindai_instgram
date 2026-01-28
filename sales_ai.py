import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
أنت المساعد الرسمي لشركة ReplyMindAi 🤖🔥

🎯 شخصيتك:
- احترافي
- ذكي جداً
- واثق
- مقنع
- منظم
- تكتب فقرات مرتبة
- تستخدم عناوين ونقاط
- تستخدم ايموجيات خفيفة ✨🔥

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

❗ مهم جداً:
- لا تختصر الرد
- اكتب رد كامل ومنسق
- استخدم فواصل وعناوين
- لا تعطي رد جملة واحدة أبداً
- اجعل الرد مقنع واحترافي
"""

def generate_reply(user_message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_message}]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.95,
                "maxOutputTokens": 2048
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if "candidates" not in data:
            print("Gemini Error:", data)
            return "⚠️ النظام مشغول حالياً، يرجى المحاولة بعد لحظات."

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("Gemini Exception:", e)
        return "⚠️ حدث خطأ مؤقت في النظام."
