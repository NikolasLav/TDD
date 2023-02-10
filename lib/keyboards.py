from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import BaseStateGroup, Keyboard, KeyboardButtonColor, Text, GroupEventType, GroupTypes, VKAPIError, Callback, EMPTY_KEYBOARD, template_gen, TemplateElement, CtxStorage
from vkbottle.modules import json
from datetime import datetime
import manage
from manage import Reg


part = Blueprint("Keyboard generator")
part.on.vbml_ignore_case = True
ctx = CtxStorage()
ctx.set("a", "Активация change_settings")
# api = API(token=ctx.get("user_token"))


@part.on.private_message(text="stop")
async def stop_handler(message: Message):
	await message.answer("refresh", keyboard=EMPTY_KEYBOARD)


# @part.on.private_message(state=Reg.KEYBOARD)
async def start_handler(message: Message):
	await part.state_dispenser.set(message.peer_id, Reg.END)
	keyboard = (
		Keyboard()
		.add(Callback("Изменить настройки поиска", {"cmd": "change_settings"}), KeyboardButtonColor.PRIMARY)
		.add(Callback("Показать настройки поиска", {"cmd": "view_settings"}))
	)
	return await message.answer(f"Можете уже искать.", keyboard=keyboard)


@part.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_message_event(event: MessageEvent):
	if event.object.payload["cmd"] == "change_settings":
		await event.show_snackbar(ctx.get("a"))
	elif event.object.payload["cmd"] == "view_settings":
		if ctx.get("user_name") != None:
			await event.show_snackbar(f"""{ctx.get("user_name")}, родился {ctx.get("bdate")}. Ищем в городе: {ctx.get("city_title")}""")
		else:
			await event.show_snackbar("Пользователь не настроен")
