"""沙箱后端基类 — 手动实现所有文件操作，避免 deepagents BaseSandbox 的 shell 包装开销。"""

import logging
import os
import re
import shlex

import posixpath

from core.common.exception.api_exception import ApiException
from deepagents.backends.protocol import (
    EditResult,
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
    FileInfo,
    GrepMatch,
    SandboxBackendProtocol,
    WriteResult,
)

_PROTECTED_ENV_KEYS = {'PATH', 'SHELL', 'HOME', 'USER', 'LANG', 'LC_ALL'}
_ENV_KEY_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

logger = logging.getLogger(__name__)


def _sanitize_env(env: dict | None) -> dict:
    """过滤并校验环境变量。

    - key 必须匹配 [a-zA-Z_][a-zA-Z0-9_]*
    - 不允许覆盖系统关键变量（PATH, SHELL 等）
    """
    if not env:
        return {}

    safe = {}
    for key, value in env.items():
        if not _ENV_KEY_RE.match(key):
            logger.warning("非法环境变量 key: %s，已忽略", key)
            continue
        if key in _PROTECTED_ENV_KEYS:
            logger.warning("保护变量 %s 不允许覆盖，已忽略", key)
            continue
        safe[key] = str(value)
    return safe


class BaseSandboxBackend(SandboxBackendProtocol):
    """手动实现的沙箱后端基类。

    子类必须实现：
    - id: 沙箱唯一标识
    - _build_cmd(inner_cmd): 构建最终执行命令
    - execute(command, timeout): 调用具体 executor 执行
    """

    @property
    def id(self) -> str:
        raise NotImplementedError

    def _build_cmd(self, inner_cmd: str) -> str:
        raise NotImplementedError

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        raise NotImplementedError

    # =========================================================================
    # 路径校验
    # =========================================================================

    def _validate_path(self, file_path: str) -> str:
        """校验文件路径必须在 work_dir 范围内，防止路径遍历攻击。"""
        if hasattr(self, "_work_dir"):
            real_path = posixpath.normpath(file_path)
            work_dir = posixpath.normpath(self._work_dir)
            if not real_path.startswith(work_dir + "/") and real_path != work_dir:
                raise ApiException(
                    msg=f"路径遍历被拒绝: {file_path} 超出工作目录 {self._work_dir}"
                )
            return real_path
        return file_path

    # =========================================================================
    # 文件读取
    # =========================================================================

    def _read_raw(self, file_path: str) -> str:
        """读取文件原始内容（无行号）"""
        escaped = shlex.quote(file_path)
        cmd = self._build_cmd(f"cat {escaped} 2>&1")
        result = self.execute(cmd)
        if result.exit_code != 0:
            return f"Error: {result.output}"
        return result.output

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        escaped = shlex.quote(file_path)
        cmd = self._build_cmd(
            f"cat -n {escaped} 2>&1 | tail -n +$(({offset} + 1)) | head -n {limit}"
        )
        result = self.execute(cmd)
        if result.exit_code != 0:
            return f"Error reading {file_path}: {result.output}"
        return result.output

    # =========================================================================
    # 文件写入
    # =========================================================================

    def write(self, file_path: str, content: str) -> WriteResult:
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                mkdir_cmd = self._build_cmd(f"mkdir -p {shlex.quote(dir_path)}")
                self.execute(mkdir_cmd)

            escaped_path = shlex.quote(file_path)
            cmd = self._build_cmd(f"cat > {escaped_path} << 'SANDBOX_EOF'\n{content}\nSANDBOX_EOF")
            self.execute(cmd)
            return WriteResult(path=file_path, files_update=None)
        except Exception as e:
            return WriteResult(error=str(e))

    # =========================================================================
    # 文件编辑
    # =========================================================================

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> EditResult:
        content = self._read_raw(file_path)
        if content.startswith("Error"):
            return EditResult(error=content)

        occurrences = content.count(old_string)
        if occurrences == 0:
            return EditResult(
                error=f"'{old_string[:50]}...' not found in {file_path}"
            )
        if occurrences > 1 and not replace_all:
            return EditResult(
                error=f"'{old_string[:50]}...' found {occurrences} times in {file_path}"
            )

        new_content = content.replace(old_string, new_string)
        write_result = self.write(file_path, new_content)
        if write_result.error:
            return EditResult(error=write_result.error)
        return EditResult(
            path=file_path,
            files_update=None,
            occurrences=1 if not replace_all else occurrences,
        )

    # =========================================================================
    # 目录列表
    # =========================================================================

    def ls(self, path: str) -> dict:
        escaped = shlex.quote(path)
        cmd = self._build_cmd(f"ls -la {escaped} 2>&1")
        result = self.execute(cmd)
        if result.exit_code != 0:
            return {"error": result.output}

        entries = []
        lines = result.output.strip().split("\n")
        for line in lines[1:]:  # 跳过 total 行
            parts = line.split(maxsplit=8)
            if len(parts) >= 9:
                entries.append({
                    "name": parts[8],
                    "permissions": parts[0],
                    "size": parts[4],
                    "modified": " ".join(parts[5:8]),
                })
        return {"entries": entries}

    def ls_info(self, path: str) -> list[FileInfo]:
        escaped = shlex.quote(path)
        cmd = self._build_cmd(f"ls -la {escaped} 2>&1")
        result = self.execute(cmd)
        if result.exit_code != 0:
            return []

        entries = []
        for line in result.output.strip().split("\n")[1:]:
            parts = line.split(maxsplit=8)
            if len(parts) >= 9:
                name = parts[8]
                is_dir = parts[0].startswith("d")
                entries.append({
                    "path": os.path.join(path, name),
                    "is_dir": is_dir,
                    "size": int(parts[4]) if parts[4].isdigit() else 0,
                    "modified_at": " ".join(parts[5:8]),
                })
        return entries

    # =========================================================================
    # Glob
    # =========================================================================

    def glob(self, pattern: str, path: str = "/") -> dict:
        escaped_path = shlex.quote(path)
        cmd = self._build_cmd(
            f"find {escaped_path} -name {shlex.quote(pattern)} 2>&1 | head -100"
        )
        result = self.execute(cmd)
        if result.exit_code != 0:
            return {"error": result.output}
        matches = [line for line in result.output.strip().split("\n") if line]
        return {"matches": matches}

    def glob_info(self, pattern: str, path: str = "/") -> list[FileInfo]:
        escaped_path = shlex.quote(path)
        cmd = self._build_cmd(
            f"find {escaped_path} -name {shlex.quote(pattern)} 2>&1 | head -100"
        )
        result = self.execute(cmd)
        if result.exit_code != 0:
            return []
        entries = []
        for line in result.output.strip().split("\n"):
            if line:
                entries.append({
                    "path": line,
                    "is_dir": False,
                    "size": 0,
                    "modified_at": "",
                })
        return entries

    # =========================================================================
    # Grep
    # =========================================================================

    def grep(
        self, pattern: str, path: str | None = None, glob: str | None = None
    ) -> dict:
        search_path = shlex.quote(path) if path else "."
        grep_cmd = "grep -rn"
        if glob:
            grep_cmd += f" --include={shlex.quote(glob)}"
        cmd = self._build_cmd(
            f"{grep_cmd} {shlex.quote(pattern)} {search_path} 2>&1 | head -100"
        )
        result = self.execute(cmd)
        if result.exit_code not in (0, 1):  # 1 = 无匹配
            return {"error": result.output}
        matches = []
        for line in result.output.strip().split("\n"):
            if line and ":" in line:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    matches.append({
                        "path": parts[0],
                        "line": int(parts[1]) if parts[1].isdigit() else 0,
                        "content": parts[2],
                    })
        return {"matches": matches}

    def grep_raw(
        self, pattern: str, path: str | None = None, glob: str | None = None
    ) -> list[GrepMatch] | str:
        search_path = shlex.quote(path) if path else "."
        grep_opts = "-rHnF"
        glob_opt = f"--include='{glob}'" if glob else ""
        cmd = self._build_cmd(
            f"grep {grep_opts} {glob_opt} -e {shlex.quote(pattern)} {search_path} 2>/dev/null || true"
        )
        result = self.execute(cmd)
        output = result.output.strip()
        if not output:
            return []
        matches = []
        for line in output.split("\n"):
            parts = line.split(":", 2)
            if len(parts) >= 3:
                matches.append({
                    "path": parts[0],
                    "line": int(parts[1]),
                    "text": parts[2],
                })
        return matches

    # =========================================================================
    # 文件上传/下载
    # =========================================================================

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        responses = []
        for path, content in files:
            try:
                self.write(path, content.decode("utf-8"))
                responses.append(FileUploadResponse(path=path, error=None))
            except Exception:
                responses.append(
                    FileUploadResponse(path=path, error="permission_denied")
                )
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        responses = []
        for path in paths:
            content = self._read_raw(path)
            if content.startswith("Error"):
                responses.append(
                    FileDownloadResponse(
                        path=path, content=None, error="file_not_found"
                    )
                )
            else:
                responses.append(
                    FileDownloadResponse(
                        path=path, content=content.encode("utf-8"), error=None
                    )
                )
        return responses
