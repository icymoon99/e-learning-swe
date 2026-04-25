from django.db import models
from core.models import AbstractBaseModel
from llm.models import ElLLMModel


AGENT_STATUS_CHOICES = (
    ("active", "启用"),
    ("inactive", "停用"),
    ("deleted", "已删除"),
)

EXECUTION_STATUS_CHOICES = (
    ("running", "执行中"),
    ("completed", "已完成"),
    ("failed", "失败"),
)


class ElAgent(AbstractBaseModel):
    """Agent 配置模型"""

    code = models.CharField(max_length=128, unique=True, db_index=True, verbose_name="Agent 编码")
    name = models.CharField(max_length=255, default="", verbose_name="Agent 名称")
    description = models.TextField(default="", verbose_name="功能描述")
    system_prompt = models.TextField(default="", verbose_name="系统提示词")
    llm_model = models.ForeignKey(
        ElLLMModel, on_delete=models.PROTECT,
        null=True, blank=True, related_name="agents",
        verbose_name="LLM 模型"
    )
    status = models.CharField(
        max_length=32,
        choices=AGENT_STATUS_CHOICES,
        default="active",
        db_index=True,
        verbose_name="状态",
    )
    metadata = models.JSONField(default=dict, verbose_name="扩展配置")
    executor = models.ForeignKey(
        'ElExecutor', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='agents', verbose_name='CLI 执行器'
    )

    class Meta:
        db_table = "el_agent"
        verbose_name = "Agent 配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.code})"


class ElAgentExecutionLog(AbstractBaseModel):
    """Agent 执行日志"""

    agent = models.ForeignKey(
        ElAgent, on_delete=models.CASCADE, verbose_name="关联 Agent", related_name="executions"
    )
    thread_id = models.CharField(max_length=128, db_index=True, verbose_name="线程 ID")
    status = models.CharField(
        max_length=32,
        choices=EXECUTION_STATUS_CHOICES,
        default="running",
        verbose_name="执行状态",
    )
    events = models.JSONField(default=list, verbose_name="原始事件流")
    result = models.JSONField(null=True, blank=True, verbose_name="执行结果")
    error_message = models.TextField(default="", verbose_name="错误信息")

    # Git 工作流结果
    git_pr_url = models.CharField(
        max_length=512, default="", blank=True, verbose_name="PR 地址"
    )
    git_pr_number = models.IntegerField(
        null=True, blank=True, verbose_name="PR 编号"
    )
    git_commit_hash = models.CharField(
        max_length=64, default="", blank=True, verbose_name="最后一次 commit hash"
    )

    class Meta:
        db_table = "el_agent_execution_log"
        verbose_name = "Agent 执行日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.agent.name} - {self.thread_id} ({self.status})"


class ElExecutor(AbstractBaseModel):
    """CLI 执行器 — 系统中可用的编程工具定义"""

    code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='执行器编码')
    name = models.CharField(max_length=100, verbose_name='显示名称')
    enabled = models.BooleanField(default=True, db_index=True, verbose_name='是否启用')
    timeout = models.IntegerField(default=3600, verbose_name='超时时间（秒）')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='扩展配置')

    class Meta:
        db_table = 'el_agent_executor'
        ordering = ['created_at']
        verbose_name = 'CLI 执行器'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f'{self.name} ({self.code})'
