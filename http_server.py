from aiohttp import web
from aiopg import pool
from functools import partial
from views import User, Users, Adverts

import sys, asyncio

import config

#проверочный
async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

# Зарегистрируем подключение к БД:
# Для начала опиши функцию для регистрации подключения к БД
async def register_connection(app: web.Application):
    #  действия во время старта приложения
    pg_pool = await pool.create_pool(config.POSTGRE_DSN)  # создаем пулл подключений (содержит несколько коннекторов)
    app['pg_pool'] = pg_pool  # записываем в контекст приложения. Словарь с ключем=имя_пула
    #код до yield является этапом инициализации (вызывается при запуске),
    # код после yield выполняется при очистке. У генератора должен быть только один выход.
    yield
    pg_pool.close()  # когда приложение завершит работу, пул закроется

async def get_app():

    app = web.Application()  # создаем приложение

    # регистрируем подключение к БД (чтобы не забыть при очистке обработать соответствующие сигналы)
    app.cleanup_ctx.append(partial(register_connection))

    #роутер настраиваем
    app.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])

    # есть же милиион способов:)
    app.router.add_view('/api/v1/users/{user_id:\d+}', User)
    app.router.add_view('/api/v1/users', Users)
    app.router.add_view('/api/v1/advs', Adverts)
    app.router.add_view('/api/v1/advs/{advs_id:\d+}', Adverts)

    return app

if __name__ == '__main__':

    #some issue with connection to DB on Windows on code, which work on Linux.
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = get_app()
    web.run_app(app, host='127.0.0.1', port=8080)  # запускаем приложение
