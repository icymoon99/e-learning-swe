from __future__ import annotations

import dataclasses

import pytest

from agent.context import GitContext


class TestGitContext:
    """GitContext 不可变 dataclass 测试"""

    def test_create_with_required_fields(self):
        """测试使用必需字段创建"""
        ctx = GitContext(
            thread_id="thread-001",
            task_branch="feature/auth",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        assert ctx.thread_id == "thread-001"
        assert ctx.task_branch == "feature/auth"
        assert ctx.git_repo_url == "https://github.com/owner/repo.git"
        assert ctx.git_platform == "github"

    def test_defaults_for_optional_fields(self):
        """测试可选字段默认值"""
        ctx = GitContext(
            thread_id="t1",
            task_branch="main",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        assert ctx.git_token == ""

    def test_custom_optional_fields(self):
        """测试自定义可选字段"""
        ctx = GitContext(
            thread_id="t1",
            task_branch="main",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
            git_token="ghp_xxxx",
        )
        assert ctx.git_token == "ghp_xxxx"

    def test_is_dataclass(self):
        """验证 GitContext 是 dataclass"""
        assert dataclasses.is_dataclass(GitContext)

    def test_frozen_cannot_modify(self):
        """尝试修改 frozen dataclass 会抛出 FrozenInstanceError"""
        ctx = GitContext(
            thread_id="t1",
            task_branch="main",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.thread_id = "modified"  # type: ignore[misc]

    def test_hashable(self):
        """frozen dataclass 应该是可哈希的"""
        ctx = GitContext(
            thread_id="t1",
            task_branch="main",
            git_repo_url="https://github.com/owner/repo.git",
            git_platform="github",
        )
        hash(ctx)  # 不应抛出异常
