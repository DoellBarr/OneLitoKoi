import asyncio
import logging
import configs
from core import bot as main_bot
from aiogram import Dispatcher, Bot
from plugins import routers
from controllers import scheduler

dp = Dispatcher()
for router in routers:
    dp.include_router(router)


@dp.startup.register
async def on_startup(bot: Bot):
    print("starting up...")
    me = await bot.me()
    configs.bot_username = me.username
    print(
        f"""bot is running
ID: {me.id}
Name: {me.full_name}
Username: @{me.username}"""
    )
    print("starting scheduler...")
    scheduler.start()


@dp.shutdown.register
async def on_shutdown(bot: Bot, dispatcher: Dispatcher):
    print("Shutting Down..")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling(main_bot))
    except KeyboardInterrupt:
        loop.run_until_complete(dp.stop_polling())
