from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from agent.context import GitContext
from agent.middleware.git_sandbox import GitSandboxMiddleware, _build_auth_clone_url


def _make_runtime(context: GitContext | None = None, agent_code: str = "test-agent"):
    """构造模拟 runtime 对象"""
    runtime = MagicMock()
    runtime.context = context
    runtime.config = MagicMock()
    runtime.config.configurable = {"agent_code": agent_code, "thread_id": "thread-123"}
    return runtime


def _make_mock_backend():
    """构造模拟后端"""
    backend = MagicMock()
    backend.execute.return_value = MagicMock(exit_code=0, output="")
    return backend


class TestBuildAuthCloneUrl:
    """_build_auth_clone_url 函数测试"""

    def test_gitlab_embeds_oauth2_token(self):
        """GitLab 应使用 oauth2:{token}@ 格式"""
        url = _build_auth_clone_url(
            "http://192.168.1.38/oio-smart/repo.git",
            "secret-token",
            "gitlab",
        )
        assert url == "http://oauth2:secret-token@192.168.1.38/oio-smart/repo.git"

    def test_github_embeds_token(self):
        """GitHub 应使用 {token}@ 格式"""
        url = _build_auth_clone_url(
            "https://github.com/owner/repo.git",
            "ghp_xxxx",
            "github",
        )
        assert url == "https://ghp_xxxx@github.com/owner/repo.git"

    def test_gitee_embeds_oauth2_token(self):
        """Gitee 应使用 oauth2:{token}@ 格式"""
        url = _build_auth_clone_url(
            "https://gitee.com/owner/repo.git",
            "gitee-token",
            "gitee",
        )
        assert url == "https://oauth2:gitee-token@gitee.com/owner/repo.git"

    def test_empty_token_returns_original(self):
        """Token 为空时应返回原始 URL"""
        url = _build_auth_clone_url("https://github.com/owner/repo.git", "", "github")
        assert url == "https://github.com/owner/repo.git"

    def test_ssh_url_returns_unchanged(self):
        """SSH URL 不应修改"""
        url = _build_auth_clone_url(
            "git@github.com:owner/repo.git", "ghp_xxxx", "github"
        )
        assert url == "git@github.com:owner/repo.git"

    def test_unknown_platform_uses_oauth2(self):
        """未知平台应使用 oauth2:{token}@ 格式"""
        url = _build_auth_clone_url(
            "https://git.example.com/owner/repo.git",
            "token123",
            "custom",
        )
        assert url == "https://oauth2:token123@git.example.com/owner/repo.git"


class TestGitSandboxMiddlewareBeforeAgent:
    """before_agent 钩子测试"""

    def test_skips_without_git_context(self):
        """没有 GitContext 时，before_agent 应该跳过"""
        middleware = GitSandboxMiddleware(backend=MagicMock())
        runtime = _make_runtime(context=None)
        runtime.context = None

        result = middleware.before_agent({}, runtime)
        assert result is None

    def test_creates_work_branch(self):
        """有 GitContext 时，应该执行 clone 和分支创建"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abc12345",
            task_branch="feature/auth",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        runtime = _make_runtime(context=ctx)

        result = middleware.before_agent({}, runtime)

        assert result is None
        execute_calls = [call[0][0] for call in backend.execute.call_args_list]
        assert any("git clone" in c for c in execute_calls)
        assert any("git checkout -b" in c for c in execute_calls)

    def test_marks_context_none_on_clone_failure(self):
        """clone 失败时，_git_context 应设为 None 以跳过后续操作"""
        backend = MagicMock()
        backend.execute.return_value = MagicMock(exit_code=1, output="fatal: not found")

        middleware = GitSandboxMiddleware(backend=backend)
        ctx = GitContext(
            thread_id="t1",
            task_branch="main",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        runtime = _make_runtime(context=ctx)

        middleware.before_agent({}, runtime)

        assert middleware._git_context is None

    def test_work_branch_naming(self):
        """工作分支名应为 {task_branch}_{thread_id[:8]}_{agent_code}"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abcdef12",
            task_branch="feat/login",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        runtime = _make_runtime(context=ctx, agent_code="coder")

        middleware.before_agent({}, runtime)

        execute_calls = [call[0][0] for call in backend.execute.call_args_list]
        assert any("feat/login_thread-a_coder" in c for c in execute_calls)

    def test_clone_url_embeds_token_for_gitlab(self):
        """有 git_token 时，clone URL 应嵌入认证信息"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abc12345",
            task_branch="feature/auth",
            git_repo_url="http://192.168.1.38/oio-smart/repo.git",
            git_platform="gitlab",
            git_token="secret-token",
        )
        runtime = _make_runtime(context=ctx)

        middleware.before_agent({}, runtime)

        execute_calls = [call[0][0] for call in backend.execute.call_args_list]
        assert any(
            "git clone http://oauth2:secret-token@192.168.1.38/oio-smart/repo.git ." in c
            for c in execute_calls
        )

    def test_clone_without_token_uses_plain_url(self):
        """无 git_token 时，应使用原始 URL 克隆"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abc12345",
            task_branch="feature/auth",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        runtime = _make_runtime(context=ctx)

        middleware.before_agent({}, runtime)

        execute_calls = [call[0][0] for call in backend.execute.call_args_list]
        assert any(
            "git clone https://github.com/owner/repo.git ." in c
            for c in execute_calls
        )


