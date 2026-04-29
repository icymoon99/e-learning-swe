"""Django-Q2 异步任务函数"""

import logging

logger = logging.getLogger(__name__)

# AI 回复内容最大长度
AI_CONTENT_MAX_LENGTH = 2000


def execute_task_conversation(
    conversation_id: str,
    agent_code: str,
    task_id: str,
    execution_log_id: str,
    git_token: str = "",
) -> None:
    """异步执行任务指令

    Args:
        conversation_id: ElTaskConversation ULID
        agent_code: Agent 编码
        task_id: ElTask ULID
        execution_log_id: ElAgentExecutionLog ULID
        git_token: Git Token 实际值（从 ElGitSource.token 获取）
    """
    from task.models import ElTaskConversation, ElTask
    from agent.models import ElAgent, ElAgentExecutionLog
    from agent.orchestrator import orchestrator

    try:
        conv = ElTaskConversation.objects.get(id=conversation_id)
        task = ElTask.objects.get(id=task_id)
        agent = ElAgent.objects.get(code=agent_code)
        execution_log = ElAgentExecutionLog.objects.get(id=execution_log_id)
    except (
        ElTaskConversation.DoesNotExist,
        ElTask.DoesNotExist,
        ElAgent.DoesNotExist,
        ElAgentExecutionLog.DoesNotExist,
    ):
        logger.error(
            "[Task] 执行参数不存在 - conv:%s, task:%s, agent:%s, log:%s",
            conversation_id, task_id, agent_code, execution_log_id,
        )
        return

    try:
        # 调用编排器执行 Agent
        result = orchestrator.execute(
            agent_id=str(agent.id),
            message=conv.content,
            thread_id=execution_log.thread_id,
            agent_code=agent_code,
            task_branch=task.source_branch,
            git_repo_url=(
                task.git_source.repo_url
                if task.git_source
                else ""
            ),
            git_platform=(
                task.git_source.platform
                if task.git_source
                else ""
            ),
            git_token=git_token,
            task_id=task_id,
        )

        # 更新执行日志状态
        execution_log.status = result.get("status", "failed")
        execution_log.result = result.get("result")
        execution_log.error_message = result.get("error_message")
        update_fields = ["status", "updated_at"]
        if execution_log.result is not None:
            update_fields.append("result")
        if execution_log.error_message is not None:
            update_fields.append("error_message")
        execution_log.save(update_fields=update_fields)

        # 创建 AI 回复对话
        result_content = result.get("result")
        if result_content is not None:
            ElTaskConversation.objects.create(
                task=task,
                content=str(result_content)[:AI_CONTENT_MAX_LENGTH],
                comment_type="ai",
                agent_code=agent_code,
                execution_log=execution_log,
            )

        logger.info(
            "[Task] 任务指令执行完成 - task:%s, agent:%s",
            task_id, agent_code,
        )

    except Exception as e:
        logger.exception(
            "[Task] 任务指令执行失败 - task:%s, agent:%s: %s",
            task_id, agent_code, e,
        )
        execution_log.status = "failed"
        execution_log.error_message = str(e)[:1000]
        execution_log.save(
            update_fields=["status", "error_message", "updated_at"]
        )
