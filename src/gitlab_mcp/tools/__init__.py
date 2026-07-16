"""MCP Tool 共享类型和响应辅助函数。"""

from typing import Any

from pydantic import ValidationError

from gitlab_mcp.gitlab.client import GitLabClientError

ToolResponse = dict[str, Any]


def success_response(data: Any) -> ToolResponse:
    """构造统一的成功 JSON 响应。"""

    return {"success": True, "data": data}


def client_error_response(error: GitLabClientError) -> ToolResponse:
    """构造不包含认证信息的 GitLab 错误 JSON 响应。"""

    return {
        "success": False,
        "error": {"type": "gitlab_error", **error.to_dict()},
    }


def response_validation_error(error: ValidationError) -> ToolResponse:
    """构造 GitLab 响应模型校验错误。"""

    return {
        "success": False,
        "error": {
            "type": "response_validation_error",
            "message": "GitLab API 响应格式无效",
            "details": error.errors(include_input=False, include_url=False),
        },
    }


def parameter_error(message: str) -> ToolResponse:
    """构造 Tool 参数校验错误。"""

    return {
        "success": False,
        "error": {"type": "invalid_parameters", "message": message},
    }


def validate_project_id(project_id: int | str) -> str | None:
    """校验数值 ID 或 namespace/project 形式的项目标识。"""

    if isinstance(project_id, bool):
        return "project_id 必须是正整数或非空项目路径"
    if isinstance(project_id, int):
        if project_id <= 0:
            return "project_id 必须是正整数"
        return None
    if not project_id.strip():
        return "project_id 不能为空"
    return None


def validate_non_empty(value: str, name: str) -> str | None:
    """校验必填字符串参数。"""

    if not value.strip():
        return f"{name} 不能为空"
    return None
