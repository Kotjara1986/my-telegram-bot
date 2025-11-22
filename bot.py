import requests
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import os
from dotenv import load_dotenv
# ============================================================
# НАСТРОЙКИ
# ============================================================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") #"8527967929:AAGWpCv_ca2PTu-wqtiz071h0aloOMgS4wA"
OPENWEATHER_TOKEN = "133afef43b141bc548780200f95db1dc"

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

# ============================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================
main_menu = ReplyKeyboardMarkup(
    [
        ["🌦 Погода", "💰 Криптовалюта"],
        ["🔮 Гороскоп", "😂 Анекдот"]
    ],
    resize_keyboard=True
)

# ============================================================
# СТАРТ
# ============================================================
def start(update, context):
    update.message.reply_text(
        "👋 Привет! Я твой многофункциональный бот.\n"
        "Выбери действие:",
        reply_markup=main_menu
    )

# ============================================================
# ПОГОДА
# ============================================================
def weather(update, context):
    city = "Riga"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_TOKEN}&units=metric&lang=ru"

    try:
        data = requests.get(url).json()

        temp = data['main']['temp']
        feels = data['main']['feels_like']
        desc = data['weather'][0]['description']

        text = (
            f"🌦 **Погода в Риге**\n\n"
            f"🌡 Температура: *{temp}°C*\n"
            f"🤔 Ощущается как: *{feels}°C*\n"
            f"☁ Состояние: *{desc}*"
        )

        update.message.reply_markdown(text)

    except:
        update.message.reply_text("❌ Не удалось получить погоду.")

# ============================================================
# АНЕКДОТ
# ============================================================
def joke(update, context):
    try:
        data = requests.get("https://v2.jokeapi.dev/joke/Any?lang=ru").json()

        if data["type"] == "single":
            text = data["joke"]
        else:
            text = data["setup"] + "\n\n" + data["delivery"]

        update.message.reply_text(f"😂 *Анекдот:*\n\n{text}", parse_mode="Markdown")

    except:
        update.message.reply_text("❌ Анекдот сейчас недоступен.")

# ============================================================
# КРИПТА
# ============================================================
def crypto(update, context):
    coins = ["bitcoin", "ethereum", "dao-maker", "avalanche-2", "solana"]
    params = {"ids": ",".join(coins), "vs_currencies": "usd"}

    try:
        data = requests.get(COINGECKO_URL, params=params).json()

        text = (
            "💰 *Курсы криптовалют:*\n\n"
            f"₿ Bitcoin (BTC): *{data['bitcoin']['usd']}$*\n"
            f"Ξ Ethereum (ETH): *{data['ethereum']['usd']}$*\n"
            f"DAO Maker (DAO): *{data['dao-maker']['usd']}$*\n"
            f"Avalanche (AVAX): *{data['avalanche-2']['usd']}$*\n"
            f"Solana (SOL): *{data['solana']['usd']}$*"
        )

        update.message.reply_markdown(text)

    except:
        update.message.reply_text("❌ Не удалось получить курс криптовалют.")

# ============================================================
# INLINE-КНОПКИ ДЛЯ ГОРОСКОПА
# ============================================================
signs = [
    "овен","телец","близнецы","рак","лев","дева",
    "весы","скорпион","стрелец","козерог","водолей","рыбы"
]

def horoscope(update, context):
    keyboard = []
    row = []

    # формируем сетку 3×4
    for i, s in enumerate(signs):
        row.append(InlineKeyboardButton(s.title(), callback_data=f"hs_{s}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    update.message.reply_text(
        "🔮 Выбери свой знак зодиака:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================================
# ОБРАБОТКА INLINE — ГОРОСКОПА
# ============================================================
def handle_inline(update, context):
    query = update.callback_query
    query.answer()

    if query.data.startswith("hs_"):
        sign = query.data.replace("hs_", "")

        try:
            url = f"https://horoskopos.ru/api/horoscope/today/{sign}"
            data = requests.get(url).json()

            text = data.get("text", "Гороскоп недоступен.")

            query.edit_message_text(
                text=f"🔮 *Гороскоп для {sign.title()}:*\n\n{text}",
                parse_mode="Markdown"
            )

        except:
            query.edit_message_text("❌ Ошибка при получении гороскопа.")

# ============================================================
# ОБРАБОТЧИК ТЕКСТА МЕНЮ
# ============================================================
def text_handler(update, context):
    msg = update.message.text.lower()

    if "погода" in msg:
        return weather(update, context)
    elif "крипт" in msg:
        return crypto(update, context)
    elif "анек" in msg:
        return joke(update, context)
    elif "гороскоп" in msg:
        return horoscope(update, context)
    else:
        update.message.reply_text("Выбери действие из меню:", reply_markup=main_menu)

# ============================================================
# ЗАПУСК
# ============================================================
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_inline))
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()



