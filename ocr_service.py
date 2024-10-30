from paddleocr import PaddleOCR
from config import SUPPORTED_LANGUAGES
from PIL import Image
import io
import logging

ocr_instances = {lang: PaddleOCR(use_angle_cls=True, lang=lang) for lang in SUPPORTED_LANGUAGES}

async def recognize_text(image: Image.Image, lang: str = 'en') -> str:
    ocr = ocr_instances.get(lang)
    if not ocr:
        return "Выбранный язык не поддерживается."

    try:
        # Преобразование изображения для PaddleOCR
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        result = ocr.ocr(img_bytes, cls=True)
        text = "\n".join([line[1][0] for line in result[0]])
        return text if text else "Не удалось распознать текст на изображении."

    except Exception as e:
        logging.error(f"Ошибка при распознавании текста: {e}")
        return "Произошла ошибка при распознавании текста."
