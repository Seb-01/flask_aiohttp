from json import dumps

import config
import my_exception

from aiohttp import web
import base64

from validator import validate
from schema import USER_CREATE, ADVERT_CREATE

from flask import json
from werkzeug.security import generate_password_hash, check_password_hash

#реализация логина|пароля
def set_password(password):
    password_hash = generate_password_hash(password)
    return password_hash

# для проверки пароля: кодируем открытый пароль в SHA256
def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)
    # password = hashlib.sha256(user_password.encode()).hexdigest()
    # if hashed_password == password:
    #     return True
    # else:
    #     return False

# обработка http - запросов: пользователь
class User(web.View):

    #Корутина для метода get
    #  будет доступно по роуту /api/v1/users/{user_id:\d+}
    #  вместо user_id подставляется число, переданное в url
    async def get(self):
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка роли и пароля администратора
        # подготовка к декодированию: 'Basic R29zaGE6R29zaDU1NS1naGoz' (нам нужен код после пробела)
        auth_for_64decode = auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0]  # логин
        passw = credential[1]  # пароль

        #проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                #если есть такой username?
                if result:
                    # если username является admin
                    if result[4] == True:
                        print('Admin!!')
                        # проверка пароля
                        if check_password(result[3], passw):
                            pg_pool = self.request.app['pg_pool']
                            # подключаемя к БД и забираем инфу
                            user_id = self.request.match_info['user_id']  # получаем user_id
                            await cursor.execute('SELECT * from public.user where id = %s', user_id)
                            result = await cursor.fetchone()
                            if result:
                                return web.json_response({
                                    'id': result[0],
                                    'name': result[1]
                                })
                            # если ничего не нашли
                            raise web.HTTPNotFound()
                        else:
                            print('Неверный пароль Admin!')
                            raise web.HTTPUnauthorized()
                    else:
                        print('Пользователь не является Admin!')
                        raise web.HTTPUnauthorized()

                # не нашли такого пользователя
                raise web.HTTPNotFound()


# обработка http - запросов: пользователи
class Users(web.View):

    #Корутина для метода get
    #  будет доступно по роуту (/api/v1/users)
    async def get(self):
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка роли и пароля администратора
        #подготовка к декодированию: 'Basic R29zaGE6R29zaDU1NS1naGoz' (нам нужен код после пробела)
        auth_for_64decode=auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0] #логин
        passw = credential[1]   #пароль

        #проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                #если есть такой username?
                if result:
                    # если username является admin
                    if result[4] == True:
                        print('Admin!!')
                        # проверка пароля
                        if check_password(result[3], passw):
                            pg_pool = self.request.app['pg_pool']
                            # подключаемя к БД и забираем инфу
                            await cursor.execute('SELECT * from public.user')
                            results = await cursor.fetchall()
                            if results:
                                res = []
                                for result in results:
                                    item = {}
                                    item['id'] = result[0]
                                    item['name'] = result[1]
                                    item['email'] = result[2]
                                    res.append(item)
                                return web.json_response(res)
                            # если ничего не нашли
                            raise web.HTTPNotFound()
                        else:
                            print('Неверный пароль Admin!')
                            raise web.HTTPUnauthorized()
                    else:
                        print('Пользователь не является Admin!')
                        raise web.HTTPUnauthorized()

                # не нашли такого пользователя
                raise web.HTTPNotFound()

        # Корутина для метода get
        #  будет доступно по роуту (/api/v1/users)

    @validate('json', USER_CREATE)
    async def post(self):
        # res = json.dumps({"answer": "Попытка создать пользователя!"}, ensure_ascii=False)
        # return web.json_response(res, headers={"Content-Language":"ru-RU, en", "Accept-Language":"ru-RU, en"})

        #Если мы сюда попали, значит проверка json пройдена:
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка роли и пароля администратора
        # подготовка к декодированию: 'Basic R29zaGE6R29zaDU1NS1naGoz' (нам нужен код после пробела)
        auth_for_64decode = auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0]  # логин
        passw = credential[1]  # пароль

        # проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                # если есть такой username?
                if result:
                    # если username является admin
                    if result[4] == True:
                        print('Admin!!')
                        # проверка пароля
                        if check_password(result[3], passw):
                            # сохраняем запись о пользователе в БД
                            json_req=await self.request.json()
                            username = json_req.get('username')
                            password = set_password(json_req.get('password'))
                            email = json_req.get('email')

                            try:
                                #Внимание! Двойные кавычки здесь не пройдут!
                                sql_expr="INSERT INTO public.user (username, email, password_hash) VALUES (\'%s\',\'%s\',\'%s\')" % (username, email, password)
                                await cursor.execute(sql_expr)
                                #result=await cursor.fetchall()
                            except my_exception.DBInsertError:
                                if config.DEBUG:
                                    print('Ошибка cursor.execute(query)')
                                raise web.HTTPBadRequest
                            else:
                                #psycopg2.ProgrammingError: commit cannot be used in asynchronous mode
                                await conn.commit()
                                res=[]
                                item = {}
                                item['user'] = username
                                item['email'] = email
                                res.append(item)
                                return web.json_response(res)

                        else:
                            print('Неверный пароль Admin!')
                            raise web.HTTPUnauthorized()
                    else:
                        print('Пользователь не является Admin!')
                        raise web.HTTPUnauthorized()

                else: # не нашли такого пользователя
                    raise web.HTTPNotFound()

