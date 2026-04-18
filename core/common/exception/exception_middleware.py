import logging

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import TokenError

from .api_status_enum import ResponseStatus
from .api_exception import ApiException

logger = logging.getLogger(__name__)


class ExceptionGlobalMiddleware(MiddlewareMixin):
    """
    Django全局异常处理器
    用于捕获和处理应用程序中的所有异常
    """

    def process_exception(self, request, exception):
        # 直接抛出 django admin 的异常
        if str(request.path).startswith("/admin/"):
            return None

        logger.error("Exception occurred", exc_info=exception)

        if isinstance(exception, ApiException):
            # 系统自定义异常
            ex_data = {
                "code": exception.code,
                "message": exception.msg,
                "content": None,
            }
            return JsonResponse(data=ex_data)
        elif isinstance(exception, TokenError):
            # simple-jwt token 认证失败
            ex_data = {
                "code": ResponseStatus.UNAUTHORIZED.code,
                "message": ResponseStatus.UNAUTHORIZED.message,
                "content": None,
            }
            return JsonResponse(data=ex_data, status=401)
        else:
            # 未知异常
            message = str(exception) or ResponseStatus.ERROR.message
            ex_data = {
                "code": ResponseStatus.ERROR.code,
                "message": message,
                "content": None,
            }
            return JsonResponse(data=ex_data, status=500)
