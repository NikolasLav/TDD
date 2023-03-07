from config import bot_config as config
from loguru import logger
from vkbottle.bot import Bot
from vkbottle import load_blueprints_from_package

#################
# Main programm #
#################

logger.disable('vkbottle')
bot = Bot(token=config['group_token'])
for part in load_blueprints_from_package("lib"):
	part.load(bot)
print("Бот запустился")
bot.run_forever()