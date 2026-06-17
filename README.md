# ainote-skill

Cursor Agent Skill：小红书相关能力——创建笔记任务、修改任务文案、上传配图、查询任务列表、导入模板、获取设备列表。

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
1. 在 ainote Web 端侧边栏 **「AI Agent 接入」** 复制 `sk-...` API Key（需 VIP 会员）

2. 安装 Python 依赖：

```bash
pip install -r requirements.txt
```

3. 配置 API Key：

```bash
export AINOTE_API_KEY=sk-your-key-here
```

## 使用流程

```bash
# 1. 拉取设备列表（写入 .cache/devices.json）
python3 scripts/device-list.py

# 2. 创建任务 / 上传配图 / 修改文案 / 查列表 / 导模板
python3 scripts/add-task.py '{"title":"标题","text":"正文","deviceName":"设备名"}'
python3 scripts/upload-image.py --params '{"taskId":98765}' /path/to/image.jpg
python3 scripts/edit-task.py '{"taskId":98765,"title":"新标题","text":"新正文"}'
python3 scripts/task-list.py --params '{"category":"checked","deviceName":"设备名","pageSize":10,"pageNum":1}'
```

详细参数见 [SKILL.md](./SKILL.md)。

## License

MIT