class TestGitSandboxMiddlewareAfterAgent:
    """after_agent 钩子测试"""

    def test_skips_without_git_context(self):
        """没有 GitContext 时，after_agent 应该跳过"""
        middleware = GitSandboxMiddleware(backend=MagicMock())
        runtime = _make_runtime(context=None)
        runtime.context = None

        result = middleware.after_agent({}, runtime)
        assert result is None

    def test_commits_and_creates_pr(self):
        """解析 Agent JSON 输出并执行 commit/push/PR"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abc12345",
            task_branch="feature/auth",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
            git_token_secret="TEST_TOKEN",
        )
        runtime = _make_runtime(context=ctx)
        middleware._git_context = ctx
        middleware._agent_code = "test-agent"

        from langchain_core.messages import AIMessage
        state = {
            "messages": [
                AIMessage(
                    content='{"commit_message": "feat: add login", "pr_title": "Add login", "pr_description": "Implemented login flow", "summary": "Done"}'
                ),
            ]
        }

        with patch.dict(os.environ, {"TEST_TOKEN": "fake-token"}):
            with patch(
                "agent.middleware.git_sandbox._get_platform"
            ) as mock_get_platform:
                mock_platform = MagicMock()
                mock_platform.create_pr.return_value = {
                    "url": "https://github.com/owner/repo/pull/1",
                    "number": 1,
                }
                mock_get_platform.return_value = mock_platform

                result = middleware.after_agent(state, runtime)

                assert result is not None
                assert result["git_pr_url"] == "https://github.com/owner/repo/pull/1"
                assert result["git_pr_number"] == 1

    def test_pr_creation_uses_git_token_directly(self):
        """有 git_token 时，应直接使用 token 值而非环境变量"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abc12345",
            task_branch="feature/auth",
            git_repo_url="http://192.168.1.38/oio-smart/repo.git",
            git_platform="gitlab",
            git_token="direct-token-value",
        )
        runtime = _make_runtime(context=ctx)
        middleware._git_context = ctx
        middleware._agent_code = "test-agent"

        from langchain_core.messages import AIMessage
        state = {
            "messages": [
                AIMessage(
                    content='{"commit_message": "feat: x", "pr_title": "T", "pr_description": "D"}'
                ),
            ]
        }

        with patch(
            "agent.middleware.git_sandbox._get_platform"
        ) as mock_get_platform:
            mock_platform = MagicMock()
            mock_platform.create_pr.return_value = {
                "url": "http://192.168.1.38/pull/1",
                "number": 1,
            }
            mock_get_platform.return_value = mock_platform

            result = middleware.after_agent(state, runtime)

            assert result is not None
            mock_get_platform.assert_called_once_with(
                "gitlab", "direct-token-value", "http://192.168.1.38/oio-smart/repo.git"
            )

    def test_push_sets_auth_url_when_token_available(self):
        """有 token 时，push 前应设置认证 URL"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="thread-abc12345",
            task_branch="feature/auth",
            git_repo_url="http://192.168.1.38/oio-smart/repo.git",
            git_platform="gitlab",
            git_token="secret-token",
        )
        runtime = _make_runtime(context=ctx)
        middleware._git_context = ctx
        middleware._agent_code = "test-agent"

        from langchain_core.messages import AIMessage
        state = {
            "messages": [
                AIMessage(
                    content='{"commit_message": "feat: x", "pr_title": "T", "pr_description": "D"}'
                ),
            ]
        }

        with patch(
            "agent.middleware.git_sandbox._get_platform",
        ) as mock_get_platform:
            mock_platform = MagicMock()
            mock_platform.create_pr.return_value = None
            mock_get_platform.return_value = mock_platform
            middleware.after_agent(state, runtime)

        execute_calls = [call[0][0] for call in backend.execute.call_args_list]
        assert any(
            "git remote set-url origin http://oauth2:secret-token@192.168.1.38/oio-smart/repo.git" in c
            for c in execute_calls
        )

    def test_uses_defaults_when_json_parse_fails(self):
        """Agent 未输出合法 JSON 时，使用默认 commit message"""
        backend = _make_mock_backend()
        middleware = GitSandboxMiddleware(backend=backend)

        ctx = GitContext(
            thread_id="t1",
            task_branch="main",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        runtime = _make_runtime(context=ctx)
        middleware._git_context = ctx
        middleware._agent_code = "test-agent"

        from langchain_core.messages import AIMessage
        state = {
            "messages": [
                AIMessage(content="I finished the work"),
            ]
        }

        # Token 不存在，PR 步骤跳过，但 commit/push 应执行
        result = middleware.after_agent(state, runtime)

        execute_calls = [call[0][0] for call in backend.execute.call_args_list]
        assert any("git add -A" in c for c in execute_calls)
        assert any("git commit" in c for c in execute_calls)


class TestParseAgentOutput:
    """_parse_agent_output 内部方法测试"""

    def test_parses_valid_json(self):
        middleware = GitSandboxMiddleware(backend=MagicMock())
        from langchain_core.messages import AIMessage
        state = {
            "messages": [
                AIMessage(
                    content='{"commit_message": "fix: bug", "pr_title": "Bug fix", "pr_description": "Fixed it"}'
                ),
            ]
        }
        commit, title, desc = middleware._parse_agent_output(state)
        assert commit == "fix: bug"
        assert title == "Bug fix"
        assert desc == "Fixed it"

    def test_parses_json_in_code_block(self):
        middleware = GitSandboxMiddleware(backend=MagicMock())
        from langchain_core.messages import AIMessage
        state = {
            "messages": [
                AIMessage(
                    content="```\njson\n{\"commit_message\": \"feat: x\", \"pr_title\": \"T\", \"pr_description\": \"D\"}\n```"
                ),
            ]
        }
        commit, title, desc = middleware._parse_agent_output(state)
        assert commit == "feat: x"

    def test_empty_messages_returns_defaults(self):
        middleware = GitSandboxMiddleware(backend=MagicMock())
        state = {"messages": []}
        commit, title, desc = middleware._parse_agent_output(state)
        assert commit  # 有默认值
        assert title  # 有默认值

    def test_no_messages_returns_defaults(self):
        middleware = GitSandboxMiddleware(backend=MagicMock())
        state = {}
        commit, title, desc = middleware._parse_agent_output(state)
        assert commit
        assert title

    def test_ignores_tool_messages(self):
        """应该跳过 tool 类型的消息"""
        middleware = GitSandboxMiddleware(backend=MagicMock())
        from langchain_core.messages import AIMessage, ToolMessage
        state = {
            "messages": [
                ToolMessage(content="tool output", tool_call_id="1"),
                AIMessage(
                    content='{"commit_message": "real msg", "pr_title": "T", "pr_description": "D"}'
                ),
            ]
        }
        commit, title, desc = middleware._parse_agent_output(state)
        assert commit == "real msg"
