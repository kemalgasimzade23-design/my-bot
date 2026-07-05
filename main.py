import os
from flask import Flask
from threading import Thread
import telebot
import random
import time

# --- НАСТРОЙКА ВЕБ-СЕРВЕРА ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Лоли жива и работает 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

# Запуск сервера в отдельном потоке
t = Thread(target=run)
t.start()

# --- КОД ТВОЕГО БОТА ---
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

users_data = {}

def init_user(user_id):
    if user_id not in users_data:
        users_data[user_id] = {"coins": 0, "tag": "", "last_work": 0, "used_promo": False}

def get_user_mention(m):
    init_user(m.from_user.id)
    user_tag = users_data[m.from_user.id]["tag"]
    name = f"@{m.from_user.username}" if m.from_user.username else m.from_user.first_name
    if user_tag:
        return f"[{user_tag}] {name}"
    return name

@bot.message_handler(commands=['start'])
def start_command(m):
    bot.reply_to(m, "Привет, я твой помощник Лоли! 🥳")

@bot.message_handler(commands=['help'])
def help_command(m):
    help_text = (
        "📋 **Список доступных команд:**\n\n"
        "🔹 `/start` — Запустить бота\n"
        "🔹 `/help` — Показать это меню\n"
        "🔹 `лоли` — Проверить, в сети ли бот\n"
        "🔹 `инфа [текст]` — Узнать вероятность чего-либо\n"
        "🔹 `лоли кто [текст]` — Выбрать случайного юзера\n\n"
        "💰 **Экономика чата:**\n"
        "🔹 `ферма` — Собрать монеты (раз в 4 часа)\n"
        "🔹 `кошелек` — Посмотреть свой баланс\n"
        "🔹 `лоли магазин` — Купить тег [Крутой] за 100 монет\n"
        "🔹 `промокод [код]` — Активировать секретный промокод"
    )
    bot.reply_to(m, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text.lower() == 'лоли')
def loli_command(m):
    mention = get_user_mention(m)
    bot.reply_to(m, f"✅ {mention} на месте!")

@bot.message_handler(func=lambda m: m.text.lower() == 'ферма')
def farm_command(m):
    user_id = m.from_user.id
    init_user(user_id)
    current_time = time.time()
    cooldown = 14400 

    if current_time - users_data[user_id]["last_work"] < cooldown:
        left_seconds = int(cooldown - (current_time - users_data[user_id]["last_work"]))
        hours = left_seconds // 3600
        minutes = (left_seconds % 3600) // 60
        bot.reply_to(m, f"⏳ Ваша ферма еще отдыхает! Приходите через {hours} ч. {minutes} мин.")
        return

    earned = random.randint(1, 100)
    users_data[user_id]["coins"] += earned
    users_data[user_id]["last_work"] = current_time
    mention = get_user_mention(m)
    bot.reply_to(m, f"🌾 {mention}, ферма принесла вам прибыль! Начислено: {earned} монет! 🪙")

@bot.message_handler(func=lambda m: m.text.lower() == 'кошелек')
def wallet_command(m):
    user_id = m.from_user.id
    init_user(user_id)
    mention = get_user_mention(m)
    bot.reply_to(m, f"💳 Кошелек {mention}:\nВаш баланс: {users_data[user_id]['coins']} монет 🪙")

@bot.message_handler(func=lambda m: m.text.lower().startswith('промокод'))
def promo_command(m):
    user_id = m.from_user.id
    init_user(user_id)
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(m, "❌ Вы не ввели промокод!")
        return
    user_code = parts[1].strip()

    if user_code == "LOLIADMINCODE1":
        if users_data[user_id]["used_promo"]:
            bot.reply_to(m, "❌ Вы уже активировали этот промокод!")
            return
        users_data[user_id]["coins"] += 1000
        users_data[user_id]["used_promo"] = True
        bot.reply_to(m, "🎁 АДМИНСКИЙ КОД АКТИВИРОВАН! Вам начислено 1000 монет! 🪙")
    else:
        bot.reply_to(m, "❌ Такого промокода не существует!")

@bot.message_handler(func=lambda m: m.text.lower() == 'лоли магазин')
def shop_command(m):
    user_id = m.from_user.id
    init_user(user_id)
    if users_data[user_id]["coins"] < 100:
        bot.reply_to(m, "❌ Недостаточно монет!")
        return
    users_data[user_id]["coins"] -= 100
    users_data[user_id]["tag"] = "Крутой"
    mention = get_user_mention(m)
    bot.reply_to(m, f"🎉 Поздравляем! Тег куплен!\nТеперь вы: {mention}")

@bot.message_handler(func=lambda m: m.text.lower().startswith('лоли инфа') or m.text.lower().startswith('инфа'))
def info_command(m):
    percent = random.randint(0, 100)
    mention = get_user_mention(m)
    bot.reply_to(m, f"🤔 {mention} Я думаю, что вероятность {percent}%")

@bot.message_handler(func=lambda m: m.text.lower().startswith('лоли кто'))
def who_is_command(m):
    text_parts = m.text.split(maxsplit=2)
    question = text_parts[2] if len(text_parts) > 2 else "тут кто-то странный"
    try:
        chat_admins = bot.get_chat_administrators(m.chat.id)
        random_admin = random.choice(chat_admins)
        chosen_user = random_admin.user
        user_mention = f"@{chosen_user.username}" if chosen_user.username else chosen_user.first_name
    except Exception:
        chosen_user = m.from_user
        user_mention = f"@{chosen_user.username}" if chosen_user.username else chosen_user.first_name
    bot.send_message(m.chat.id, f"🔮 Ясно вижу, что {user_mention} {question}")

print("Бот готов к деплою на Render!")
bot.infinity_polling()