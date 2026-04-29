"""沙箱类型 Schema 定义

每种沙箱类型的 metadata 字段元信息，用于前端动态表单渲染和后端校验。
"""

SANDBOX_TYPE_SCHEMAS = {
    "localdocker": {
        "label": "本地 Docker",
        "fields": {
            "image": {
                "type": "string", "required": True,
                "default": "sandbox:latest",
                "label": "镜像", "hint": "Docker 镜像名称或路径",
            },
            "work_dir": {
                "type": "string", "required": True,
                "default": "workspace",
                "label": "工作目录", "hint": "相对于镜像 WORKDIR 的目录名称，禁止绝对路径",
            },
        },
    },
    "remotedocker": {
        "label": "远程 Docker",
        "fields": {
            "image": {
                "type": "string", "required": True,
                "default": "sandbox:latest",
                "label": "镜像", "hint": "Docker 镜像名称或路径",
            },
            "work_dir": {
                "type": "string", "required": True,
                "default": "workspace",
                "label": "工作目录", "hint": "相对于镜像 WORKDIR 的目录名称，禁止绝对路径",
            },
            "ssh_host": {
                "type": "string", "required": True,
                "label": "SSH 地址", "hint": "远程服务器地址",
            },
            "ssh_port": {
                "type": "number", "required": False,
                "default": 22,
                "label": "SSH 端口", "hint": "",
            },
            "ssh_user": {
                "type": "string", "required": True,
                "label": "SSH 用户", "hint": "",
            },
            "ssh_key_path": {
                "type": "string", "required": False,
                "label": "SSH 密钥路径",
                "hint": "SSH 私钥文件路径，与密码至少填一个",
            },
            "ssh_password": {
                "type": "string", "required": False,
                "label": "SSH 密码", "hint": "SSH 密码，与密钥路径至少填一个",
            },
        },
    },
    "localsystem": {
        "label": "本地系统",
        "fields": {
            "root_path": {
                "type": "string", "required": True,
                "default": "sandbox/",
                "label": "沙箱根目录",
                "hint": "相对于 CMD 工作目录的路径，禁止使用 / 开头的绝对路径",
            },
            "work_dir": {
                "type": "string", "required": True,
                "default": "workspace",
                "label": "工作目录", "hint": "root_path 下的子目录，禁止绝对路径",
            },
        },
    },
    "remotesystem": {
        "label": "远程系统",
        "fields": {
            "root_path": {
                "type": "string", "required": True,
                "default": "sandbox/",
                "label": "沙箱根目录",
                "hint": "相对于 CMD 工作目录的路径，禁止使用 / 开头的绝对路径",
            },
            "work_dir": {
                "type": "string", "required": True,
                "default": "workspace",
                "label": "工作目录", "hint": "root_path 下的子目录，禁止绝对路径",
            },
            "ssh_host": {
                "type": "string", "required": True,
                "label": "SSH 地址", "hint": "远程服务器地址",
            },
            "ssh_port": {
                "type": "number", "required": False,
                "default": 22,
                "label": "SSH 端口", "hint": "",
            },
            "ssh_user": {
                "type": "string", "required": True,
                "label": "SSH 用户", "hint": "",
            },
            "ssh_key_path": {
                "type": "string", "required": False,
                "label": "SSH 密钥路径",
                "hint": "SSH 私钥文件路径，与密码至少填一个",
            },
            "ssh_password": {
                "type": "string", "required": False,
                "label": "SSH 密码", "hint": "SSH 密码，与密钥路径至少填一个",
            },
        },
    },
}


def get_type_schema(sandbox_type: str) -> dict:
    """获取指定沙箱类型的 schema。"""
    if sandbox_type not in SANDBOX_TYPE_SCHEMAS:
        raise ValueError(f"未知沙箱类型: {sandbox_type}")
    return SANDBOX_TYPE_SCHEMAS[sandbox_type]


def get_all_type_schemas() -> dict:
    """返回所有沙箱类型的 schema。"""
    return {"types": SANDBOX_TYPE_SCHEMAS}
