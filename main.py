import telebot

TOKEN = "7971999489:AAFKum1c8R963uF4YbJzwbYt9ZQZoOiwWLo"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot ishlayapti ✅")

bot.polling()
