---
name: ainote-skill
description: ainote skill / 小红书相关能力：创建笔记任务、修改任务文案、上传配图、查询任务列表、导入模板、获取设备列表。Use when publishing or querying content via ainote skill API.
version: 2.3.0
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
      description: 要调用的子能力名：`device-list` / `add-task` / `edit-task` / `upload-image` / `task-list` / `add-template`
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

设置环境变量 **`AINOTE_API_KEY`**（`sk-` 前缀，在 Web 端「AI Agent 接入」复制）。

API 地址固定为 `https://ainote.com.cn/api/web`，无需配置。

每次调用前脚本会校验 API Key 是否存在；请求头使用 `X-AINOTE-API-KEY`。

## 推荐流程

1. `device-list` → 缓存 `.cache/devices.json`（`[{name, deviceId, url}]`）
2. `add-task` → 创建文字笔记，返回 `taskId`
3. `upload-image` → 传入 `taskId` 与本地图片路径，上传并插入配图
4. `edit-task` → 可选，按 `taskId` 修改标题与正文，不改动配图
5. `task-list` → 可选，查询任务列表，验证笔记 `images` 已更新

## 子能力与脚本

| 子能力 | 脚本 | 说明 |
|--------|------|------|
| `device-list` | `scripts/device-list.py` | 获取所有设备并写入 `.cache/devices.json` |
| `add-task` | `scripts/add-task.py` | 创建笔记任务（仅 title/text/device，不含配图） |
| `edit-task` | `scripts/edit-task.py` | 按 taskId 修改标题与正文，不修改配图 |
| `upload-image` | `scripts/upload-image.py` | 上传本地图片并追加到指定 task |
| `task-list` | `scripts/task-list.py` | 获取笔记任务列表 |
| `add-template` | `scripts/add-template.py` | 导入笔记模板 |

### `add-task` 参数
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 标题 |
| `text` | string | 是 | 正文 |
| `deviceId` | number | 条件 | 设备 ID（见 devices.json）；仅一台时可省略 |
| `deviceName` | string | 条件 | 设备名，可替代 deviceId |

返回 `taskId`（即 `data.id`），供 `upload-image` / `edit-task` 使用。配图请走 `upload-image`，不在 add-task 中传递。

### `edit-task` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `taskId` | number | 是 | 要修改的任务 ID |
| `title` | string | 是 | 新标题 |
| `text` | string | 是 | 新正文 |

仅更新标题与正文，**不会修改**任务已有配图。

### `upload-image` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `taskId` | number | 是 | `add-task` 返回的任务 ID |
| 本地路径 | string | 是 | CLI positional，支持多张图片 |

返回 `{taskId, urls, images}`：`urls` 为本次上传的 URL，`images` 为该 task 当前全部配图。

### `task-list` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 否 | 默认 `published`；查配图任务可用 `checked` |
| `deviceName` / `publishKey` | string | 条件 | 同 add-task |
| `pageSize` / `pageNum` | number | 否 | 客户端分页（服务端返回全量后切片） |

### `add-template` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 是 | 小红书笔记链接（可多条，逗号分隔）；或纯文案（多条用 `---` 分隔），与 Web 端「导入模板」一致 |

返回解析后的模板列表：`[{title, desc, imgs}]`，`imgs` 为配图远程 URL 数组。

## 快速调用

```bash
# 在 skill 根目录下执行

# 1) 拉取设备列表（首次必做）
python3 scripts/device-list.py

# 2) 创建文字笔记
python3 scripts/add-task.py '{"title":"标题","text":"文案","deviceId":123}'
# 返回含 taskId，例如 {"noteshareResult":{...},"taskId":98765}

# 3) 上传本地图片并插入该笔记
python3 scripts/upload-image.py --params '{"taskId":98765}' /path/a.jpg /path/b.png

# 4) 修改标题与正文（不改动配图）
python3 scripts/edit-task.py '{"taskId":98765,"title":"新标题","text":"新文案"}'

# 5) 已发布/待发布列表
python3 scripts/task-list.py --params '{"category":"checked","deviceName":"我的设备","pageSize":10,"pageNum":1}'

# 6) 导入模板（小红书链接或文案）
python3 scripts/add-template.py --params '{"keyword":"https://www.xiaohongshu.com/explore/..."}'
```
