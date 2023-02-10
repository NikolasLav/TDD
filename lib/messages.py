from vkbottle import CtxStorage, BaseStateGroup
from vkbottle.bot import Blueprint, Message
from lib import keyboards
from manage import Reg, user_info, get_ready

part = Blueprint("For questions and answers")
part.on.vbml_ignore_case = True


ctx = CtxStorage()


@part.on.private_message(lev="start")
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
			await keyboards.start_handler(message)
			return await get_ready(await user_info(message.peer_id))
	except:
		await part.state_dispenser.set(message.peer_id, Reg.AGE_TO)
		return """Ошибка, принимаются только цифры
		Введите возраст "ДО":"""