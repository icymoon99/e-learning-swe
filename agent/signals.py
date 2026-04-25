"""Agent 应用启动信号 — 注册内置 CLI 执行器到内存"""


def register_builtin_executors():
    """将代码中定义的 Executor 插件注册到 ExecutorRegistry。

    在 AppConfig.ready() 时调用，确保 Agent 启动时
    所有内置执行器已注册到内存注册表。
    """
    from sandbox.executors.base import ExecutorRegistry
    from sandbox.executors.trae_executor import TraeExecutor

    ExecutorRegistry.register(TraeExecutor())
