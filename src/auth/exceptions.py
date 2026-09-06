# package-specific errors
class AuthError(Exception):
    """Base class for auth errors. Handled globally in src.main."""


class UserAlreadyExists(AuthError):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"A user with this {field} already exists")


class UserNotFound(AuthError):
    def __init__(self) -> None:
        super().__init__("User not found")


class InvalidCredentials(AuthError):
    def __init__(self) -> None:
        super().__init__("Incorrect email or password")


class InvalidToken(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid or expired token")


class InactiveUser(AuthError):
    def __init__(self) -> None:
        super().__init__("User account is inactive")
