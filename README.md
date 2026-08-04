# ainote-skill

Cursor Agent Skill：内容项目运营（资料 / **Agent 本地写稿落库** / 选题）+ 小红书发布。

## 写稿原则

1. Web 派单；本地 Agent 按 `taskId=` / 今日 due 领取任务并写稿
2. `content-task-claim` → 本地写稿 → `piece-create` → `content-task-finish`
3. **禁止**使用 `content-task-confirm`（会触发服务端 LLM）

## 安装

请安装 **`content` 分支**（含 claim/due/finish 与写稿格式规范）：

### 方式一：Skills CLI（推荐）

```bash
npx skills add https://github.com/wuxin0608/ainote-skill/tree/content -g -y
```

### 方式二：手动克隆

```bash
git clone -b content https://github.com/wuxin0608/ainote-skill.git ~/.cursor/skills/ainote-skill
```

## 配置

1. 在 ainote Web 端 **「AI Agent 接入」** 复制 `sk-...` API Key（**用户级固定密钥**，需 VIP）
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

```bash
export AINOTE_API_KEY=sk-your-key-here
# 可选：覆盖 API 地址
# export AINOTE_API_BASE=https://ai2027.cn/note/web
```

## 使用流程

```bash
# 选项目
python3 scripts/project-list.py
python3 scripts/project-use.py '{"projectId":123}'

# Web 复制「执行任务 taskId=987 projectId=123」时：
python3 scripts/content-task-get.py '{"taskId":987}'
python3 scripts/content-task-claim.py '{"taskId":987}'
# … 本地写稿（见 references/content-formats.md）…
python3 scripts/piece-create.py '{"taskId":987,"topicId":11,"result":"成稿全文","batch_tag":"...","batch_piece_index":1}'
python3 scripts/content-task-finish.py '{"taskId":987,"batch_tag":"..."}'

# 或拉取今日到期
python3 scripts/content-task-due.py '{"projectId":123}'

# 小红书发布
python3 scripts/device-list.py
python3 scripts/add-task.py '{"title":"标题","text":"正文","deviceName":"设备名"}'
```

详细参数见 [SKILL.md](./SKILL.md)。

## License

MIT
