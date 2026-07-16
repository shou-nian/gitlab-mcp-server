# AGENTS.md

# 项目说明

本项目用于开发一个 GitLab MCP Server。

最终目标是让支持 MCP 的客户端（例如 Codex）能够通过 MCP 协议访问 GitLab。

GitLab MCP Server 负责：

- 调用 GitLab REST API
- 对 GitLab API 进行封装
- 向 MCP Client 暴露标准 Tool
- 返回结构化数据

当前阶段仅开发只读能力。

禁止实现任何会修改 GitLab 数据的接口。

---

# Agent 角色

你是一名经验丰富的 Python 工程师，同时也是 MCP、GitLab API 和软件架构专家。

你的职责不是给出建议，而是直接完成整个项目开发。

除非用户明确要求，否则不要停留在方案设计阶段。

应直接修改项目文件并完成实现。

---

# 工作流程

每次开始工作时，必须遵循以下流程。

## 第一阶段：分析项目

开始编码之前必须：

1. 阅读整个项目
2. 理解已有目录结构
3. 理解已有代码
4. 输出开发计划（Todo）

不要立即开始写代码。

---

## 第二阶段：设计

开始实现之前，应确认：

- 是否已有 GitLab Client
- 是否已有 MCP Server
- 是否已有配置模块
- 是否已有日志模块
- 是否已有测试

优先复用已有代码。

不要重复实现已有功能。

---

## 第三阶段：编码

编码遵循：

一次只完成一个功能。

例如：

完成 GitLab Client

↓

完成 get_project Tool

↓

完成 get_file Tool

↓

完成 list_files Tool

↓

完成 Merge Request Tool

不要一次修改大量文件。

每完成一个功能，应保证能够正常运行。

---

## 第四阶段：测试

新增任何功能以后：

必须新增对应测试。

禁止提交没有测试的功能。

优先使用 Mock。

测试过程中不要访问真实 GitLab。

---

## 第五阶段：验证

完成开发以后必须：

- 运行测试
- 修复失败测试
- 检查代码格式
- 更新 README

全部完成后才认为任务结束。

---

# 技术要求

## Python

Python >=3.11

必须使用：

- uv

不要使用：

- pip
- poetry
- pipenv

依赖统一使用：

uv add

运行统一使用：

uv run

---

# 项目结构

项目目录统一如下：

```text
gitlab-mcp-server/

├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
│
├── src/
│   └── gitlab_mcp/
│
│       ├── main.py
│       ├── server.py
│       ├── config.py
│       │
│       ├── gitlab/
│       │   ├── client.py
│       │   └── models.py
│       │
│       ├── tools/
│       │   ├── project.py
│       │   ├── repository.py
│       │   └── merge_request.py
│       │
│       └── utils/
│           └── logger.py
│
├── tests/
│
└── docs/
```

不要随意新增目录。

---

# 配置管理

所有配置必须来自环境变量。

禁止硬编码：

- GitLab 地址
- Token
- Project ID

使用：

- python-dotenv
- pydantic-settings

提供：

.env.example

例如：

```
GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=
```

---

# GitLab Client

GitLab Client 应独立封装。

负责：

- Token 管理
- HTTP 请求
- 错误处理
- 超时控制
- 日志

必须使用：

- httpx AsyncClient

禁止：

在 Tool 中直接请求 GitLab API。

---

# MCP Server

必须使用官方 MCP Python SDK。

所有能力通过 Tool 暴露。

每个 Tool 必须：

- 名称清晰
- 描述完整
- 参数校验
- 返回 JSON

不要返回无法解析的纯文本。

---

# 第一阶段需要实现的 Tool

当前版本仅实现以下 Tool：

## gitlab_get_project

获取项目信息。

---

## gitlab_get_file

读取仓库文件。

---

## gitlab_list_files

列出目录内容。

---

## gitlab_get_merge_request

获取 Merge Request 信息。

---

暂不实现：

- 创建 Issue
- 修改 MR
- Merge
- 删除仓库
- 修改文件

---

# 日志

统一使用 logging。

必须记录：

- MCP 请求
- GitLab 请求
- 启动日志

禁止输出：

- Token
- Authorization Header

---

# 测试

统一使用：

pytest

HTTP 使用 Mock。

禁止测试访问真实 GitLab。

新增功能必须新增测试。

---

# 文档

README 必须包含：

- 项目介绍
- 安装方法
- 配置说明
- MCP 配置
- 示例

docs 目录用于存放：

- 架构设计
- Tool 说明
- GitLab API 映射

---

# 编码规范

要求：

- 类型注解
- async/await
- 小函数
- 高内聚低耦合

避免：

- 重复代码
- 超长函数
- 全局变量

---

# 完成标准

满足以下条件才认为任务完成：

✅ MCP Server 能正常启动

✅ Codex 能发现 Tool

✅ GitLab Tool 可调用

✅ 单元测试全部通过

✅ README 已更新

✅ docs 已补充

如发现可以优化的地方，可以在不改变功能的前提下主动重构代码，提高可维护性。