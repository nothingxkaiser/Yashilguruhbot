import os
import json
import threading
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9189130519:AAEdAW1W9sBVNaRubz9pkKOblehzReTXIJA")
OGRETMEN_ID = 7033815531         # Öğretmenin / senin sayısal ID'n (int)
GRUP_ID = -5527054915         # Sınıf grubunun -100 ile başlayan ID'si (int)
PANEL_URL = "https://yashilguruh-h7bcvxwpz-muhammeds-projects-b354fc35.vercel.app"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Seriye göre unvan hesaplama (en üstte Prime)
def unvon_hisobla(seri: int) -> str:
    if seri >= 20:
        return "Prime"
    if seri >= 14:
        return "Master"
    if seri >= 10:
        return "Titan"
    if seri >= 6:
        return "Vanguard"
    if seri >= 3:
        return "Ranger"
    return "Starter"

@app.route("/")
def ana_sayfa():
    return "Bot ishlayapti!"

def web_sunucu_baslat():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

@bot.message_handler(commands=["start"])
def start_komutu(message):
    if message.from_user.id != OGRETMEN_ID:
        bot.reply_to(message, "Bu bo‘lim faqat o‘qituvchi uchun.")
        return

    klavye = ReplyKeyboardMarkup(resize_keyboard=True)
    web_tugma = KeyboardButton(
        text="📋 5-sinf panelini ochish",
        web_app=WebAppInfo(url=PANEL_URL)
    )
    klavye.add(web_tugma)
    bot.send_message(
        message.chat.id,
        "Nazоrat panelini ochish uchun pastdagi tugmani bosing:",
        reply_markup=klavye
    )

@bot.message_handler(content_types=["web_app_data"])
def panel_verisi_al(message):
    if message.from_user.id != OGRETMEN_ID:
        return

    try:
        veri = json.loads(message.web_app_data.data)
        yozuvlar = veri.get("yozuvlar", {})

        satirlar = ["📊 *5-SINF KUNLIK HISOBOTI*\n"]
        for ism, h in yozuvlar.items():
            otirdi = h.get("yaxshiOtirdi", False)
            vazifa = h.get("uygaVazifaQildi", False)
            seri = int(h.get("seri", 0))
            unvan = unvon_hisobla(seri)

            otirdi_matn = "✅ Yaxshi o‘tirdi" if otirdi else "❌ Yaxshi o‘tirmadi"
            vazifa_matn = "✅ Vazifasini qildi" if vazifa else "❌ Vazifasini qilmadi"

            satirlar.append(
                f"👤 *{ism}* — 🏆 *{unvan}* ({seri} kun)\n"
                f"   • {otirdi_matn}\n"
                f"   • {vazifa_matn}"
            )

        hisobot_matni = "\n\n".join(satirlar)
        bot.send_message(GRUP_ID, hisobot_matni, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Hisobot guruhga yuborildi!")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    threading.Thread(target=web_sunucu_baslat, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
