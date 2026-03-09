---
name: jina-reader
description: 使用 Jina Reader 提取任意网页/推文的纯文本内容.免费,无需 API Key,输出 Markdown 格式.支持动态网页,Twitter/X,PDF 等.
version: 1.0.0
author: SilverMoon

# Jina Reader 技能
免费提取任意网页的纯文本内容,输出 Markdown 格式.

## 特点
- **免费**:无需 API Key,无限制, **快速**:秒级响应, **干净**:输出结构化 Markdown, **广泛支持**:动态网页,Twitter/X,PDF,GitHub 等

## 使用方法

### 基础用法
```bash
curl -s "https://r.jina.ai/<URL>"
```

# 提取网页
curl -s "https://r.jina.ai/https://example.com"

# 提取推文
curl -s "https://r.jina.ai/https://x.com/user/status/123456"

# 提取 GitHub README
curl -s "https://r.jina.ai/https://github.com/user/repo"

# 提取 PDF
curl -s "https://r.jina.ai/https://example.com/doc.pdf"

## 脚本

### `scripts/fetch.sh`
#!/bin/bash

# Jina Reader 封装脚本
URL="$1"

if [ -z "$URL" ]; then
 echo "Usage: $0 <URL>" >&2
 exit 1
fi

curl -s "https://r.jina.ai/$URL"

## 高级选项
Jina Reader 支持以下查询参数:

`output`, 说明=输出格式, 示例=`?output=markdown` (默认)
`cached`, 说明=使用缓存, 示例=`?cached=true`

完整文档:https://jina.ai/reader

## 最佳实践
1. **优先使用**:比 `web_fetch` 更稳定,支持更多网站
2. **Twitter/X**:完美支持,无需登录
3. **错误处理**:如果返回空内容,可能网站被屏蔽,尝试 `playwright-scraper-skill`

## 限制
- 不支持需要登录的页面, 部分反爬虫网站可能失败, 大文件可能超时