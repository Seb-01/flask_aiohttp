import jsonschema
from aiohttp import request, web
import config

def validate(source: str, req_schema: dict):
    """Валидатор входящих запросов"""
    print('Работает декоратор!')
    def decorator(func):

        async def wrapper(*args, **kwargs):
            #getattr позволяет получить значение атрибута объекта по его имени
            #нужно убедиться, что в request передали json с телом запроса
            #функция getattr() возвращает значение атрибута указанного объекта object по его имени name

            #если ничего не передано
            try:
                # Request object can be retrieved by View.request property
                inst = await args[0].request.json()

            except AttributeError as e:
                if config.DEBUG:
                    print(e)
                raise web.HTTPBadRequest

            try:
                jsonschema.validate(
                    # getattr(object, name, default)
                    # Параметры: object - объект, значение атрибута которого требуется получить
                    # name - имя атрибута объект, должно быть строкой
                    # default - значение по умолчанию, которое будет возвращено, если имя атрибута name отсутствует.
                    # Возвращаемое значение: значение именованного атрибута объекта
                    inst, schema=req_schema,
                )
            except jsonschema.ValidationError as e:
                if config.DEBUG:
                    print(e)
                raise web.HTTPBadRequest

            return await func(*args, **kwargs)

        # После того, как к функции применен декоратор, её атрибут __name__ изменился на имя внутренней функции
        # wrapper() декоратора. Хотя технически это верно, но это не очень полезная информация для IDE
        # и процесса отладки программы. Чтобы предотвратить смену атрибута __name__ и документации декорируемой функции:
        # Renaming the function name:
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
