from rest_framework.renderers import JSONRenderer

from .ulid_encoder import ULIDEncoder


class ULIDJSONRenderer(JSONRenderer):
    """
    一个自定义的 JSON 渲染器，使用 ULIDEncoder 来处理 ULID 字段。
    """

    encoder_class = ULIDEncoder
