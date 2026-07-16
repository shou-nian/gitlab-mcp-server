# Tool 说明

所有 Tool 都是幂等只读操作，返回可解析的 JSON 对象。`project_id` 接受正整数或 `namespace/project` 字符串；项目路径和文件路径会由 Client 进行 URL 编码。

## `gitlab_get_project`

获取一个 GitLab 项目的基本信息以及 GitLab 返回的其他扩展字段。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project_id` | integer 或 string | 是 | 正整数 ID 或 `namespace/project` |

核心响应字段：`id`、`name`、`path_with_namespace`、`web_url`、`description`、`default_branch`、`visibility`。

## `gitlab_get_file`

读取指定 ref 下的一个仓库文件及元数据。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project_id` | integer 或 string | 是 | 项目标识 |
| `file_path` | string | 是 | 仓库内完整文件路径，不能为空 |
| `ref` | string | 是 | 分支、标签或提交 SHA，不能为空 |

核心响应字段：`file_name`、`file_path`、`size`、`encoding`、`content`、`ref`、`blob_id`、`commit_id`、`last_commit_id`。

注意：GitLab 默认以 base64 返回 `content`。Server 保留原始内容和 `encoding`，不会对二进制文件做有损转换。

## `gitlab_list_files`

列出仓库目录内容。Client 使用每页 100 条并根据 `X-Next-Page` 自动读取全部分页。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `project_id` | integer 或 string | 是 | 无 | 项目标识 |
| `path` | string | 否 | `""` | 目录路径，空字符串表示根目录 |
| `ref` | string 或 null | 否 | `null` | 分支、标签或提交 SHA；省略时由 GitLab 使用默认分支 |
| `recursive` | boolean | 否 | `false` | 是否递归列出子目录 |

每个目录项包含 `id`、`name`、`type`、`path`、`mode`；`type` 为 `tree`、`blob` 或 `commit`。

## `gitlab_get_merge_request`

获取项目内一个 Merge Request。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project_id` | integer 或 string | 是 | 项目标识 |
| `merge_request_iid` | integer | 是 | 项目内 MR IID，必须大于 0 |

核心响应字段：`id`、`iid`、`project_id`、`title`、`state`、`source_branch`、`target_branch`、`web_url`、`description`、`author`。

## 响应格式

成功：

```json
{"success": true, "data": {}}
```

失败：

```json
{
  "success": false,
  "error": {
    "type": "invalid_parameters",
    "message": "project_id 不能为空"
  }
}
```
