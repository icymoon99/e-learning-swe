# 预置供应商定义（base_url 为 OpenAI 兼容 API 地址）

PRESET_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": [
            {"model_code": "gpt-4.1", "display_name": "GPT-4.1", "context_window": 1047576, "max_output_tokens": 32768},
            {"model_code": "gpt-4.1-mini", "display_name": "GPT-4.1 mini", "context_window": 1047576, "max_output_tokens": 32768},
            {"model_code": "gpt-4.1-nano", "display_name": "GPT-4.1 nano", "context_window": 1047576, "max_output_tokens": 32768},
            {"model_code": "gpt-4o", "display_name": "GPT-4o", "context_window": 128000, "max_output_tokens": 16384},
            {"model_code": "o3", "display_name": "o3", "context_window": 200000, "max_output_tokens": 100000},
            {"model_code": "o3-pro", "display_name": "o3 Pro", "context_window": 200000, "max_output_tokens": 100000},
            {"model_code": "o4-mini", "display_name": "o4-mini", "context_window": 200000, "max_output_tokens": 100000},
        ],
    },
    "anthropic": {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "models": [
            {"model_code": "claude-opus-4-6", "display_name": "Claude Opus 4.6", "context_window": 200000, "max_output_tokens": 32000},
            {"model_code": "claude-sonnet-4-6", "display_name": "Claude Sonnet 4.6", "context_window": 200000, "max_output_tokens": 64000},
            {"model_code": "claude-sonnet-4-5", "display_name": "Claude Sonnet 4.5", "context_window": 200000, "max_output_tokens": 64000},
            {"model_code": "claude-haiku-4-5", "display_name": "Claude Haiku 4.5", "context_window": 200000, "max_output_tokens": 8192},
        ],
    },
    "tongyi": {
        "name": "通义千问",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": [
            {"model_code": "qwen3-coder-plus", "display_name": "Qwen3 Coder Plus", "context_window": 262144, "max_output_tokens": 65536},
            {"model_code": "qwen3.6-plus", "display_name": "Qwen3.6 Plus", "context_window": 262144, "max_output_tokens": 65536},
            {"model_code": "qwen-max", "display_name": "Qwen-Max", "context_window": 131072, "max_output_tokens": 8192},
            {"model_code": "qwen-plus", "display_name": "Qwen-Plus", "context_window": 131072, "max_output_tokens": 8192},
            {"model_code": "qwen-turbo", "display_name": "Qwen-Turbo", "context_window": 1000000, "max_output_tokens": 8192},
        ],
    },
    "zhipu": {
        "name": "智谱 AI",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": [
            {"model_code": "glm-4.6", "display_name": "GLM-4.6", "context_window": 131072, "max_output_tokens": 4096},
            {"model_code": "glm-4-plus", "display_name": "GLM-4 Plus", "context_window": 131072, "max_output_tokens": 4096},
            {"model_code": "glm-4-flash", "display_name": "GLM-4 Flash", "context_window": 131072, "max_output_tokens": 4096},
            {"model_code": "glm-4-air", "display_name": "GLM-4 Air", "context_window": 131072, "max_output_tokens": 4096},
        ],
    },
    "kimi": {
        "name": "月之暗面 · Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "models": [
            {"model_code": "kimi-k2.5", "display_name": "Kimi K2.5", "context_window": 131072, "max_output_tokens": 65536},
            {"model_code": "kimi-k2.5-turbo", "display_name": "Kimi K2.5 Turbo", "context_window": 131072, "max_output_tokens": 65536},
            {"model_code": "moonshot-v1-128k", "display_name": "Moonshot v1 128K", "context_window": 131072, "max_output_tokens": 8192},
            {"model_code": "moonshot-v1-32k", "display_name": "Moonshot v1 32K", "context_window": 32768, "max_output_tokens": 8192},
        ],
    },
}
