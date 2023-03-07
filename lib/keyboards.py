from vkbottle.bot import Blueprint, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback, EMPTY_KEYBOARD

####################
# Keyboard manager #
####################

part = Blueprint("Keyboard generator")
part.on.vbml_ignore_case = True

KEYBOARD = (
	Keyboard()
	.add(Callback("Поиск", {"cmd": "search"}), KeyboardButtonColor.PRIMARY)
	#.add(Callback("Изменить настройки поиска", {"cmd": "change_settings"}), KeyboardButtonColor.PRIMARY)
	.add(Callback("Показать настройки поиска", {"cmd": "view_settings"})))


"""Handler for cleaner (actually not needed)"""
@part.on.private_message(text="стоп")
async def stop_handler(message: Message):
	await message.answer("refresh", keyboard=EMPTY_KEYBOARD)


"""Main keyboard"""
async def keyboard_handler(message: Message):
	return await message.answer(f"Программа готова к поиску.", keyboard=KEYBOARD)
  