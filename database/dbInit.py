from gino import Gino
from configs.Config import Config
from utils.logger import logging
import asyncio

db: Gino = Gino()


async def connect():
    while True:
        try:
            await db.set_bind(Config.get_db_addr())
            await db.gino.create_all()  # type: ignore
            logging.info("Successfully connected to database!")
            break
        except Exception as e:
            logging.warning(f"Failed to connect to database: {e}! retrying...")
            await asyncio.sleep(1)
            continue


async def disconnect():
    await db.pop_bind().close()
    logging.info("Database disconnected")
