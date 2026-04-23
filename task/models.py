from django.db import models

from core.models import AbstractBaseModel

TASK_STATUS_CHOICES = (
    ("open", "进行中"),
    ("closed", "已关闭"),
)

CONVERSATION_TYPE_CHOICES = (
    ("user", "用户指令"),
    ("ai", "AI 回复"),
    ("system", "系统通知"),
)


class ElTask(AbstractBaseModel):
    """任务"""

    title = models.CharField(max_length=500, verbose_name="标题")
    description = models.TextField(default="", verbose_name="描述")
    git_source = models.ForeignKey(
        "git_source.ElGitSource",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="仓库源",
    )
    source_branch = models.CharField(
        max_length=128,
        default="main",
        verbose_name="源分支",
    )
    status = models.CharField(
        max_length=32,
        choices=TASK_STATUS_CHOICES,
        default="open",
        verbose_name="状态",
    )

    class Meta:
        db_table = "el_task"
        verbose_name = "任务"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"


class ElTaskConversation(AbstractBaseModel):
    """任务对话/指令流"""

    task = models.ForeignKey(
        ElTask,
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name="关联任务",
    )
    content = models.TextField(verbose_name="内容")
    comment_type = models.CharField(
        max_length=32,
        choices=CONVERSATION_TYPE_CHOICES,
        verbose_name="类型",
    )
    agent_code = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="关联 Agent 编码",
    )
    execution_log = models.ForeignKey(
        "agent.ElAgentExecutionLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="关联执行日志",
    )

    class Meta:
        db_table = "el_task_conversation"
        verbose_name = "任务对话"
        verbose_name_plural = verbose_name
        ordering = ["created_at"]

    def __str__(self):
        type_label = self.get_comment_type_display()
        agent = f" ({self.agent_code})" if self.agent_code else ""
        return f"{type_label}{agent}: {self.content[:50]}"

    def get_comment_type_display(self):
        mapping = dict(CONVERSATION_TYPE_CHOICES)
        return mapping.get(self.comment_type, self.comment_type)


class ElTaskMemory(AbstractBaseModel):
    """任务级 Agent 记忆记录"""

    STATUS_CHOICES = (
        ("success", "成功"),
        ("failed", "失败"),
    )

    task = models.ForeignKey(
        "task.ElTask",
        on_delete=models.CASCADE,
        related_name="memories",
        verbose_name="所属任务",
    )
    agent = models.ForeignKey(
        "agent.ElAgent",
        on_delete=models.SET_NULL,
        null=True,
        related_name="task_memories",
        verbose_name="执行 Agent",
    )
    thread_id = models.CharField(max_length=128, verbose_name="线程 ID")
    execution_order = models.PositiveIntegerField(verbose_name="执行顺序号")
    summary = models.TextField(verbose_name="Agent 执行摘要")
    commit_message = models.TextField(null=True, blank=True, verbose_name="Git 提交信息")
    pr_url = models.URLField(null=True, blank=True, verbose_name="PR 地址")
    commit_hash = models.CharField(max_length=128, null=True, blank=True, verbose_name="Commit Hash")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, verbose_name="执行状态")
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")

    class Meta:
        db_table = "el_task_memory"
        ordering = ["execution_order"]
        verbose_name = "任务记忆"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"TaskMemory(task={self.task_id}, order={self.execution_order})"
