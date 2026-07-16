"""项目查询 Tool。"""

from pydantic import ValidationError

from gitlab_mcp.gitlab.client import GitLabClient, GitLabClientError
from gitlab_mcp.gitlab.models import Project
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


async def gitlab_get_project(
    client: GitLabClient,
    project_id: int | str,
) -> ToolResponse:
    """获取 GitLab 项目信息。"""

    logger.info("MCP tool request tool=gitlab_get_project")
    if error := validate_project_id(project_id):
        return parameter_error(error)

    try:
        payload = await client.get_project(project_id)
        project = Project.model_validate(payload)
    except GitLabClientError as exc:
        return client_error_response(exc)
    except ValidationError as exc:
        return response_validation_error(exc)
    return success_response(project.model_dump(mode="json"))
