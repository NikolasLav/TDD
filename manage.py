import db
from config import bot_config as config
from vkbottle import API, CtxStorage, BaseStateGroup
 
import asyncio
import asyncpg

###############################
# VK methods and etc. manager #
###############################

ctx = CtxStorage()
api = API(config['user_token'])
DSN = f'postgresql://postgres:{config["pgpwd"]}@127.0.0.1/test'


"""Class for step-by-step survey"""
class Reg(BaseStateGroup):
	START = 0
	AGE_FROM = 1
	AGE_TO = 2
	END = 3  # END добавляю чтобы стейт останавливался.


"""Search preparation"""
async def get_ready(user_id):
	quantity = 1000 #максимальная выдача
	if ctx.get("sex") == 1:
		sex = 2
	elif ctx.get("sex") == 2:
		sex = 1
	else:
		sex = 0
	
	request = await api.users.search(count=quantity, city_id=ctx.get("city_id"), sex=sex, age_from=ctx.get("age_from"), age_to=ctx.get("age_to"), fields=["bdate", "city", "relation"])
	profiles = []
	profiles += request.items

	# работаем с БД: подготавливаем вывод
	conn = await asyncpg.connect(DSN)
	await db.remove_from_temp(conn, user_id)
	await db.make_temp_list(conn, profiles)
	await prepare(conn, user_id)
	await conn.close()
	

async def user_info(user_id):
		user_info = await api.users.get(user_id, fields=["sex","city","relation", "bdate"])
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
		await get_ready(user_id)


"""Get top-3 photos"""
async def _get_top3(photos: dict, owner_id=False) -> (list | None):
    try:
        photos = photos.items
        # Доступно более 3-х фото для оценки или это отметки
        if len(photos) >= 3 or owner_id:
            result = []
            for photo in photos:
                    rate = photo.likes.count + photo.comments.count
                    if owner_id:
                        result += [[rate, photo.owner_id, photo.id]]
                    else:
                        result += [[rate, photo.id]]
            result.sort(reverse=True)
            result = result [0:3]
            photos = []
            if owner_id:
                for _, owner_id, photo in result:
                    photos += [owner_id, photo]
            else:
                for _, photo in result:
                    photos.append(photo)
                    
            return photos
        else:
            return None    
    except:
        return None


"""Rate profiles"""
async def rate_profiles(persons) -> list:
	new_persons = []
	# for person, photos, marked in zip(persons, profile_photos, marked_photos):
	for person in persons:
		try:
			profile_photos = await api.photos.get(owner_id=person['id'], album_id="profile", rev=1, extended=1)
		except:
			profile_photos = None #метод иногда не срабатывает?
		photos = await _get_top3(profile_photos)
		marked = None #await _get_top3(marked_photos, owner_id=True)
		name = f"{person['first_name']} {person['last_name']}"
		person = {'id': person['id'],
		          'name': name, 'photo_ids': photos, 'marked_photos': marked}
		new_persons.append(person)
	return new_persons


"""Display preparing"""
async def prepare(conn, user_id):
	print('подготовка профилей')
	person = await db.get_results(conn, user_id=user_id, not_seen=True)
	if person == []:
		while person == []:
			profiles = await db.get_profiles(conn)
			if len(profiles) > 0:
				print(len(profiles), 'профилей пошло на оценку')
				persons = await rate_profiles(profiles)
				if len(persons) > 0:
					await db.add_results(conn, user_id, persons)
			elif len(profiles) == 0:
				break