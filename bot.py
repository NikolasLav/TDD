# Команды для бота
# import manage
# import db
from config import bot_config as config
import asyncio
from loguru import logger
from vkbottle.bot import Bot, Message
from vkbottle import load_blueprints_from_package, CtxStorage


#logger.disable('vkbottle')
bot = Bot(token=config['group_token'])
for part in load_blueprints_from_package("lib"):
	part.load(bot)

ctx_storage = CtxStorage()
ctx_storage.set("user_token", config['user_token'])

bot.run_forever()