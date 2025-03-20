import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.types.message import ContentType

# Bot va dispatcher yaratamiz
TOKEN = "8015050646:AAHzRS9kg1cWZjCpA-8F9nm5SRxeyV7JIDI"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Foydalanuvchilar ma'lumotlarini saqlash uchun baza
users_data = {}

# Klaviatura tugmalari
tg_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
    ],
    resize_keyboard=True
)

main_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)],
        [KeyboardButton(text="🔍 Qidiruv"), KeyboardButton(text="👤 Profil")],
        [KeyboardButton(text="📩 Anonim chat"), KeyboardButton(text="🔔 Xavfsizlik")]
    ],
    resize_keyboard=True
)

def save_user(user_id, name, phone=None, location=None):
    if user_id not in users_data:
        users_data[user_id] = {"name": name, "phone": phone, "location": location}
    else:
        if phone:
            users_data[user_id]["phone"] = phone
        if location:
            users_data[user_id]["location"] = location

def is_registered(user_id):
    """Foydalanuvchi telefon raqam yuborganini tekshirish"""
    return user_id in users_data and users_data[user_id].get("phone") is not None

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    save_user(user_id, message.from_user.full_name)

    if not is_registered(user_id):
        await message.answer("📞 Botdan to‘liq foydalanish uchun telefon raqamingizni yuboring.", reply_markup=tg_buttons)
    else:
        await message.answer("👋 Salom! Xizmatlardan foydalanish uchun menyudan tanlang.", reply_markup=main_buttons)

@dp.message(lambda message: message.content_type == ContentType.CONTACT)
async def save_phone(message: types.Message):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    save_user(user_id, message.from_user.full_name, phone=phone_number)
    await message.answer("✅ Telefon raqamingiz saqlandi! Endi botdan to‘liq foydalanishingiz mumkin.", reply_markup=main_buttons)

@dp.message(lambda message: not is_registered(message.from_user.id))
async def ask_for_phone(message: types.Message):
    await message.answer("📞 Iltimos, botdan foydalanish uchun telefon raqamingizni yuboring.", reply_markup=tg_buttons)

@dp.message(lambda message: message.text == "📍 Lokatsiyani yuborish")
async def location_info(message: types.Message):
    await message.answer("📍 Lokatsiyani yuborish tugmasi sizning joylashuvingizni bizga jo‘natadi. "
                         "Bu orqali biz sizga yaqin atrofdagi foydalanuvchilarni topishimiz mumkin.")

@dp.message(lambda message: message.content_type == ContentType.LOCATION)
async def save_location(message: types.Message):
    """Foydalanuvchining lokatsiyasini saqlash"""
    user_id = message.from_user.id
    location = {
        "latitude": message.location.latitude,
        "longitude": message.location.longitude
    }

    save_user(user_id, message.from_user.full_name, location=location)
    await message.answer("📍 Lokatsiyangiz saqlandi!", reply_markup=main_buttons)

@dp.message(lambda message: message.text == "🔍 Qidiruv")
async def search_info(message: types.Message):
    await message.answer("🔍 Qidiruv tugmasi orqali foydalanuvchilarni telefon raqami yoki ismi bo‘yicha topishingiz mumkin.\n\n"
                         "Qo‘llash usuli:\n"
                         "1️⃣ `/search Ism` - Foydalanuvchini ismi bo‘yicha qidirish.\n"
                         "2️⃣ Telefon raqamini yozib yuboring - Telefon raqam orqali foydalanuvchini topish.")

@dp.message(lambda message: message.text == "👤 Profil")
async def profile_info(message: types.Message):
    user_id = message.from_user.id
    user = users_data.get(user_id, {})
    response = f"👤 **Sizning profilingiz**\n📛 Ism: {user.get('name', 'Noma’lum')}\n📞 Raqam: {user.get('phone', 'Noma’lum')}"

    if user.get("location"):
        response += f"\n📍 Lokatsiya: {user['location']['latitude']}, {user['location']['longitude']}"

    await message.answer(response)

@dp.message(lambda message: message.text == "📩 Anonim chat")
async def chat_info(message: types.Message):
    await message.answer("📩 Anonim chat tugmasi orqali boshqa foydalanuvchilar bilan anonim tarzda suhbat qurishingiz mumkin.\n\n"
                         "Hali bu funksiya ishlab chiqilmoqda.")

@dp.message(lambda message: message.text == "🔔 Xavfsizlik")
async def security_info(message: types.Message):
    await message.answer("🔔 Xavfsizlik bo‘limi orqali akkauntingiz himoyasi va xavfsizlik sozlamalarini boshqarishingiz mumkin.\n\n"
                         "Hali bu funksiya ishlab chiqilmoqda.")

@dp.message(Command("users"))
async def show_users(message: types.Message):
    """Barcha ro‘yxatdan o‘tgan foydalanuvchilarni ko‘rsatish"""
    if not users_data:
        await message.answer("📋 Hozircha ro‘yxatdan o‘tgan foydalanuvchilar yo‘q.")
        return

    response = "📋 **Foydalanuvchilar ro‘yxati:**\n\n"
    for user_id, data in users_data.items():
        response += f"👤 {data.get('name', 'Noma’lum')}\n"
        response += f"📞 {data.get('phone', 'Noma’lum')}\n"
        if data.get("location"):
            response += f"📍 {data['location']['latitude']}, {data['location']['longitude']}\n"
        response += "──────────────\n"

    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
