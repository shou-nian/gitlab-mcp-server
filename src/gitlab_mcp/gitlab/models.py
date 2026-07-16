"""GitLab API 响应模型。"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class GitLabModel(BaseModel):
    """保留 GitLab 返回的扩展字段，同时校验 Tool 依赖的核心字段。"""

    model_config = ConfigDict(extra="allow")


class Project(GitLabModel):
    id: int
    name: str
    path_with_namespace: str
    web_url: str
    description: str | None = None
    default_branch: str | None = None
    visibility: str | None = None


class RepositoryFile(GitLabModel):
    file_name: str
    file_path: str
    size: int
    encoding: str
    content: str
    ref: str
    blob_id: str
    commit_id: str
    last_commit_id: str


class RepositoryTreeItem(GitLabModel):
    id: str
    name: str
    type: Literal["tree", "blob", "commit"]
    path: str
    mode: str


class MergeRequest(GitLabModel):
    id: int
    iid: int
    project_id: int
    title: str
    state: str
    source_branch: str
    target_branch: str
    web_url: str
    description: str | None = None
    author: dict[str, Any] | None = None
