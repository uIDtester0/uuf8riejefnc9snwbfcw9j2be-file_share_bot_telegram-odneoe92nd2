import logging
import hashlib
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

API_TOKEN = 'error404'
BOT_USERNAME = 'error404'  # Укажите имя пользователя вашего бота
DATA_FILE = 'data.txt'  # Файл для хранения данных

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def save_file_data(user_id, file_hash, file_id):
    with open(DATA_FILE, 'a') as f:
        f.write(f"{user_id}:{file_hash}:{file_id}\n")

def get_file_data(user_id, file_hash):
    try:
        with open(DATA_FILE, 'r') as f:
            for line in f:
                stored_user_id, stored_file_hash, stored_file_id = line.strip().split(':')
                if stored_user_id == str(user_id) and stored_file_hash == file_hash:
                    return stored_file_id
    except FileNotFoundError:
        return None
    return None

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Проверяем, есть ли параметр в команде
    if message.get_args():
        file_hash = message.get_args()
        user_id = message.from_user.id

        # Проверяем, есть ли файл с таким хэшом
        file_id = get_file_data(user_id, file_hash)
        if file_id:
            await bot.send_document(chat_id=user_id, document=file_id)
        else:
            await message.reply("Файл не найден.")
    else:
        await message.reply("Hi! Я бот для обмена файлами.")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, что пользователь имеет ID 404
    if user_id != 404:
        return

    file_id = message.document.file_id

    # Генерируем уникальный идентификатор для файла
    file_hash = hashlib.md5(f"{user_id}_{file_id}".encode()).hexdigest()

    # Сохраняем файл для пользователя
    save_file_data(user_id, file_hash, file_id)
    link = f"https://t.me/{BOT_USERNAME}?start={file_hash}"
    await message.reply(f"Файл сохранен! Ты можешь получить его по ссылке:\n<code>{link}</code>", parse_mode=types.ParseMode.HTML)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
