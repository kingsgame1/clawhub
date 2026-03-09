# SearXNG 搜索技能
使用 SearXNG 进行多引擎网络搜索的 OpenClaw 技能.

## 文件结构
```
search-searxng/
├── SKILL.md # 技能定义(供 OpenClaw 识别)
├── searxng_client.py # SearXNG 客户端实现
├── config.json # 配置文件
└── README.md # 本文件

## 快速开始

### 基本搜索
```python
from skills.search_searxng.searxng_client import SearXNGClient

client = SearXNGClient()
results = client.search("比特币价格预测")
print(client.format_output(results))

### 指定引擎
results = client.search(
 "Python 异步编程",
 engines=["google", "bing", "duckduckgo"],
 limit=5
)

### 搜索图片
results = client.search_images("猫咪壁纸", limit=10)

### 搜索新闻
results = client.search_news("AI technology", limit=5)

### 搜索视频
results = client.search_videos("Python 教程", limit=5)

## ️ 配置
编辑 `config.json`:

```json
{
 "instance_url": "https://searx.work", // SearXNG 实例地址
 "default_engines": ["google", "bing", "duckduckgo"],
 "default_language": "zh-CN",
 "default_limit": 10,
 "safe_search": 0, // 安全搜索等级 (0-2)
 "timeout": 10
}

### 可用的引擎
- `google` - Google 搜索
- `bing` - Microsoft Bing
- `duckduckgo` - DuckDuckGo, `wikipedia` - 维基百科, `github` - GitHub
- `stackoverflow` - Stack Overflow
- `reddit` - Reddit, `youtube` - YouTube, `news` - 新闻聚合

更多引擎请参考 SearXNG 文档.

## 结果格式
搜索结果包含以下部分:

 "success": True,
 "query": "搜索关键词",
 "results": [
 "title": "结果标题",
 "url": "https://example.com",
 "content": "结果摘要...",
 "engine": "google",
 "score": 1.0,
 "category": "general"
 ],
 "answers": [...], # 直接答案
 "infoboxes": [...], # 信息框
 "suggestions": [...], # 搜索建议
 "engines": [...] # 使用的引擎

## 使用场景
1. **多源信息聚合**: 同时查询多个搜索引擎
2. **隐私敏感搜索**: 无用户追踪
3. **定制化搜索**: 选择特定引擎或分类
4. **新闻/图片/视频搜索**: 专门化搜索

## 自定义部署

### 使用 Docker 部署自建实例
```bash

# 拉取镜像
docker pull searxng/searxng

# 运行容器
docker run -d \
 --name searxng \
 -p 8080:8080 \
 -v ${PWD}/searxng:/etc/searxng \
 searxng/searxng

# 访问
open http://localhost:8080

然后更新 `config.json`:

 "instance_url": "http://localhost:8080"

## 故障排除
**问题:搜索失败或无结果**

解决:检查 instance_url 是否可访问
 尝试更换公共实例:
 - https://searx.work
 - https://search.wdyl.org

**问题:结果不相关**

解决:使用更精确的关键词
 指定 engines 参数选择更适合的搜索引擎

## 相关资源
- SearXNG 官网: https://searxng.org/, SearXNG GitHub: https://github.com/searxng/searxng, 公共实例列表: https://searx.space/

## 贡献
欢迎提交问题和改进建议!