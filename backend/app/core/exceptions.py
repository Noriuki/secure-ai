class AppError(Exception):
    def __init__(self, message: str = "Application error") -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class ValidationAppError(AppError):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)
