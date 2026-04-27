"""执行器 metadata Schema 定义。

每种执行器的 metadata 字段元信息，用于前端动态表单渲染和后端校验。
Schema 定义在代码中（不存 DB），DB 仅存储值。
"""

EXECUTOR_SCHEMAS = {
    "trae": {
        "env_vars": {
            "TRAECLI_PERSONAL_ACCESS_TOKEN": {
                "type": "password",
                "required": True,
                "label": "Personal Access Token",
                "hint": "Trae CLI 鉴权令牌",
            },
        },
        "cli_args": {},
    },
}


def get_executor_schema(code: str) -> dict:
    """获取指定执行器的 schema。"""
    if code not in EXECUTOR_SCHEMAS:
        raise ValueError(f"未知执行器类型: {code}")
    return EXECUTOR_SCHEMAS[code]


def get_all_executor_schemas() -> dict:
    """返回所有执行器的 schema。"""
    return dict(EXECUTOR_SCHEMAS)
