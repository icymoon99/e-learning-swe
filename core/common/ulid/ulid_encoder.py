import json
from ulid import ULID


class ULIDEncoder(json.JSONEncoder):
    """
    自定义 JSON 编码器，用于将 ULID 对象序列化为字符串。
    """

    def default(self, obj):
        if isinstance(obj, ULID):
            return str(obj)
        return super().default(obj)
