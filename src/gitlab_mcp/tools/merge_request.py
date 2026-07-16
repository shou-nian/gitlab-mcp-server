"""Merge Request 查询 Tool。"""

from pydantic import ValidationError

from gitlab_mcp.gitlab.client import GitLabClient, GitLabClientError
from gitlab_mcp.gitlab.models import MergeRequest
from gitlab_mcp.tools import (
    ToolResponse,
    client_error_response,
    parameter_error,
    response_validation_error,
    success_response,
    validate_project_id,
)
from gitlab_mcp.utils.logger import get_logger

logger = get_logger(__name__)


async def gitlab_get_merge_request(
    client: GitLabClient,
    project_id: int | str,
    merge_request_iid: int,
) -> ToolResponse:
    """通过项目标识和项目内 IID 获取 Merge Request 信息。"""

    logger.info("MCP tool request tool=gitlab_get_merge_request")
    if error := validate_project_id(project_id):
        return parameter_error(error)
    if isinstance(merge_request_iid, bool) or merge_request_iid <= 0:
        return parameter_error("merge_request_iid 必须是正整数")

    try:
        payload = await client.get_merge_request(project_id, merge_request_iid)
        merge_request = MergeRequest.model_validate(payload)
    except GitLabClientError as exc:
        return client_error_response(exc)
    except ValidationError as exc:
        return response_validation_error(exc)
    return success_response(merge_request.model_dump(mode="json"))
