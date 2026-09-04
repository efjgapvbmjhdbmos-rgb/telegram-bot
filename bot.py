import telebot
from yt_dlp import YoutubeDL
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import os
import io
import requests
import qrcode
from flask import Flask
import threading
import textwrap

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
user_photos = {}

def hdr_filter(image):
    image = ImageEnhance.Contrast(image).enhance(1.4)
    image = ImageEnhance.Color(image).enhance(1.3)
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    return image

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "اهلا بيك! ابعتلي صورة عشان تعدلها 🔥")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image = Image.open(io.BytesIO(downloaded_file))
    user_photos[chat_id] = image
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔥 HDR ايفون 17", callback_data="hdr"))
    bot.send_message(chat_id, "اختار فلتر:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id in user_photos:
        image = user_photos[chat_id]
        if call.data == "hdr":
            image = hdr_filter(image)
        
        image.save('final.jpg', quality=95)
        bot.send_photo(chat_id, open('final.jpg', 'rb'))

threading.Thread(target=run_flask).start()
bot.polling(none_stop=True)