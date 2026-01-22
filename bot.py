import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import SOURCES, MAX_ARTS

BOT_TOKEN = os.getenv("8554158049:AAFO5a1UdZu5gVo6VdUQJr0kzPHZIUKurn8")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- storage ----------
STORAGE_FILE = "storage.json"

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"sent": []}
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

storage = load_storage()

# ---------- menu ----------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎨 Запросить арты", callback_data="get_art")]
    ])

# ---------- handlers ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет.\nВыбери действие 👇",
        reply_markup=main_menu()
    )

@dp.callback_query(lambda c: c.data == "get_art")
async def ask_tag(callback: types.CallbackQuery):
    await callback.message.answer(
        "Напиши запрос в формате:\n\n+арт #тег количество\n\nПример:\n+арт #vivian 5",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(lambda m: m.text and m.text.startswith("+арт"))
async def send_art(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        return

    tag = parts[1].replace("#", "")
    try:
        count = min(int(parts[2]), MAX_ARTS)
    except:
        return

    sent_media = []
    used_source = 0

    for source in SOURCES:
        used_source += 1
        async for msg in bot.iter_messages(source, search=f"#{tag}", limit=50):
            if not msg.photo:
                continue

            file_id = msg.photo[-1].file_id
            if file_id in storage["sent"]:
                continue

            sent_media.append(types.InputMediaPhoto(media=file_id))
            storage["sent"].append(file_id)

            if len(sent_media) >= count:
                break

        if sent_media:
            break
        else:
            await message.answer(f"Перехожу на {used_source + 1} источник")

    if not sent_media:
        await message.answer("Арты с таким тегом не найдены.")
        return

    save_storage(storage)

    await message.answer_media_group(sent_media)

# ---------- run ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())