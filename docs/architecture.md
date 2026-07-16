# 架构设计

## 目标与边界

GitLab MCP Server 在 MCP Client 与 GitLab REST API v4 之间提供只读适配层。当前边界只包含项目、仓库文件、仓库目录和单个 Merge Request 查询，不注册任何写入 Tool。

## 模块关系

```text
MCP Client
    │ stdio / MCP
    ▼
server.py ── Tool 注册、生命周期、依赖注入
    │
    ▼
tools/ ───── 参数校验、响应模型校验、统一 JSON 封装
    │
    ▼
gitlab/client.py ── Token、超时、HTTP 错误、分页、请求日志
    │ httpx.AsyncClient
    ▼
GitLab REST API v4
```

辅助模块：

- `config.py`：使用 `pydantic-settings` 从环境变量和 `.env` 加载配置。
- `gitlab/models.py`：校验各 API 的核心字段，同时保留 GitLab 扩展字段。
- `utils/logger.py`：统一配置 stderr 日志，避免干扰 stdio MCP 消息。
- `main.py`：加载配置并以 stdio 启动 Server。

## 生命周期

生产启动时，MCP lifespan 创建一个 `GitLabClient`，四个 Tool 共用同一 `httpx.AsyncClient` 连接池。Server 停止时异步关闭连接池。测试通过 `create_server(client=...)` 注入 Mock Client，因此不读取 Token，也不会访问网络。

## 数据流

1. MCP SDK 根据 Tool 函数类型注解校验输入并生成 JSON Schema。
2. Tool 层执行项目 ID、文件路径、ref 和 MR IID 等业务校验。
3. GitLab Client 对 URL 路径参数编码并发起带 `PRIVATE-TOKEN` 的 GET 请求。
4. Client 处理超时、连接、HTTP 状态、JSON 和分页错误。
5. Tool 使用 Pydantic 模型验证核心响应字段。
6. Server 返回统一的结构化 JSON，同时由 MCP SDK提供文本兼容内容。

## 安全与日志

- 仅实现 HTTP GET 请求。
- Token 由 `SecretStr` 保存，只用于构造请求 Header。
- 日志不记录 Header、Token 或响应正文。
- MCP Tool annotations 显式声明 `readOnlyHint=true`、`destructiveHint=false`。
- `.env` 被 Git 忽略；仓库只提供空 Token 的 `.env.example`。

## 错误模型

Tool 不向调用方暴露 Python traceback，失败时返回：

```json
{
  "success": false,
  "error": {
    "type": "gitlab_error",
    "message": "GitLab API 请求失败",
    "status_code": 404,
    "details": {"message": "404 Project Not Found"}
  }
}
```

错误类型包括 `invalid_parameters`、`gitlab_error` 和 `response_validation_error`。
