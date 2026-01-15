# ================== SOZLAMALAR ==================
import os
import telebot
from telebot import types

# ================= SOZLAMALAR =================

TOKEN = os.getenv("TOKEN")   # 🔥 FAQAT ENV NOMI
ADMIN_ID = 5938434244

if not TOKEN:
    raise ValueError("TOKEN topilmadi (ENV)")

bot = telebot.TeleBot(TOKEN)

# ================== KATALOG ==================
CATALOG = {
    "🔩 Furnitura": {
        "🔧 Sharner": [
            {
                "id": "sharner_autsite",
                "name": "Sharner Autsite",
                "price": 7000,
                "photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtSm6VPb1AtXVFEv7ttL9kffuxe0QkuK3D3FaBkfHDYg&s=10"
            }
        ]
    }
}

# ================== MA’LUMOTLAR ==================
user_cart = {}        # {chat_id: [product]}
orders = []           # barcha buyurtmalar

# ================== START ==================
@bot.message_handler(commands=['start'])
def start(message):
    kb = types.InlineKeyboardMarkup()
    for cat in CATALOG.keys():
        kb.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.send_message(message.chat.id, "📂 Kategoriyani tanlang:", reply_markup=kb)

# ================== KATEGORIYA ==================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_products(call):
    cat_name = call.data.replace("cat_", "")
    products = CATALOG[cat_name]["🔧 Sharner"]

    for p in products:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🛒 Savatchaga qo‘shish", callback_data=f"add_{p['id']}"))
        bot.send_photo(
            call.message.chat.id,
            p["photo"],
            caption=f"📦 <b>{p['name']}</b>\n💰 Narx: <b>{p['price']} so‘m</b>",
            parse_mode="HTML",
            reply_markup=kb
        )

# ================== SAVATCHAGA QO‘SHISH ==================
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_to_cart(call):
    chat_id = call.message.chat.id
    product_id = call.data.replace("add_", "")

    for cat in CATALOG.values():
        for group in cat.values():
            for p in group:
                if p["id"] == product_id:
                    user_cart.setdefault(chat_id, []).append(p)

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📦 Savatchani ko‘rish", callback_data="cart"))
    bot.send_message(chat_id, "✅ Savatchaga qo‘shildi", reply_markup=kb)

# ================== SAVATCHA ==================
@bot.callback_query_handler(func=lambda call: call.data == "cart")
def show_cart(call):
    chat_id = call.message.chat.id
    items = user_cart.get(chat_id, [])

    if not items:
        bot.send_message(chat_id, "Savatcha bo‘sh ❌")
        return

    text = "🛒 <b>Savatchangiz:</b>\n"
    total = 0
    for p in items:
        text += f"• {p['name']} — {p['price']} so‘m\n"
        total += p["price"]

    text += f"\n<b>Jami:</b> {total} so‘m"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📞 Telefonni yuborish", request_contact=True))

    bot.send_message(chat_id, text, parse_mode="HTML")
    bot.send_message(chat_id, "Buyurtmani yakunlash uchun telefon yuboring:", reply_markup=kb)

# ================== CONTACT ==================
@bot.message_handler(content_types=['contact'])
def finish_order(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    phone = message.contact.phone_number
    items = user_cart.get(chat_id, [])

    total = sum(p["price"] for p in items)

    order = {
        "name": name,
        "phone": phone,
        "items": items,
        "total": total
    }
    orders.append(order)

    order_text = ""
    for p in items:
        order_text += f"• {p['name']} — {p['price']} so‘m\n"

    bot.send_message(chat_id, "✅ Buyurtma qabul qilindi!", reply_markup=types.ReplyKeyboardRemove())

    bot.send_message(
        ADMIN_ID,
        f"📥 <b>YANGI BUYURTMA</b>\n\n"
        f"👤 {name}\n📞 {phone}\n\n"
        f"{order_text}\n<b>Jami:</b> {total} so‘m",
        parse_mode="HTML"
    )

    user_cart.pop(chat_id, None)

# ================== ADMIN PANEL ==================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📋 Buyurtmalar", "📊 Statistika")
    kb.add("🗑 Buyurtmalarni tozalash")

    bot.send_message(message.chat.id, "👨‍💼 Admin panel", reply_markup=kb)

# ================== ADMIN BUYURTMALAR ==================
@bot.message_handler(func=lambda m: m.text == "📋 Buyurtmalar" and m.chat.id == ADMIN_ID)
def admin_orders(message):
    if not orders:
        bot.send_message(ADMIN_ID, "Buyurtmalar yo‘q ❌")
        return

    text = "📋 <b>Barcha buyurtmalar:</b>\n\n"
    for i, o in enumerate(orders, 1):
        text += f"{i}. {o['name']} — {o['total']} so‘m\n"

    bot.send_message(ADMIN_ID, text, parse_mode="HTML")

# ================== ADMIN STATISTIKA ==================
@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.chat.id == ADMIN_ID)
def admin_stats(message):
    total_orders = len(orders)
    total_sum = sum(o["total"] for o in orders)

    bot.send_message(
        ADMIN_ID,
        f"📊 <b>Statistika</b>\n\n"
        f"📦 Buyurtmalar: {total_orders}\n"
        f"💰 Umumiy summa: {total_sum} so‘m",
        parse_mode="HTML"
    )

# ================== ADMIN TOZALASH ==================
@bot.message_handler(func=lambda m: m.text == "🗑 Buyurtmalarni tozalash" and m.chat.id == ADMIN_ID)
def clear_orders(message):
    orders.clear()
    bot.send_message(ADMIN_ID, "✅ Buyurtmalar tozalandi")

# ================== RUN ==================
print("Bot ishga tushdi...")
bot.infinity_polling()
