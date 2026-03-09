# Agent Browser Skill - OpenClaw 集成

## 安装状态
- SKILL.md 已创建, 封装脚本已创建 (`scripts/browser.sh`), agent-browser 已安装 (v0.13.0), ⏳ 待下载 Chromium(首次使用时自动下载)

## 快速开始

### 首次使用(下载 Chromium)
```bash
agent-browser install # 需要约 150MB 空间
```

# 打开测试页面
agent-browser open https://example.com

# 获取快照
agent-browser snapshot

# 截图
agent-browser screenshot /tmp/test.png

# 关闭
agent-browser close

## 使用方法

### 方法 1:直接命令(推荐)
agent-browser open <url>
agent-browser click <selector>
agent-browser fill <selector> <text>

### 方法 2:封装脚本
cd /root/.openclaw/workspace/skills/agent-browser/scripts
./browser.sh open https://example.com
./browser.sh screenshot page.png
./browser.sh close

## 典型工作流

### 示例 1:自动化搜索
agent-browser open https://www.google.com
agent-browser find role textbox fill --name "Search" "OpenClaw AI"
agent-browser find role button click --name "Google Search"
agent-browser wait --load networkidle
agent-browser screenshot search.png

### 示例 2:数据抓取
agent-browser snapshot > snapshot.json
agent-browser eval "
 const items = document.querySelectorAll('h1, h2, h3');
 return Array.from(items).map(el => el.textContent);
" > titles.txt

### 示例 3:表单测试
agent-browser open https://httpbin.org/forms/post
agent-browser fill "#custname" "Test User"
agent-browser fill "#custtel" "1234567890"
agent-browser fill "#custemail" "test@example.com"
agent-browser select "#size" "medium"
agent-browser click "#submit"
agent-browser screenshot form-result.png

## 高级功能

# 按角色
agent-browser find role button click --name "Submit"

# 按文本
agent-browser find text "Sign In" click

# 按标签
agent-browser find label "Email" fill "user@example.com"

### 等待条件
agent-browser wait --load networkidle # 等待网络空闲
agent-browser wait --text "Welcome" # 等待文本出现
agent-browser wait "#element" # 等待元素可见
agent-browser wait 5000 # 等待 5000 毫秒

### 截图与导出
agent-browser screenshot page.png # 视口截图
agent-browser screenshot --full page.png # 全页截图
agent-browser screenshot --annotate page.png # 注释截图
agent-browser pdf report.pdf # 导出 PDF

## 命令速查
**导航**, 命令=`open <url>`, 说明=打开页面
, 命令=`back`, 说明=后退
, 命令=`forward`, 说明=前进
, 命令=`reload`, 说明=刷新
**交互**, 命令=`click <sel>`, 说明=点击
, 命令=`type <sel> <text>`, 说明=输入
, 命令=`fill <sel> <text>`, 说明=清空并填充
, 命令=`press <key>`, 说明=按键
, 命令=`hover <sel>`, 说明=悬停
, 命令=`check <sel>`, 说明=选中复选框
, 命令=`select <sel> <val>`, 说明=选择下拉项
**信息**, 命令=`snapshot`, 说明=获取快照(AI 友好)
, 命令=`get text <sel>`, 说明=获取文本
, 命令=`get html <sel>`, 说明=获取 HTML
, 命令=`get title`, 说明=获取标题
, 命令=`get url`, 说明=获取 URL
**查找**, 命令=`find role <role> <action>`, 说明=按 ARIA 角色
, 命令=`find text <text> <action>`, 说明=按文本内容
, 命令=`find label <label> <action>`, 说明=按标签文本
**等待**, 命令=`wait <sel\, 说明=ms>`, 等待元素或时间
, 命令=`wait --load networkidle`, 说明=等待网络空闲
, 命令=`wait --text "text"`, 说明=等待文本
**导出**, 命令=`screenshot [path]`, 说明=截图
, 命令=`pdf <path>`, 说明=导出 PDF
**JS**, 命令=`eval <js>`, 说明=执行 JavaScript
**退出**, 命令=`close`, 说明=关闭浏览器

## 集成到 OpenClaw

### 在脚本中使用
#!/bin/bash

# scripts/browser_automation.sh
URL="$1"
OUTPUT_DIR="/tmp/browser"

mkdir -p "$OUTPUT_DIR"

# 打开页面
agent-browser open "$URL"

# 获取快照供 AI 分析
SNAPSHOT_FILE="$OUTPUT_DIR/snapshot.json"
agent-browser snapshot > "$SNAPSHOT_FILE"

SCREENSHOT_FILE="$OUTPUT_DIR/page.png"
agent-browser screenshot "$SCREENSHOT_FILE"

# 输出结果
echo "{\"snapshot\": \"$SNAPSHOT_FILE\", \"screenshot\": \"$SCREENSHOT_FILE\"}"

# 清理

### Python 集成
```python
import subprocess
import json

def browser_open(url):
 """打开网页"""
 subprocess.run(["agent-browser", "open", url])

def browser_snapshot():
 """获取快照"""
 result = subprocess.run(
 ["agent-browser", "snapshot"],
 capture_output=True,
 text=True
 )
 return result.stdout

def browser_click(selector):
 """点击元素"""
 subprocess.run(["agent-browser", "click", selector])

def browser_close():
 """关闭浏览器"""
 subprocess.run(["agent-browser", "close"])

# 示例
browser_open("https://example.com")
snapshot = browser_snapshot()
print(snapshot)
browser_close()

## 完整文档
- SKILL.md - 详细使用指南
- README.md - 本文件

## 外部资源
- [命令参考](https://github.com/vercel-labs/agent-browser#commands)

---

**版本**: v0.13.0
**最后更新**: 2026-02-22
**状态**: 已安装且可用