---
name: noteshare
description: noteshare/小红书相关能力：发布笔记、查询已发布笔记列表、导入模板、获取设备列表。Use when publishing or querying noteshare content via ainote skill API.
version: 2.0.0
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
      description: 要调用的子能力名：`device-list` / `publish` / `note-list` / `add-template`
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

仅需 **`AINOTE_API_KEY`**（`sk-` 前缀）：

1. 环境变量 `AINOTE_API_KEY`
2. 或 `scripts/env.py` 中写死（从 `env.example.py` 复制）

可选 `AINOTE_API_BASE`，默认 `https://ainote.com.cn/api/web`。

每次调用前脚本会校验 API Key 是否存在；请求头使用 `X-AINOTE-API-KEY`。

## 推荐流程

1. `device-list` → 缓存 `.cache/devices.json`（`[{name, url}]`）
2. 其他脚本通过 `deviceName` 或 `publishKey` 指定设备 URL

## 子能力与脚本

| 子能力 | 脚本 | 说明 |
|--------|------|------|
| `device-list` | `scripts/device-list.py` | 获取所有设备并写入 `.cache/devices.json` |
| `publish` | `scripts/publish.py` | 创建笔记任务 |
| `note-list` | `scripts/note-list.py` | 获取已发布笔记列表 |
| `add-template` | `scripts/add-template.py` | 导入笔记模板 |

### `publish` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 标题 |
| `text` | string | 是 | 正文 |
| `urls` / `imgs` | string[] | 否 | 配图 URL |
| `deviceName` | string | 条件 | 设备名（见 devices.json）；仅一台时可省略 |
| `publishKey` | string | 条件 | 完整 note-share URL，可替代 deviceName |

### `note-list` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 否 | 默认 `published` |
| `deviceName` / `publishKey` | string | 条件 | 同 publish |
| `pageSize` / `pageNum` | number | 否 | 客户端分页（服务端返回全量后切片） |

### `add-template` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 模板标题 |
| `text` | string | 是 | 模板正文 |
| `imgs` | string[] | 是 | 配图 URL（1–10 张） |
| `tag` | string | 否 | 话题标签 |
| `originalId` | string | 否 | 原文 ID（去重用） |
| `deviceName` / `publishKey` | string | 条件 | 同 publish |

## 快速调用

```bash
# 在 skill 根目录下执行

# 1) 拉取设备列表（首次必做）
python3 scripts/device-list.py

# 2) 发布笔记
python3 scripts/publish.py '{"urls":["https://..."],"title":"标题","text":"文案","deviceName":"我的设备"}'

# 3) 已发布列表
python3 scripts/note-list.py --params '{"category":"published","deviceName":"我的设备","pageSize":10,"pageNum":1}'

# 4) 导入模板
python3 scripts/add-template.py --params '{"title":"标题","text":"文案","imgs":["https://..."],"deviceName":"我的设备"}'
```
