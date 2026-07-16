"""GitLab API 封装。"""

from gitlab_mcp.gitlab.client import GitLabClient, GitLabClientError

__all__ = ["GitLabClient", "GitLabClientError"]