# обработка http - запросов: объявления
class Adverts(web.View):
    @validate('json', ADVERT_CREATE)
    async def post(self):

        # Если мы сюда попали, значит проверка json пройдена:
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка пользователя
        # подготовка к декодированию:
        auth_for_64decode = auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0]  # логин
        passw = credential[1]  # пароль

        # проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                # если есть такой username?
                if result:
                    # проверка пароля
                    if check_password(result[3], passw):
                        # сохраняем объявление в БД
                        json_req = await self.request.json()
                        title = json_req.get('title')
                        body = json_req.get('body')
                        user_id=result[0]

                        try:
                            # Внимание! Двойные кавычки здесь не пройдут!
                            sql_expr = f'INSERT INTO public.advert (title, body, user_id) VALUES (\'{title}\',\'{body}\',\'{user_id}\') RETURNING id'
                            await cursor.execute(sql_expr)
                            # здесь нужно создать селект-запрос сразу после INSERT
                        except my_exception.DBInsertError:
                            if config.DEBUG:
                                print('Ошибка cursor.execute(query)')
                            raise web.HTTPBadRequest

                        # psycopg2.ProgrammingError: commit cannot be used in asynchronous mode
                        #conn.commit()
                        res = []
                        item = {}
                        item['title'] = title
                        item['body'] = body
                        item['user_id'] = user_id
                        res.append(item)
                        return web.json_response(res)

                    else:
                        print('Неверный пароль!')
                        raise web.HTTPUnauthorized()

                else:  # не нашли такого пользователя
                    print('Нет такого пользователя!')
                    raise web.HTTPNotFound()

    #получить все объявления - получать можно только список своих объявлений. Admin получает все!
    async def get(self):
        # Если мы сюда попали, значит проверка json пройдена:
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка пользователя
        # подготовка к декодированию:
        auth_for_64decode = auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0]  # логин
        passw = credential[1]  # пароль

        # проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                # если есть такой username?
                if result:
                    # проверка пароля
                    if check_password(result[3], passw):
                        try:
                            # Внимание! Двойные кавычки здесь не пройдут!
                            if result[4] == True:
                                #это админ
                                sql_expr = 'SELECT * FROM public.advert'
                            else:
                                sql_expr = f'SELECT * FROM public.advert JOIN public.user ON public.user.id=public.advert.user_id WHERE user_id={result[0]}'
                            await cursor.execute(sql_expr)
                            result = await cursor.fetchall()

                        except my_exception.DBSelectError:
                            if config.DEBUG:
                                print('Ошибка cursor.execute(query)')
                            raise web.HTTPBadRequest
                        # psycopg2.ProgrammingError: commit cannot be used in asynchronous mode
                        # conn.commit()
                        response = []
                        #если был запрос конкретного объявления
                        advert_id = self.request.match_info.get('advs_id')  # получаем номер объявления
                        if advert_id != None:
                            advert_id=int(advert_id)

                        for res in result:
                            item = {}
                            item['title'] = res[1]
                            item['body'] = res[2]
                            item['user_id'] = res[4]
                            if advert_id:
                                if res[0] == advert_id:
                                    response.append(item)
                            else:
                                response.append(item)
                        return web.json_response(response)

                    else:
                        print('Неверный пароль!')
                        raise web.HTTPUnauthorized()

                else:  # не нашли такого пользователя
                    print('Нет такого пользователя!')
                    raise web.HTTPNotFound()

    async def delete(self):
        # Если мы сюда попали, значит проверка json пройдена:
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка пользователя
        # подготовка к декодированию:
        auth_for_64decode = auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0]  # логин
        passw = credential[1]  # пароль

        # проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                # если есть такой username?
                if result:
                    # проверка пароля
                    if check_password(result[3], passw):
                        # есть ли объявление таким id?
                        advert_id = self.request.match_info.get('advs_id')  # получаем номер объявления
                        if advert_id == None:
                            raise web.HTTPNotFound()
                        else:
                            advert_id = int(advert_id)

                        await cursor.execute(f'SELECT id, user_id from public.advert where public.advert.id={advert_id}')
                        result_ad = await cursor.fetchone()
                        if result_ad == None:
                            raise web.HTTPNotFound()

                        # username только свои объявления удаляет. Admin Может все!)
                        if (result[4] == True) or (result[0] == result_ad[1]):
                            try:
                                sql_expr = f'Delete from public.advert where id={advert_id}'
                                await cursor.execute(sql_expr)

                            except my_exception.DBDeleteError:
                                if config.DEBUG:
                                    print('Ошибка cursor.execute(query)')
                                raise web.HTTPBadRequest

                            response = []
                            item = {}
                            item['Result'] = 'Successful removal'
                            item['advert_id'] = advert_id
                            response.append(item)

                            return web.json_response(response)
                        else:
                            if config.DEBUG:
                                print('Отсутствуют права на удаление!')
                            raise web.HTTPUnauthorized()

                    else:
                        if config.DEBUG:
                            print('Неверный пароль!')
                        raise web.HTTPUnauthorized()

                else:  # не нашли такого пользователя
                    if config.DEBUG:
                        print('Нет такого пользователя!')
                    raise web.HTTPNotFound()

    @validate('json', ADVERT_CREATE)
    async def put(self):
        # Если мы сюда попали, значит проверка json пройдена:
        # проверка авторизации
        auth = self.request.headers.get('Authorization')
        if auth is None:
            raise web.HTTPUnauthorized()  # not authorization

        # проверка пользователя
        # подготовка к декодированию:
        auth_for_64decode = auth.split(' ')
        pre_credential = (base64.b64decode(auth_for_64decode[1])).decode('utf-8')

        credential = pre_credential.split(':')
        username = credential[0]  # логин
        passw = credential[1]  # пароль

        # проверка credential
        pg_pool = self.request.app['pg_pool']
        # подключаемя к БД и забираем инфу
        async with pg_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT * from public.user where username like \'{username}\'')
                result = await cursor.fetchone()
                # если есть такой username?
                if result:
                    # проверка пароля
                    if check_password(result[3], passw):
                        # есть ли объявление таким id?
                        advert_id = self.request.match_info.get('advs_id')  # получаем номер объявления
                        if advert_id == None:
                            raise web.HTTPNotFound()
                        else:
                            advert_id = int(advert_id)

                        await cursor.execute(
                            f'SELECT id, user_id from public.advert where public.advert.id={advert_id}')
                        result_ad = await cursor.fetchone()
                        if result_ad == None:
                            raise web.HTTPNotFound()

                        # username только свои объявления обновляет. Admin Может все!)
                        if (result[4] == True) or (result[0] == result_ad[1]):
                            try:
                                # сохраняем обновление объявления в БД
                                json_req = await self.request.json()
                                title = json_req.get('title')
                                body = json_req.get('body')

                                sql_expr = f'UPDATE public.advert SET title=\'{title}\', body=\'{body}\' WHERE public.advert.id={advert_id}'
                                await cursor.execute(sql_expr)

                            except my_exception.DBUpdateError:
                                if config.DEBUG:
                                    print('Ошибка cursor.execute(query)')
                                raise web.HTTPBadRequest

                            response = []
                            item = {}
                            item['Result'] = 'Successful update'
                            item['title'] = title
                            item['body'] = body
                            item['advert_id'] = advert_id
                            response.append(item)

                            return web.json_response(response)
                        else:
                            if config.DEBUG:
                                print('Отсутствуют права на обновление!')
                            raise web.HTTPUnauthorized()

                    else:
                        if config.DEBUG:
                            print('Неверный пароль!')
                        raise web.HTTPUnauthorized()

                else:  # не нашли такого пользователя
                    if config.DEBUG:
                        print('Нет такого пользователя!')
                    raise web.HTTPNotFound()