"""Кастомные исключения для бизнес-логики"""


class BusinessError(Exception):
    """Базовое исключение для бизнес-ошибок"""

    pass


class UserAlreadyExistsError(BusinessError):
    """Пользователь с таким email или username уже существует"""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"{field} already registered: {value}")


class InvalidCredentialsError(BusinessError):
    """Неверный username или пароль"""

    pass


class UserNotFoundError(BusinessError):
    """Пользователь не найден"""

    pass


class InvalidRefreshTokenError(BusinessError):
    """Невалидный refresh token"""

    pass


class ExpiredRefreshTokenError(BusinessError):
    """Истёкший refresh token"""

    pass


class FileTooLargeError(BusinessError):
    """Файл слишком большой"""

    pass


class InvalidFileError(BusinessError):
    """Невалидный файл"""

    pass
