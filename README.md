# GitLab MCP Server

一个基于官方 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 的只读 GitLab MCP Server。它通过 stdio 向 Codex 等 MCP Client 暴露结构化 Tool，并由独立的异步 Client 调用 GitLab REST API v4。

当前版本只提供以下能力：

- `gitlab_get_project`：获取项目信息
- `gitlab_get_file`：读取仓库文件和元数据
- `gitlab_list_files`：列出仓库目录内容
- `gitlab_get_merge_request`：获取 Merge Request 信息

项目不会创建、修改或删除任何 GitLab 数据。

## 环境要求

- Python 3.11 或更高版本
- [uv](https://docs.astral.sh/uv/)
- 可访问目标 GitLab 实例的网络
- 建议使用仅含 `read_api` 权限的 GitLab Access Token

## 安装

```bash
git clone <repository-url>
cd gitlab-mcp-server
uv sync
```

`uv sync` 会严格按照 `uv.lock` 创建或更新项目虚拟环境。项目不使用 `pip`、Poetry 或 Pipenv。

## 配置

复制示例配置并填写 GitLab 信息：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

环境变量说明：

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `GITLAB_URL` | 是 | 无 | GitLab 实例根地址，例如 `https://gitlab.example.com` |
| `GITLAB_TOKEN` | 是 | 无 | GitLab Access Token；日志不会输出该值 |
| `GITLAB_TIMEOUT` | 否 | `30` | GitLab HTTP 请求超时秒数，必须大于 0 |
| `LOG_LEVEL` | 否 | `INFO` | Python 日志级别 |

环境变量优先于 `.env`。不要把 `.env` 提交到版本库。

## 启动

```bash
uv run gitlab-mcp
```

Server 使用 stdio 传输；直接启动后等待 MCP Client 消息属于正常行为。日志写入 stderr，不会污染 MCP 协议的 stdout。

Server 支持优雅退出。MCP Client 关闭 stdin、发送 `SIGINT`（如 `Ctrl+C`）或发送 `SIGTERM` 时，Server 会停止接收请求、取消仍在执行的任务，并在进程退出前关闭 GitLab HTTP 连接池。正常退出过程及结果只记录到 stderr，不会输出 Python traceback。

也可以使用仓库根兼容入口：

```bash
uv run python main.py
```

## Codex / MCP Client 配置

在 Codex 的 `config.toml` 中添加：

```toml
[mcp_servers.gitlab]
command = "uv"
args = ["run", "--directory", "D:/path/to/gitlab-mcp-server", "gitlab-mcp"]

[mcp_servers.gitlab.env]
GITLAB_URL = "https://gitlab.example.com"
GITLAB_TOKEN = "your-read-only-token"
GITLAB_TIMEOUT = "30"
```

通用 JSON MCP 配置示例：

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/gitlab-mcp-server",
        "gitlab-mcp"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.example.com",
        "GITLAB_TOKEN": "your-read-only-token"
      }
    }
  }
}
```

重启 MCP Client 后，应能发现四个以 `gitlab_` 开头的 Tool。

## 调用示例

参数中的 `project_id` 支持 GitLab 数值项目 ID，也支持 `namespace/project` 路径。

获取项目：

```json
{
  "name": "gitlab_get_project",
  "arguments": {"project_id": "group/demo"}
}
```

读取文件：

```json
{
  "name": "gitlab_get_file",
  "arguments": {
    "project_id": "group/demo",
    "file_path": "src/app.py",
    "ref": "main"
  }
}
```

GitLab Files API 的 `content` 字段通常为 base64。Server 会保留 GitLab 原始 `encoding` 和 `content`，由调用方按需解码。

列出目录：

```json
{
  "name": "gitlab_list_files",
  "arguments": {
    "project_id": 42,
    "path": "src",
    "ref": "main",
    "recursive": false
  }
}
```

获取 Merge Request：

```json
{
  "name": "gitlab_get_merge_request",
  "arguments": {
    "project_id": 42,
    "merge_request_iid": 7
  }
}
```

成功响应统一为 `{"success": true, "data": ...}`，参数错误或 GitLab API 错误统一为 `{"success": false, "error": ...}`。

## 开发与测试

测试全部使用 `AsyncMock` 或 `httpx.MockTransport`，不会访问真实 GitLab：

```bash
uv run pytest -q
uv run ruff check src tests main.py
uv run ruff format --check src tests main.py
```

更多信息：

- [架构设计](docs/architecture.md)
- [Tool 说明](docs/tools.md)
- [GitLab API 映射](docs/api-mapping.md)
