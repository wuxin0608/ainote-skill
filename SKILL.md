---
name: ainote-skill
description: ainote skill / 内容运营与小红书发布：切换项目、维护资料；Agent 本地起草选题并经用户确认后 create task 落库；再本地写稿 piece-create 保存；以及设备笔记发布。Use when publishing or generating content via ainote skill API. NEVER trigger backend LLM generation.
version: 2.6.0
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
      description: 子能力名，见下方表格（如 `project-list` / `content-task-create` / `piece-create`）
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

## 核心原则（必读）

**选题与写稿一律由当前前端 Agent 完成，后端只做存储，不调用任何模型。**

- ✅ Agent 本地起草选题 → **展示给用户确认** → `content-task-create`（带选题，`skip_ai`）落库
- ✅ 确认后再 Agent 本地写稿 → `piece-create` 挂到对应 `taskId` + `topicId`
- ✅ 改稿用 `piece-update`；发布用 `add-task` / `upload-image`
- ❌ **禁止**调用 `content-task-confirm`（会触发后端 LLM 生成）
- ❌ **禁止**在未获用户确认选题前写稿或建任务

## 配置

设置环境变量 **`AINOTE_API_KEY`**（`sk-` 前缀）。

- Key 为**用户级固定唯一密钥**：注册时自动生成，在 Web 端「AI Agent 接入」复制。
- 同一 Key 可管理多个项目；先用 `project-list` / `project-use` 选定当前项目。
- API 地址固定为 `https://ainote.com.cn/api/web`，无需配置。
- 请求头：`X-AINOTE-API-KEY`（需 VIP）。

## 推荐流程

### A. Agent 选题确认 → 建任务 → 写稿落库

1. `project-list` → `project-use`（写入 `.cache/project.json`）
2. 可选：`file-list` / `file-upsert`、`topic-list` 拉取或维护资料与选题库
3. **Agent 本地起草选题**（若干条：`title` / `angle` / `audience`），**先发给用户确认/修改**，未确认不得继续
4. 用户确认后：`content-task-create`（`goal` + `selected_topics`）→ 任务与选题一并入库，返回 `taskId` 与 topics（含 topic `id`）
5. 可选：`content-task-get` 核对任务与选题
6. **Agent 按已确认选题本地写稿**（一题一稿或多渠道）
7. `piece-create`（必带 `taskId` + `topicId`/`project_task_topic_id` + `result`）保存成稿
8. 可选：`piece-update` / `piece-list`；小红书再走发布流程

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
| `topic-create` | `scripts/topic-create.py` | 写入项目选题库（可选；任务选题以 create task 为准） |
| `content-task-create` | `scripts/content-task-create.py` | **用户确认后**：任务+选题落库（`skip_ai`，不调模型） |
| `content-task-get` | `scripts/content-task-get.py` | 查询任务与选题（只读） |
| `piece-create` | `scripts/piece-create.py` | **保存 Agent 成稿**（挂已有 task/topic） |
| `piece-list` | `scripts/piece-list.py` | 成稿列表 |
| `piece-update` | `scripts/piece-update.py` | 修改成稿 |
| `device-list` | `scripts/device-list.py` | 设备列表 |
| `add-task` | `scripts/add-task.py` | 创建笔记任务 |
| `edit-task` | `scripts/edit-task.py` | 修改标题正文 |
| `upload-image` | `scripts/upload-image.py` | 上传配图 |
| `task-list` | `scripts/task-list.py` | 笔记任务列表 |
| `add-template` | `scripts/add-template.py` | 导入笔记模板 |

### 已废弃（Agent 禁止使用）

| 子能力 | 脚本 | 原因 |
|--------|------|------|
| `content-task-confirm` | `scripts/content-task-confirm.py` | 确认选题并触发**后端**生成 |

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
| `selected_topics` | object[] | 是 | 用户已确认选题：`[{title, angle?, audience?, use_count?, project_topic_id?}]` |
| `content_types` | string[] | 否 | 默认 `["xiaohongshu"]` |
| `audience` | string | 否 | 受众补充 |

脚本固定传 `skip_ai=true` / `source=agent`，**不会**触发后端模型。  
返回 `taskId` 与 `topics`（含服务端分配的 topic `id`，写稿时要用）。

### `content-task-get` 参数

- `{"taskId":123}` → 任务详情 + topics

### `piece-create` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `result` | string | 是 | 成稿全文（Agent 已写好） |
| `taskId` / `project_task_id` | number | 是* | 挂到已确认任务（推荐必填） |
| `topicId` / `project_task_topic_id` | number | 是* | 对应选题 id（来自 create/get） |
| `title` | string | 否 | 省略则用选题标题或正文首行 |
| `content_type` | string | 否 | 默认 `xiaohongshu` |
| `angle` / `audience` | string | 否 | 一般可省略（跟选题） |
| `projectId` | number | 否 | 默认用 `.cache/project.json` |

\* 正常流程必须带 `taskId` + `topicId`。

### `piece-list` / `piece-update`

- `piece-list`：`{"taskId":123}`
- `piece-update`：`{"id":1,"result":"成稿正文"}`

### 发布侧参数（摘要）

- `add-task`：`title` / `text` / `deviceId|deviceName`
- `edit-task`：`taskId` / `title` / `text`
- `upload-image`：`--params '{"taskId":N}'` + 本地图片路径
- `task-list`：`category` / `deviceName` / 分页
- `add-template`：`keyword`（小红书链接或文案）

## 写稿提示（Agent）

1. 先 `file-list` / `topic-list` 获取事实，**不要虚构**价格、资质、案例。
2. 选题阶段：列出 2～5 条候选，标明标题/角度/受众，**等用户回复确认或修改后再** `content-task-create`。
3. 写稿阶段：严格按已确认选题写；小红书第一行短标题，短段落，末行 3～6 个 `#话题`。
4. 每篇写完用 `piece-create` 带上对应 `taskId` + `topicId`。

## 快速调用

```bash
# 在 skill 根目录下执行

# 0) 选项目
python3 scripts/project-list.py
python3 scripts/project-use.py '{"projectId":123}'

# 1) 资料（可选）
python3 scripts/file-list.py
python3 scripts/topic-list.py

# 2) Agent 本地起草选题 → 用户确认后落库
python3 scripts/content-task-create.py '{
  "goal":"推广方向",
  "selected_topics":[
    {"title":"选题A","angle":"场景切入","audience":"宝妈"},
    {"title":"选题B","angle":"对比测评"}
  ],
  "content_types":["xiaohongshu"]
}'
# → taskId + topics[].id

# 3) Agent 按选题写稿后保存
python3 scripts/piece-create.py '{
  "taskId":987,
  "topicId":11,
  "result":"标题\\n\\n正文...\\n\\n#话题1 #话题2",
  "content_type":"xiaohongshu"
}'

# 4) 发布到小红书
python3 scripts/device-list.py
python3 scripts/add-task.py '{"title":"标题","text":"文案","deviceId":123}'
```
