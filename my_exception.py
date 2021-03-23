class DBError(Exception):
    """Базовый класс для исключений операций с БД"""
    pass

class DBInsertError(DBError):
    """Вызывается, когда SQL Insert отрабатывается с ошибкой"""
    pass

class DBSelectError(DBError):
    """Вызывается, когда SQL Select отрабатывается с ошибкой"""
    pass

class DBDeleteError(DBError):
    """Вызывается, когда SQL Select отрабатывается с ошибкой"""
    pass

class DBUpdateError(DBError):
    """Вызывается, когда SQL Select отрабатывается с ошибкой"""
    pass