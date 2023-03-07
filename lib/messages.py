from vkbottle import API, CtxStorage, GroupEventType, GroupTypes
from vkbottle.bot import Blueprint, Message, MessageEvent, rules, MessageEventMin
from lib import keyboards
from manage import Reg, user_info, prepare
from config import bot_config as config
from random import randrange as rand
import asyncpg
import db

####################
# Messages manager #
####################

part = Blueprint("For questions and answers")
part.on.vbml_ignore_case = True
api = API(config['group_token'])
ctx = CtxStorage()
DSN = f'postgresql://postgres:{config["pgpwd"]}@127.0.0.1/test'

"""Bot starting' handle"""
@part.on.private_message(lev="начать")
async def age_from(message: Message):
    try:
        int(ctx.get("age_from"))
        int(ctx.get("age_to"))
        await keyboards.start_handler(message)
        return """Злоупотребляете функционалом VK? 😑
        По заданным параметрам поиск уже производился.
        Вы можете изменить настройки, чтобы обновить поисковый запрос."""
    except:
        await part.state_dispenser.set(message.peer_id, Reg.AGE_FROM)
        return """Введите возраст "ОТ":"""


@part.on.private_message(state=Reg.AGE_FROM)
async def age_to(message: Message):
	try:
		int(message.text)
		ctx.set('age_from', message.text)
		await part.state_dispenser.set(message.peer_id, Reg.AGE_TO)
		return """Введите возраст "ДО":"""
	except:
		await part.state_dispenser.set(message.peer_id, Reg.AGE_FROM)
		return """Ошибка, принимаются только цифры
		Введите возраст "ОТ":"""


@part.on.private_message(state=Reg.AGE_TO)
async def send_keyboard(message: Message):
	try:
		int(message.text)
		ctx.set('age_to', message.text)
		if int(ctx.get("age_from")) > int(ctx.get("age_to")):
			await part.state_dispenser.set(message.peer_id, Reg.AGE_FROM)
			return """Ошибка, искомый возраст "ОТ" не может быть больше чем возрасто "ДО". Давате повторим ввод.
			Введите возраст "ОТ":"""
		else:
			await part.state_dispenser.set(message.peer_id, Reg.END)
			await user_info(message.peer_id)
			return await keyboards.keyboard_handler(message)
	except:
		await part.state_dispenser.set(message.peer_id, Reg.AGE_TO)
		return """Ошибка, принимаются только цифры
		Введите возраст "ДО":"""


"""raw_event' keyboars handlers"""
@part.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"cmd": "search"}),
)
async def show_result(event: MessageEvent):
    user_id = event.peer_id
    conn = await asyncpg.connect('postgresql://postgres:postgres@127.0.0.1/test')
    await event.show_snackbar("Пробуем подобрать Вам пару...")
    person = await db.get_results(conn, user_id=user_id, not_seen=True)
    if (person is not None) and (len(person) > 0):
        person = person[0]
        id = person[1]
        ctx.set('last_search', id) #для лайков
        photos = person[3].split(',')
        attachment = f'photo{id}_'+f',photo{id}_'.join(photos)
        url = "http://vk.com/id"+str(id)
        await message_send(user_id, 
        f"""{person[2]} {url}
        """, attachment)
            
        await db.update_results(
            conn, profile_id=person[1], user_id=user_id, seen=True)
        # подготовить новую, пока пользователь оценивает выдачу
        await prepare(conn, user_id)
    else:
        await message_send(
            user_id, "Список кандидатов по вашим параметрам пуст, либо все результаты уже у Вас. Попробуйте осуществить поиск по другим параметрам.")
    await conn.close()


@part.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"cmd": "change_settings"}),
)
async def show_snackbar(event: MessageEvent):
	await event.show_snackbar("Изменить настройки поиска")
    

@part.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"cmd": "view_settings"}),
)
async def show_snackbar(event: MessageEvent):
	if ctx.get("user_name") != None:
		await event.show_snackbar(f'{ctx.get("user_name")}, д/р {ctx.get("bdate")}. Город: {ctx.get("city_title")}. Возраст от {ctx.get("age_from")} до {ctx.get("age_to")}')
	else:
		await event.show_snackbar("Пользователь не настроен")


async def message_send(peer_id, msg, attachment=None):
    await api.messages.send(peer_id=peer_id, message=msg, random_id=rand(0,10000), attachment=attachment)
