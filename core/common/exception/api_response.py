from rest_framework.response import Response

from rest_framework import status as drf_status

from .api_status_enum import ResponseStatus


class ApiResponse(Response):
    def __init__(
        self,
        status: ResponseStatus = ResponseStatus.OK,
        content=None,
        http_status=drf_status.HTTP_200_OK,
        headers=None,
        exception=False,
        **kwargs
    ):
        response = {
            "code": status.code,
            "message": status.message,
        }

        # data 的响应数据体
        if content is not None:
            response["content"] = content

        # 响应的其他内容
        response.update(kwargs)

        super().__init__(
            data=response, status=http_status, headers=headers, exception=exception
        )

    @staticmethod
    def ok(content=None, **kwargs):
        return ApiResponse(status=ResponseStatus.OK, content=content, **kwargs)

    @staticmethod
    def unauthorized(**kwargs):
        return ApiResponse(status=ResponseStatus.UNAUTHORIZED, **kwargs)

    @staticmethod
    def parameter_error(message=None, **kwargs):
        """
        参数错误时的响应
        """
        return ApiResponse(
            status=ResponseStatus.PARAMETER_ERROR, message=message, **kwargs
        )

    @staticmethod
    def error(status: ResponseStatus = ResponseStatus.ERROR, content=None, **kwargs):
        return ApiResponse(status=status, content=content, **kwargs)

    @staticmethod
    def not_found(message=None, **kwargs):
        """
        资源不存在时的响应
        """
        return ApiResponse(
            status=ResponseStatus.NOT_FOUND,
            message=message or ResponseStatus.NOT_FOUND.message,
            **kwargs
        )
