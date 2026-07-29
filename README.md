# ainote-skill

Cursor Agent Skill：内容项目运营（资料 / **Agent 选题确认建任务** / **Agent 本地写稿落库**）+ 小红书发布。

## 写稿原则

1. Agent 本地起草选题 → **用户确认** → `content-task-create`（任务+选题入库，`skip_ai`，后端不调模型）
2. Agent 再按选题本地写稿 → `piece-create` 保存  
禁止使用 `content-task-confirm`（会触发服务端 LLM）。

## 安装

### 方式一：Skills CLI（推荐）

```bash
npx skills add wuxin0608/ainote-skill -g -y
```

### 方式二：手动克隆

```bash
git clone https://github.com/wuxin0608/ainote-skill.git ~/.cursor/skills/ainote-skill
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
```

## 使用流程

```bash
# 选项目
python3 scripts/project-list.py
python3 scripts/project-use.py '{"projectId":123}'

# 拉资料 → Agent 起草选题 → 用户确认 → 建任务
python3 scripts/file-list.py
python3 scripts/content-task-create.py '{
  "goal":"推广方向",
  "selected_topics":[{"title":"选题A","angle":"场景切入"}]
}'

# Agent 写稿落库
python3 scripts/piece-create.py '{
  "taskId":987,"topicId":11,"result":"成稿全文","content_type":"xiaohongshu"
}'

# 小红书发布
python3 scripts/device-list.py
python3 scripts/add-task.py '{"title":"标题","text":"正文","deviceName":"设备名"}'
```

详细参数见 [SKILL.md](./SKILL.md)。

## License

MIT
