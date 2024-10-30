import logging
from sqlalchemy.exc import SQLAlchemyError
from models import History, async_session

async def save_history(user_id: int, image_path: str, text: str):
    try:
        async with async_session() as session:
            async with session.begin():
                history_record = History(user_id=user_id, image_path=image_path, text=text)
                session.add(history_record)
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при сохранении в базу данных: {e}")
        raise RuntimeError("Не удалось сохранить историю в базу данных.")

async def get_history(user_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(History).where(History.user_id == user_id))
            return result.scalars().all()
