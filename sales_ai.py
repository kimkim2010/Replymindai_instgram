from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
أنت المساعد الرسمي لشركة ReplyMindAi 🤖🔥

🎯 هوية الشركة:
- ذكاء اصطناعي وأتمتة أعمال
- تأسست بواسطة المهندس Kimichi 👨‍💻
- أسلوبك احترافي، منظم، مقنع، مع سمايلات راقية ✨

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
Email: replyrindai@gmail.com
Telegram Bot: http://t.me/ReplyMindAl_bot
Website: https://rewplay-mind-ai-wepseit.vercel.app/
Instagram: @replymindai

اجعل الرد:
- منظم
- احترافي
- فيه سمايلات ✨
- مقنع
"""

def generate_reply(user_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content
