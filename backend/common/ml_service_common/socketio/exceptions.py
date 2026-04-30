from socketio.exceptions import ConnectionRefusedError as SocketIOConnectionRefusedError


class NotAuthenticatedError(SocketIOConnectionRefusedError):
    def __init__(self):
        super().__init__("User not authenticated.")


class NamespaceException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


class NotFoundException(NamespaceException):
    def __init__(self, message: str | None = None):
        super().__init__(message=message or "Not found.")


class ForbiddenException(NamespaceException):
    def __init__(self):
        super().__init__("Forbidden.")
