import asyncio
from pprint import pprint
from vkbottle import API, CtxStorage, BaseStateGroup

ctx = CtxStorage()


class Reg(BaseStateGroup):
	START = 0
	AGE_FROM = 1
	AGE_TO = 2
	END = 3  # END я добавляю чтобы стейт останавливался.


async def get_ready(user):
	if Reg.AGE_TO == 2:
		Reg.END
	api = API(CtxStorage().get("user_token"))
	quantity = 6 #максимальная выдача
	profiles = []
	result = []
	if user['sex'] == 1:
		sex = 2
	elif user['sex'] == 2:
		sex = 1
	else:
		sex = 0
	check_results = [100732960] # db.get_results(conn, user_id=user['id']) #проверяем выдавался ли уже результат?
	print('-check_results', check_results)
	request = await api.users.search(count=quantity, city_id=user['city_id'], sex=sex, age_from=user['age_from'], age_to=user['age_to'], fields=["bdate", "city", "relation"])
	profiles += request.items
	print('- users.search result:', len(profiles))
	for profile in profiles:
		print('== Профиль', profile.id, profile.last_name)
		try:
			if (profile.id not in check_results) and (profile.city.id == user['city_id']):
					print('+ Подходит, т.к. соответствует город и нет в чеклисте')
					# извлекаем только нужное: ID, fn, ln, bdate, city_id, relation
					profile = {'id': profile.id, 'first_name': profile.first_name, 'last_name': profile.last_name, 'bdate': profile.bdate, 'city_id': profile.city.id, 'relation': profile.relation.value}
					result += [profile]
			else:
				print('- Не подходит, т.к. есть в чеклисте, или город не тот')
		except:
			pass
	# db.make_temp_list(conn, user['id'], result)
	return pprint(result)


async def user_info(user_id):
	#try:
		api = API(CtxStorage().get("user_token"))
		user_info = await api.users.get(user_id, fields=["sex","city","relation", "bdate"])
		user = {
			"user_id": user_id,
			"first_name": user_info[0].first_name,
			"last_name": user_info[0].first_name,
			"bdate": user_info[0].bdate,
			"sex": user_info[0].sex.value,
			"city_id": user_info[0].city.id,
			"city_title": user_info[0].city.title,
			"relation": user_info[0].relation.value,
			"age_from": ctx.get("age_from"),
			"age_to": ctx.get("age_to")
			}
		
		print (user)
		for parametr in list(user):
			if user[parametr] == None:
				user.pop(parametr)
			if parametr == 'sex':
				if user[parametr] == 0:
					user.pop(parametr)
		print (user)

		ctx.set("user_id", user_id)
		ctx.set("user_name", f"{user_info[0].first_name} {user_info[0].last_name}")
		ctx.set("bdate", user_info[0].bdate)
		ctx.set("sex", user_info[0].sex)
		ctx.set("city_id", user_info[0].city.id)
		ctx.set("city_title", user_info[0].city.title)
		ctx.set("relation", user_info[0].relation.value)


		# надо запустить чеклист на проверку данных
		checklist = ['user_id', 'city_id', 'relation', 'sex', 'first_name', 'last_name', 'bdate', 'age_from', 'age_to']
		
		# запуск поиска
		


		return user
	#except:
	#	return None
