---
name: agent-browser
description: Vercel Labs 的高性能浏览器自动化 CLI.基于 Rust 构建,支持元素交互,快照,截图,PDF 导出等.无需外部 Playwright/Chrome 依赖.
version: 1.0.0
author: SilverMoon

# Vercel Agent Browser - 高性能浏览器自动化
Vercel Labs 开发的轻量级无头浏览器自动化工具,用 Rust 编写,支持 CLI 命令和 Node.js 回退模式.

## 特点
- **高性能**: Rust CLI 实现,亚毫秒级解析
- **语义定位**: 支持 ARIA role,文本,标签等语义定位器
- **AI 友好**: `snapshot` 命令返回可访问性树(带 ref ID)
- **丰富操作**: 点击,填充,拖拽,截图,PDF,JavaScript 执行
- **无需配置**: 自动下载 Chromium,零依赖启动

## 先决条件
Node.js 18+ 和 npm

```bash
node --version # 需要 >= 18.0.0
npm --version
```

## 安装

### 全局安装(推荐)
npm install -g agent-browser
agent-browser install # 首次下载 Chromium(约150MB)

### 项目依赖
npm install agent-browser
npx agent-browser install # 下载 Chromium

### Linux 依赖
npx agent-browser install --with-deps

## 核心命令

### 导航与交互
agent-browser open <url> # 打开页面(别名:goto, navigate)
agent-browser click <selector> # 点击元素
agent-browser dblclick <selector> # 双击
agent-browser type <selector> <text> # 输入文本
agent-browser fill <selector> <text> # 清空并填充
agent-browser press <key> # 按键(Enter, Tab, Control+a)
agent-browser hover <selector> # 悬停
agent-browser drag <src> <tgt> # 拖拽
agent-browser close # 关闭浏览器

### 信息获取
agent-browser snapshot # 获取可访问性树和 ref ID(AI 最佳)
agent-browser get text <selector> # 获取文本
agent-browser get html <selector> # 获取 innerHTML
agent-browser get value <selector> # 获取输入值
agent-browser screenshot [path] # 截图
agent-browser screenshot --full # 全页截图
agent-browser pdf <path> # 导出 PDF
agent-browser eval <js> # 执行 JavaScript

# 按 ARIA role
agent-browser find role button click --name "Submit"

# 按文本
agent-browser find text "Sign In" click

# 按标签
agent-browser find label "Email" fill "test@example.com"

# 按占位符
agent-browser find placeholder "Search" type "keyword"

# 更多定位器:alt, title, testid, first, last, nth

### 等待条件
agent-browser wait <selector> # 等待元素可见
agent-browser wait 5000 # 等待 5000ms
agent-browser wait --text "Welcome" # 等待文本出现
agent-browser wait --url "**/dash" # 等待 URL 匹配
agent-browser wait --load networkidle # 等待网络空闲

## 典型工作流

# 打开 Google
agent-browser open "https://google.com"

# 填充搜索框
agent-browser find role textbox fill --name "Search" "OpenClaw AI"

# 点击搜索按钮
agent-browser find role button click --name "Google Search"

# 等待结果加载
agent-browser wait --load networkidle

# 获取快照
agent-browser snapshot

# 截图保存
agent-browser screenshot search_results.png

# 关闭
agent-browser close

### 示例 2:表单填写
agent-browser open "https://example.com/login"

# 填写表单
agent-browser find label "Email" fill "user@example.com"
agent-browser find label "Password" type "securepassword"
agent-browser find role checkbox check --name "Remember me"

# 提交
agent-browser find role button click --name "Sign in"

# 等待登录完成
agent-browser wait --url "**/dashboard"

# 验证
agent-browser find text "Welcome" text

### 示例 3:数据抓取
agent-browser open "https://example.com/products"

# 等待列表加载
agent-browser wait ".product-item"

# 获取所有产品名称
agent-browser eval "
 const items = document.querySelectorAll('.product-item .name');
 return Array.from(items).map(el => el.textContent);
" > products.json

# 导出 PDF
agent-browser pdf products.pdf

## 与 OpenClaw 的集成

### 在脚本中使用
#!/bin/bash

# scripts/automate.sh
URL="$1"

if [ -z "$URL" ]; then
 echo "Usage: $0 <url>" >&2
 exit 1
fi

# 打开页面
agent-browser open "$URL"

# 获取快照用于 AI 分析
agent-browser snapshot > /tmp/snapshot.json

# 截图
agent-browser screenshot /tmp/page.png

# 输出快照路径
echo "/tmp/snapshot.json"
echo "/tmp/page.png"

### Python 集成
```python
import subprocess
import json

def browse(url, action="open"):
 """执行 agent-browser 命令"""
 result = subprocess.run(
 ["agent-browser", action, url],
 capture_output=True,
 text=True
 )
 return result.stdout, result.stderr

stdout, stderr = browse("https://example.com")

snapshot = subprocess.run(
 ["agent-browser", "snapshot"],
accessibility_tree = json.loads(snapshot.stdout)

# 使用 ref ID 进行操作
ref_id = accessibility_tree[0]["id"]
subprocess.run(["agent-browser", "click", f"@{ref_id}"])

subprocess.run(["agent-browser", "close"])

## 完整命令列表

### 核心
- `open \<url\>`: 导航到 URL
- `click \<sel\>`: 点击元素
- `type \<sel\> \<text\>`: 输入文本
- `fill \<sel\> \<text\>`: 清空并填充
- `press \<key\>`: 按键, `snapshot`: 获取可访问性树, `screenshot [path]`: 截图
- `pdf \<path\>`: 导出 PDF
- `eval \<js\>`: 执行 JS
- `close`: 关闭浏览器

### 获取信息
| `get text \<sel\>` | 获取文本内容 |
| `get html \<sel\>` | 获取 innerHTML |
| `get value \<sel\>` | 获取输入值 |
| `get attr \<sel\> \<attr\>` | 获取属性 |
| `get title` | 获取页面标题 |
| `get url` | 获取当前 URL |
| `get count \<sel\>` | 计算匹配元素 |

### 查找元素
| `find role \<role\> <action>` | 按 ARIA role |
| `find text \<text\> <action>` | 按文本内容 |
| `find label \<label\> <action>` | 按标签文本 |
| `find placeholder \<ph\> <action>` | 按占位符 |

## 高级功能

### 注释截图
agent-browser screenshot --annotate # 带元素编号的截图

### 检查状态
agent-browser is visible <selector>
agent-browser is enabled <selector>
agent-browser is checked <selector>

### 鼠标控制
agent-browser mouse move <x> <y>
agent-browser mouse down <button>
agent-browser mouse up <button>
agent-browser mouse wheel <dy>

## 错误处理

# 使用 --name 精确匹配
agent-browser find role button click --name --exact "Submit"

# 增加等待时间
agent-browser wait 5000

# 检查页面是否加载
agent-browser get title

## 最佳实践
1. **优先使用语义定位器**: `find role button` 比 `#submit` 更可靠
2. **使用 snapshot 进行 AI 分析**: 输出包含 ref ID 的可访问性树
3. **网络空闲等待**: `wait --load networkidle` 比固定时间更安全
4. **清理浏览器**: 每次任务后执行 `agent-browser close`

## 限制
- 不支持多标签页并行(需多次 `open`), 需要网络下载 Chromium(首次使用), 依赖系统图形库(Linux 需要额外依赖)

## 参考资料
- 完整文档: https://github.com/vercel-labs/agent-browser
- Vercel Labs: https://github.com/vercel-labs

**最后更新**: 2026-02-22