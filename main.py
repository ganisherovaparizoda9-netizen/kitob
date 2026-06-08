import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




GROQ_API_KEY = "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

# Gemini sozlamasi
logging.basicConfig(level=logging.INFO)
bot = Bot(token="8997510088:AAEA5bU410nmhp3o4vc3NiDEZYN76_TRQbA")
dp = Dispatcher()

def get_ai_response(prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile", # Groq'dagi juda kuchli model
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if 'choices' in data:
            return data["choices"][0]["message"]["content"]
        return f"❌ Xatolik: {data.get('error', 'Nomaalum xato')}"
    except Exception as e:
        return f"❌ Ulanish xatosi: {e}"

def get_genre_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Sarguzasht", callback_data="genre_sarguzasht"),
         InlineKeyboardButton(text="💡 Ilm-fan", callback_data="genre_ilm")],
        [InlineKeyboardButton(text="🎭 Roman", callback_data="genre_roman"),
         InlineKeyboardButton(text="✨ Motivatsiya", callback_data="genre_motivatsiya")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📚 Salom! Men AI kitob maslahatchisiman. Janr tanlang:", reply_markup=get_genre_keyboard())

@dp.callback_query(F.data.startswith("genre_"))
async def genre_handler(callback: types.CallbackQuery):
    genre = callback.data.split("_")[1]
    msg = await callback.message.answer("🔍 Izlayapman...")
    loop = asyncio.get_running_loop()
    ai_text = await loop.run_in_executor(None, get_ai_response, f"{genre} janrida 5 ta kitob tavsiya qil.")
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=msg.message_id, text=ai_text)
    await callback.answer()

@dp.message(F.text)
async def text_handler(message: types.Message):
    msg = await message.answer("🤖 O'ylayapman...")
    loop = asyncio.get_running_loop()
    ai_text = await loop.run_in_executor(None, get_ai_response, message.text)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=ai_text)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
