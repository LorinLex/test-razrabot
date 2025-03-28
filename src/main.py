import os
import asyncio
from loguru import logger

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from dotenv import dotenv_values

from src.api import check_url
from src.parser import parse


def get_env_vars() -> dict[str, str | None]:
    prefix = "RZ_"

    load_dotenv = os.getenv(f"{prefix}LOAD_DOTENV", True)
    dotenv_parced = dotenv_values() if load_dotenv else {}

    env_vars = {key: value for key, value in os.environ.items()
                if key.startswith(prefix)}

    dotenv_parced.update(env_vars)
    logger.debug("Parsed env vars")

    return {key.split(prefix)[1]: value
            for key, value in dotenv_parced.items()}


env_vars = get_env_vars()

bot_token = env_vars.get("BOT_TOKEN")
if bot_token is None:
    raise ValueError("No bot token!")

bot = Bot(bot_token)
dp = Dispatcher()


@dp.message()
async def get_item_positions(message: types.Message):
    logger.debug("Got url")
    url = message.text
    if url is None:
        logger.error("Url is None")
        await message.answer("Попробуй еще раз")
        return

    if not await check_url(url):
        logger.error("Url is not working")
        await message.answer("Что-то не так со ссылкой! Попробуй другую")
        return

    logger.debug("Url is valid")
    await message.answer("Ссылка работает! Начинаю поиск")

    kw_indexes = await parse(url)

    text = "Найдено:\n\n"
    for key, value in kw_indexes.items():
        text += f"Ключевое слово: \"{key}\", позиция: {value}\n"

    await message.answer(
        "Если позиция None, значит товар находится на позиции больше 6000...\n"
    )
    await message.answer(text)


@dp.message(CommandStart)
async def start(message: types.Message):
    logger.debug("Fetched 'start'")
    await message.answer(
        "Пришли мне ссылку на товар WB. "
        "Я найду ключевые слова и выведу индекс товара в выдаче по этому слову."
        "Ключевые слова ищу алгоритмом yake",
        parse_mode=ParseMode.HTML
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
