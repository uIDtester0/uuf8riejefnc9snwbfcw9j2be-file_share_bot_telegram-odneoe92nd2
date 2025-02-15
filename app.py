import logging
import hashlib
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

API_TOKEN = '7707875358:AAFa7bRcZdmbKfRti1cAN2mDWxNb8VzdE8Q'
BOT_USERNAME = 'anonymous_file_share_bot'  # Например: "my_file_bot"
DATA_FILE = 'data.txt'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def save_file_data(file_hash, file_id):
    with open(DATA_FILE, 'a') as f:
        f.write(f"{file_hash}:{file_id}\n")

def get_file_data(file_hash):
    try:
        with open(DATA_FILE, 'r') as f:
            for line in f:
                stored_hash, file_id = line.strip().split(':')
                if stored_hash == file_hash:
                    return file_id
    except FileNotFoundError:
        return None
    return None

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    args = message.get_args()
    if args:
        file_id = get_file_data(args)
        if file_id:
            await bot.send_document(message.from_user.id, file_id)
        else:
            await message.reply("Файл не найден.")
    else:
        await message.reply("Привет! Просто отправь мне любой файл документом!")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    file_id = message.document.file_id
    file_hash = hashlib.md5(file_id.encode()).hexdigest()
    
    save_file_data(file_hash, file_id)
    link = f"https://t.me/{BOT_USERNAME}?start={file_hash}"
    await message.reply(
        f"Файл сохранён! Ссылка для скачивания:\n<code>{link}</code>",
        parse_mode="HTML"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)