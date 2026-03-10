class DomainException(Exception):
    """Base class for all domain exceptions"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)

class NotFoundException(DomainException):
    def __init__(self, message: str = "Entity not found"):
        super().__init__(message)
