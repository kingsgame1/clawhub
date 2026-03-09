# SearXNG 搜索技能已创建

## 已安装内容
```
skills/search-searxng/
├── SKILL.md # 技能定义
├── searxng_client.py # SearXNG 客户端(支持自动发现实例)
├── config.json # 配置文件
├── README.md # 使用文档
├── SETUP.md # 安装和配置指南
└── SKILL-INSTALLED.md # 本文件(安装摘要)

---

## ️ 当前状态
**技能结构已完成,但需要自建 SearXNG 实例才能使用.**

由于网络限制,公共 SearXNG 实例在当前环境下不可访问.

## 开始使用

### 步骤 1:部署 SearXNG 实例
```bash

# 使用 Docker(推荐)
docker run -d \
 --name searxng \
 -p 8080:8080 \
 -v ~/searxng-config:/etc/searxng \
 searxng/searxng

# 验证
sleep 10 && curl http://localhost:8080

### 步骤 2:更新配置
编辑 `skills/search-searxng/config.json`:

```json
{
 "instance_url": "http://localhost:8080"
}

### 步骤 3:测试搜索
```python
from skills.search_searxng.searxng_client import SearXNGClient

client = SearXNGClient("http://localhost:8080")
results = client.search("OpenClaw AI agent")
print(client.format_output(results))

## 详细文档
- `README.md`: 使用参考文档, `SETUP.md`: 完整的安装和配置指南, `SKILL.md`: OpenClaw 技能定义

## 功能特性
 多引擎搜索, 状态=已实现, 说明=支持 Google, Bing, DuckDuckGo 等
 专门化搜索, 状态=已实现, 说明=图片,视频,新闻搜索
 自动发现实例, 状态=已实现, 说明=自动检测可用的公共实例
 格式化输出, 状态=已实现, 说明=用户友好的结果显示
️ 实例访问, 状态=需配置, 说明=需要自建或使用可访问的实例

## 替代方案
如果暂时无法使用 SearXNG,可以使用 OpenClaw 原生搜索:

使用 web_search 搜索 OpenClaw AI agent

或使用 Python:

# web_search 是内置工具
web_search("OpenClaw AI agent")

## 帮助
- 查看 `SETUP.md` 了解完整的安装步骤, 查看 `README.md` 了解使用方法, 访问 https://searxng.org/ 获取官方文档

**状态: 技能已创建 | ️ 等待 SearXNG 实例部署**