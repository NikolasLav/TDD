import asyncio
import asyncpg
from vkbottle import CtxStorage

ctx = CtxStorage()

#####################
# DB access methods #
#####################

"""Create tables"""
async def create_tables(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS temp_list (
        user_id integer,
        profile_id integer NOT NULL,
        first_name varchar(32) NOT NULL,
        last_name varchar(32) NOT NULL,
        city_id integer,
        relation integer);
        """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
        user_id integer NOT NULL,
        profile_id integer NOT NULL,
		profile_name varchar(70) NOT NULL,
        photo_ids varchar(40) NOT NULL,
        marked_photos varchar(80),
        seen boolean NOT NULL,
        banned boolean NOT NULL,
        favorite boolean NOT NULL);
        """)


"""Drop temp tables"""
async def drop_db(conn) -> None:
	await conn.execute("""
		DROP TABLE temp_list CASCADE;
		""")
        

"""Temporary list with results from VK users.search method"""
async def make_temp_list(conn, profiles):
    user_id = ctx.get("user_id")
    user_city_id = ctx.get("city_id")
    _checklist = await get_results(conn, user_id=user_id)
    checklist = []
    for item in _checklist:
        checklist.append(item[1])
    for profile in profiles:
        try:
            city_id = profile.city.id
        except:
            city_id = None
        if (city_id == user_city_id) and (profile.id not in checklist):
            try:
                relation = profile.relation.value
            except:
                relation = 0
            await conn.execute('''INSERT INTO temp_list (user_id, profile_id, first_name, last_name, city_id, relation) VALUES($1, $2, $3, $4, $5, $6)''', user_id, profile.id, profile.first_name, profile.last_name, city_id, relation)


"""Remove record(s) from temp list"""
async def remove_from_temp(conn, user_id, profile_id=None) -> None:
    try:
        if profile_id is None:
            SQL = f"DELETE FROM temp_list WHERE user_id = {user_id};"
        else:
            SQL = f"DELETE FROM temp_list WHERE user_id = {user_id} AND profile_id = {profile_id};"
        await conn.execute(SQL)
    except:
        print('-- Ошибка удаления. параметры:', user_id, profile_id)


"""Get 10 profiles from temp"""
async def get_profiles(conn) -> (list | None):
    user_id = ctx.get("user_id")
    results_temp = await conn.fetch(
            f"SELECT profile_id, first_name, last_name, relation FROM temp_list WHERE user_id = {user_id} LIMIT 10;")
    results = []
    keys = ["id", "first_name", "last_name", "relation"]
    for result in results_temp:
        profile = dict(zip(keys, result))
        results.append(profile)
    return results


"""Result: add"""
async def add_results(conn, user_id, profiles) -> None:
    checklist = []# await get_results(conn, user_id=user_id)
    for profile in profiles:
        await remove_from_temp(conn, user_id, profile['id'])
        if profile['photo_ids'] != None:
            photo_ids = ','.join(str(photo)
                                 for photo in profile['photo_ids'])
            if profile['marked_photos'] is None:
                marked_photos = None
            else:
                marked_photos = ','.join(str(photo)
                                         for photo in profile['marked_photos'])
            if profile['id'] not in checklist:
                try:
                    await conn.execute("""INSERT INTO results (
                        user_id,
                        profile_id,
                        profile_name,
                        photo_ids,
                        marked_photos,
                        seen,
                        banned,
                        favorite)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);""",
                                user_id, profile['id'], profile['name'], photo_ids, marked_photos, False, False, False)
                except:
                    pass


"""Result: delete"""
async def del_results(conn, user_id, temp=False) -> None:
    if temp:
        appendix = " AND seen = FALSE"
    else:
        appendix = ""
    await conn.execute(f"DELETE FROM results WHERE user_id = {user_id}{appendix};")


"""Result: get (for displaying)"""
async def get_results(
    conn,
    profile_id=None,
    user_id=None,
    favorite=None,
    banned=None,
    not_seen=None
) -> (list | None):
    appendix = ''
    if favorite:
        appendix += ' AND favorite = true'
    if banned:
        appendix += ' AND banned = true'
    if not_seen:
        appendix += ' AND seen = false LIMIT 1'
    if user_id == None:
        SQL = f"SELECT * FROM results WHERE profile_id = {profile_id}{appendix};"
    elif profile_id == None:
        SQL = f"SELECT * FROM results WHERE user_id = {user_id}{appendix};"
    else:
        SQL = f"SELECT * FROM results WHERE profile_id = {profile_id} AND user_id = {user_id}{appendix};"

    try:
        query = await conn.fetch(SQL)
        # if favorite or banned:
        #     for item in query:
        #         result += [[*item]]
        # else:
        #     for item in query.fetch():
        #         result += [*item]
        return query
    except:
        return None


"""Result: change status"""
async def update_results(conn, profile_id, user_id, favorite=None, banned=None, seen=None) -> None:
    appendix = ''
    if favorite:
        appendix += 'favorite = true '
    elif favorite == False:
        appendix += 'favorite = false '
    if banned:
        appendix += 'banned = true '
    elif banned == False:
        appendix += 'banned = false '
    if seen:
        appendix += 'seen = true '
    try:
        await conn.execute(
                f"UPDATE results SET {appendix} WHERE profile_id = {profile_id} AND user_id = {user_id};")
    except:
        pass
