from .api_status_enum import ResponseStatus


class ApiException(Exception):
    def __init__(
        self, status: ResponseStatus = None, msg: str = None, code: int = None
    ):
        if msg:
            self.msg = msg
            self.code = code if code else -1
        elif status:
            self.msg = status.msg
            self.code = status.code

    def __str__(self):
        return "ApiException: %s" % self.msg
