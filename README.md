# ainote-skill

Cursor Agent Skill：内容项目运营（资料 / 选题 / 全案文案）+ 小红书发布（创建设备笔记、上传配图、导入模板）。

## 安装

### 方式一：Skills CLI（推荐）

```bash
npx skills add wuxin0608/ainote-skill -g -y
```

### 方式二：手动克隆

```bash
git clone https://github.com/wuxin0608/ainote-skill.git ~/.cursor/skills/ainote-skill
```

开发分支 `content` 含全案文案能力；稳定发布后会合并至 `main`。

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
# 选项目（多项目时必做）
python3 scripts/project-list.py
python3 scripts/project-use.py '{"projectId":123}'

# 全案文案
python3 scripts/content-task-create.py '{"goal":"推广方向","content_types":["xiaohongshu"]}'
python3 scripts/content-task-get.py '{"taskId":987}'
python3 scripts/piece-list.py '{"taskId":987}'

# 小红书发布
python3 scripts/device-list.py
python3 scripts/add-task.py '{"title":"标题","text":"正文","deviceName":"设备名"}'
python3 scripts/upload-image.py --params '{"taskId":98765}' /path/to/image.jpg
```

详细参数见 [SKILL.md](./SKILL.md)。

## License

MIT
