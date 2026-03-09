# Agent Browser - 快速参考卡

## 十秒钟上手
```bash

# 打开网页
agent-browser open https://example.com

# 等待加载
agent-browser wait --load networkidle

# 获取快照 (AI 友好)
agent-browser snapshot

# 截图
agent-browser screenshot page.png

# 关闭
agent-browser close
```

---

## 常用命令速查

### 基础操作
`open <url>`, 说明=打开网页, 示例=`open https://google.com`
`snapshot`, 说明=获取快照, 示例=`snapshot > tree.json`
`screenshot [path]`, 说明=截图, 示例=`screenshot page.png`
`close`, 说明=关闭浏览器, 示例=`close`

### 表单交互
| `fill <sel> <text>` | 填充输入框 | `fill "#email" "user@ex.com"` |
| `type <sel> <text>` | 输入文本 | `type "#search" "keyword"` |
| `select <sel> <val>` | 选择下拉 | `select "#size" "medium"` |
| `check <sel>` | 选中复选框 | `check "#remember"` |

### 点击操作
| `click <sel>` | 点击元素 | `click "#submit"` |
| `dblclick <sel>` | 双击 | `dblclick "#item"` |

### 查找元素(推荐)
| `find role <role> <action>` | 按 ARIA 角色 | `find role button click --name "Submit"` |
| `find text <text> <action>` | 按文本 | `find text "Sign In" click` |
| `find label <label> <action>` | 按标签 | `find label "Email" fill "user@ex.com"` |

### 等待条件
| `wait --load networkidle` | 等待网络空闲 | `wait --load networkidle` |
| `wait --text "text"` | 等待文本出现 | `wait --text "Welcome"` |
| `wait <selector>` | 等待元素可见 | `wait "#content"` |
| `wait 5000` | 等待 5000 毫秒 | `wait 5000` |

### JavaScript
| `eval <js>` | 执行 JS | `eval "document.title"` |

## 完整工作流示例

### 示例 1:搜索
agent-browser open https://www.google.com
agent-browser find role textbox fill --name "Search" "OpenClaw AI"
agent-browser find role button click --name "Google Search"
agent-browser screenshot search.png

### 示例 2:登录
agent-browser open https://example.com/login
agent-browser wait "#email"
agent-browser fill "#email" "user@example.com"
agent-browser fill "#password" "secret"
agent-browser click "#submit"
agent-browser wait --url "**/dashboard"

### 示例 3:数据抓取
agent-browser eval '
 const items = document.querySelectorAll("h1, h2, h3");
 return Array.from(items).map(el => el.textContent);
' > titles.txt

## 常见问题

### 问题:打不开网页
**解决**: 检查 URL,确保以 `https://` 或 `http://` 开头

### 问题:元素未找到
**解决**:
- 使用 `wait` 等待元素加载
- 使用语义定位器 (`find role`, `find text`)

### 问题:截图失败
- 确保先打开网页, 使用绝对路径保存截图, 检查目录权限

## 相关资源
- **完整文档**: `SKILL.md`, **快速开始**: `README.md`, **帮助命令**: `agent-browser --help`

**版本**: v0.13.0
**最后更新**: 2026-02-22