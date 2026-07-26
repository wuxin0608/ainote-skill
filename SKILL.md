---
name: ainote-skill
description: ainote skill / 内容运营与小红书发布：切换项目、维护资料与选题、创建全案文案任务、取稿改稿；以及创建设备笔记任务、上传配图、导入模板。Use when publishing or generating content via ainote skill API.
version: 2.4.0
author: custom
type: automation
permissions:
  - network
  - file.read
input_schema:
  type: object
  properties:
    tool:
      type: string
      description: 子能力名，见下方表格（如 `project-list` / `content-task-create` / `add-task`）
    params:
      type: object
      description: 对应子能力的参数对象（也可以直接按脚本 CLI 方式调用）
  required: [tool]
output_schema:
  type: object
  properties:
    result:
      type: object
    error:
      type: string
---

## 配置

设置环境变量 **`AINOTE_API_KEY`**（`sk-` 前缀）。

- Key 为**用户级固定唯一密钥**：注册时自动生成，在 Web 端「AI Agent 接入」复制。
- 同一 Key 可管理多个项目；先用 `project-list` / `project-use` 选定当前项目。
- API 地址固定为 `https://ainote.com.cn/api/web`，无需配置。
- 请求头：`X-AINOTE-API-KEY`（需 VIP）。

## 推荐流程

### A. 全案文案（Content Ops）

1. `project-list` → `project-use`（写入 `.cache/project.json`）
2. 可选：`file-upsert` / `topic-create` 维护资料与选题
3. `content-task-create` → 返回 `taskId`
4. `content-task-get` 轮询状态；若 `pending_topic_review` 则 `content-task-confirm`
5. `piece-list` 取成稿；可选 `piece-update` 改稿
6. 小红书渠道：将成稿交给下方发布流程（`add-task` / `upload-image`）

### B. 小红书发布（原有）

1. `device-list` → 缓存 `.cache/devices.json`
2. `add-task` → `upload-image` → 可选 `edit-task` / `task-list`

## 子能力与脚本

| 子能力 | 脚本 | 说明 |
|--------|------|------|
| `project-list` | `scripts/project-list.py` | 列出可管理项目 |
| `project-use` | `scripts/project-use.py` | 切换当前项目（服务端 + 本地缓存） |
| `file-list` | `scripts/file-list.py` | 项目资料列表 |
| `file-upsert` | `scripts/file-upsert.py` | 创建/更新资料（有 `id` 则更新） |
| `topic-list` | `scripts/topic-list.py` | 选题库列表 |
| `topic-create` | `scripts/topic-create.py` | 创建选题 |
| `content-task-create` | `scripts/content-task-create.py` | 创建全案任务 |
| `content-task-get` | `scripts/content-task-get.py` | 查询任务状态 |
| `content-task-confirm` | `scripts/content-task-confirm.py` | 确认选题并生成 |
| `piece-list` | `scripts/piece-list.py` | 成稿列表 |
| `piece-update` | `scripts/piece-update.py` | 修改成稿 |
| `device-list` | `scripts/device-list.py` | 设备列表 |
| `add-task` | `scripts/add-task.py` | 创建笔记任务 |
| `edit-task` | `scripts/edit-task.py` | 修改标题正文 |
| `upload-image` | `scripts/upload-image.py` | 上传配图 |
| `task-list` | `scripts/task-list.py` | 笔记任务列表 |
| `add-template` | `scripts/add-template.py` | 导入笔记模板 |

### `project-use` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `projectId` | number | 是 | 目标项目 ID |

### `file-upsert` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | number | 否 | 有则更新 |
| `name` | string | 条件 | 显示名 |
| `file_name` | string | 否 | 新建时文件名，默认 `note.md` |
| `content` | string | 否 | 正文 |
| `projectId` | number | 否 | 默认用 `.cache/project.json` |

### `topic-create` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 选题标题 |
| `angle` | string | 否 | 切入角度 |
| `audience` | string | 否 | 受众 |

### `content-task-create` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `goal` | string | 是 | 推广方向 |
| `use_ai_topics` | bool | 否 | 默认 `true` |
| `content_types` | string[] | 否 | 默认 `["xiaohongshu"]` |
| `selected_topics` | object[] | 否 | 选题库模式：`[{project_topic_id, title?, use_count}]` |
| `audience` | string | 否 | 受众补充 |

返回 `taskId`。

### `content-task-confirm` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `taskId` | number | 是 | 任务 ID |
| `topics` | object[] | 否 | `[{id, selected, use_count}]`；省略则仅触发生成 |

### `piece-list` / `piece-update`

- `piece-list`：`{"taskId":123}`
- `piece-update`：`{"id":1,"result":"成稿正文"}`

### 发布侧参数（摘要）

- `add-task`：`title` / `text` / `deviceId|deviceName`
- `edit-task`：`taskId` / `title` / `text`
- `upload-image`：`--params '{"taskId":N}'` + 本地图片路径
- `task-list`：`category` / `deviceName` / 分页
- `add-template`：`keyword`（小红书链接或文案）

## 快速调用

```bash
# 在 skill 根目录下执行

# 0) 选项目
python3 scripts/project-list.py
python3 scripts/project-use.py '{"projectId":123}'

# 1) 资料 / 选题（可选）
python3 scripts/file-upsert.py '{"name":"项目背景","file_name":"背景.md","content":"..."}'
python3 scripts/topic-create.py '{"title":"选题A","angle":"场景切入"}'

# 2) 创建全案任务并轮询
python3 scripts/content-task-create.py '{"goal":"推广方向文案","content_types":["xiaohongshu","moments"]}'
python3 scripts/content-task-get.py '{"taskId":987}'
# 若需确认选题：
python3 scripts/content-task-confirm.py '{"taskId":987}'
python3 scripts/piece-list.py '{"taskId":987}'

# 3) 发布到小红书
python3 scripts/device-list.py
python3 scripts/add-task.py '{"title":"标题","text":"文案","deviceId":123}'
```
