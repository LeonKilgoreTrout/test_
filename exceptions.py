class AppException(Exception):
    """ Данное исключение связано с работой бота """


class ContextNotFoundException(AppException):
    """ Вероятно, вы неверно оформили сценарий общения и/или не передали ни одного контекста """
