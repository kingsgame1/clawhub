# SearXNG 搜索技能 - 安装与配置

## ️ 重要说明
由于网络限制,当前环境下的公共 SearXNG 实例不可访问.为了使用此技能,需要:

1. **自建 SearXNG 实例**(推荐)
2. 使用 OpenClaw 原生的 `web_search` 工具作为替代方案

---

## 方案 1:自建 SearXNG 实例(推荐)

### 使用 Docker 快速部署
```bash

# 1. 拉取镜像
docker pull searxng/searxng

# 2. 创建配置目录
mkdir -p ~/searxng-config

# 3. 运行容器
docker run -d \
 --name searxng \
 -p 8080:8080 \
 -v ~/searxng-config:/etc/searxng \
 searxng/searxng

# 4. 等待启动(约10秒)
sleep 10

# 5. 验证
curl http://localhost:8080/search?q=test&format=json
```

### 配置技能
更新 `skills/search-searxng/config.json`:

```json
{
 "instance_url": "http://localhost:8080",
 "default_engines": ["google", "bing", "duckduckgo"],
 "default_language": "en",
 "default_limit": 10,
 "safe_search": 0,
 "timeout": 10
}

### 使用 Docker Compose(推荐)
创建 `docker-compose.yml`:

```yaml
version: '3'

services:
 searxng:
 image: searxng/searxng
 container_name: searxng
 ports:
 - "8080:8080"
 volumes:
 - ./searxng-config:/etc/searxng
 environment:
 - SEARXNG_HOSTNAME=localhost
 - SEARXNG_PORT=8080
 restart: unless-stopped

启动:

docker-compose up -d

## 方案 2:配置搜索引擎
SearXNG 支持配置多个搜索引擎.编辑配置文件 `~/searxng-config/settings.yml`:

engines:
 - name: google
 engine: google
 shortcut: go

 - name: duckduckgo
 engine: duckduckgo
 shortcut: ddg

 - name: bing
 engine: bing
 shortcut: bi

 - name: wikipedia
 engine: wikipedia
 shortcut: wp

 - name: github
 engine: github
 shortcut: gh

## 方案 3:使用 OpenClaw 原生搜索
如果暂无法自建 SearXNG,可以使用 OpenClaw 自带的搜索工具:

```python

# web_search 是内置工具,无需额外配置
from web_search import web_search

results = web_search("OpenClaw AI agent")

## 使用示例

### Python 脚本
from skills.search_searxng.searxng_client import SearXNGClient

# 初始化客户端
client = SearXNGClient("http://localhost:8080")

# 基本搜索
results = client.search("Python 异步编程")
print(client.format_output(results))

# 指定引擎
results = client.search(
 "AI agent",
 engines=["google", "bing"],
 limit=5
)

# 搜索图片
results = client.search_images("猫咪壁纸")

# 搜索新闻
results = client.search_news("AI technology")

### 在 OpenClaw 中
搜索 OpenClaw AI agent
在 google 搜索 Python 教程
搜索图片 猫咪
搜索新闻 AI 技术

## ️ 故障排除

# 检查容器状态
docker ps | grep searxng

# 查看日志
docker logs searxng

# 测试连接
curl http://localhost:8080

### 问题:返回 HTML 而非 JSON
可能是实例使用了反爬虫保护.需要:
1. 在配置中添加 User-Agent(已在代码中实现)
2. 或使用自建实例

### 问题:搜索结果为空
1. 检查搜索引擎配置
2. 尝试不同的引擎组合
3. 检查查询语言设置

## 相关资源
- SearXNG 官网: https://searxng.org/, SearXNG GitHub: https://github.com/searxng/searxng, Docker Hub: https://hub.docker.com/r/searxng/searxng, 公共实例列表: https://searx.space/

## 支持
如有问题,请查看:
1. `skills/search-searxng/README.md` - 使用文档
2. `skills/search-searxng/config.json` - 配置文件
3. SearXNG 官方文档

**建议**: 在生产环境中使用自建 SearXNG 实例,以获得更稳定和可控的搜索服务.