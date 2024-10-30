from aiogram import types, Dispatcher
from config import SUPPORTED_LANGUAGES
from ocr_service import recognize_text
from db import save_history
from PIL import Image
import io
import os
import logging
from datetime import datetime

async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте мне изображение для распознавания текста. Вы можете также выбрать язык с помощью /language.")

async def choose_language(message: types.Message):
    languages = ", ".join(SUPPORTED_LANGUAGES)
    await message.reply(f"Доступные языки: {languages}. Используйте команду /set_language <язык> чтобы установить язык.")

async def set_language(message: types.Message):
    lang = message.get_args()
    if lang not in SUPPORTED_LANGUAGES:
        await message.reply("Такой язык не поддерживается.")
    else:
        message.bot_data[message.from_user.id] = lang
        await message.reply(f"Язык успешно установлен на {lang}.")

# Обработчик изображений
async def handle_photo(message: types.Message):
    lang = message.bot_data.get(message.from_user.id, 'en')
    
    # Загрузка изображения
    photo = message.photo[-1]
    photo_bytes = io.BytesIO()
    try:
        await photo.download(destination=photo_bytes)
        image = Image.open(photo_bytes)
    except Exception as e:
        logging.error(f"Ошибка при загрузке изображения: {e}")
        await message.reply("Не удалось загрузить изображение. Пожалуйста, попробуйте снова.")
        return

    try:
        text = await recognize_text(image, lang=lang)
        if text == "Произошла ошибка при распознавании текста.":
            await message.reply(text)
            return

        user_id = message.from_user.id
        image_dir = f"images/{user_id}"
        os.makedirs(image_dir, exist_ok=True)
        image_path = f"{image_dir}/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        image.save(image_path)

        try:
            await save_history(user_id, image_path, text)
        except RuntimeError as db_error:
            await message.reply(str(db_error))
            return

        await message.reply(f"Распознанный текст:\n\n{text}")

    except Exception as e:
        logging.error(f"Общая ошибка при обработке изображения: {e}")
        await message.reply("Произошла ошибка при обработке изображения. Пожалуйста, попробуйте снова.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(choose_language, commands=['language'])
    dp.register_message_handler(set_language, commands=['set_language'])
    dp.register_message_handler(handle_photo, content_types=['photo'])
