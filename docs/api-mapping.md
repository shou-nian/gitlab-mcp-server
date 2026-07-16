# GitLab API 映射

Server 使用 GitLab REST API v4，基础地址由 `${GITLAB_URL}/api/v4` 构造。所有路径参数使用百分号编码，认证使用 `PRIVATE-TOKEN` Header。

| MCP Tool | HTTP 方法 | GitLab API | 分页 |
| --- | --- | --- | --- |
| `gitlab_get_project` | GET | `/projects/:id` | 否 |
| `gitlab_get_file` | GET | `/projects/:id/repository/files/:file_path` | 否 |
| `gitlab_list_files` | GET | `/projects/:id/repository/tree` | 是，自动读取 `X-Next-Page` |
| `gitlab_get_merge_request` | GET | `/projects/:id/merge_requests/:merge_request_iid` | 否 |

## 参数映射

### Project

`project_id` 映射到 `:id`。当使用 `group/subgroup/project` 时，斜杠会编码为 `%2F`。

### Repository file

- `project_id` → `:id`
- `file_path` → `:file_path`，完整路径整体编码
- `ref` → query parameter `ref`

### Repository tree

- `project_id` → `:id`
- `path` → query parameter `path`
- `ref` → query parameter `ref`；为 null 时不发送
- `recursive` → query parameter `recursive`，值为 `true` 或 `false`
- Server 固定发送 `per_page=100`，并维护 `page`

### Merge Request

- `project_id` → `:id`
- `merge_request_iid` → `:merge_request_iid`

这里必须使用项目内 IID。例如 GitLab 页面 URL 以 `/-/merge_requests/7` 结尾时应传 `7`。

## 错误映射

| 情况 | Tool 错误 |
| --- | --- |
| 请求超时 | `gitlab_error` / `GitLab 请求超时` |
| DNS、连接等 RequestError | `gitlab_error` / `无法连接 GitLab` |
| GitLab 4xx 或 5xx | `gitlab_error`，包含状态码和可解析的 GitLab JSON 详情 |
| 无效 JSON | `gitlab_error` / `GitLab 返回了无效的 JSON 响应` |
| 响应缺少核心字段 | `response_validation_error` |

Server 不重试请求，以避免隐藏 GitLab 限流或权限问题；调用方可以根据结构化错误决定是否重试。
