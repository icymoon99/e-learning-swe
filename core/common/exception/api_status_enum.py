from enum import Enum


class ResponseStatus(Enum):
    """
    状态码和描述
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    OK = (0, "ok")
    ERROR = (1, "服务内部错误，请联系管理员")
    UNAUTHORIZED = (401, "用户未登录或token已失效")
    NOT_FOUND = (404, "资源不存在")
    PARAMETER_ERROR = (1000, "参数错误")
