# SearXNG 网络搜索技能
使用 SearXNG 进行多引擎网络搜索,支持 Google,Bing,DuckDuckGo 等多个搜索引擎.

## 配置
- **实例地址**: http://localhost:8080 或公共实例 https://searx.work
- **默认引擎**: google,bing,duckduckgo
- **结果数量**: 默认 10 条

## 使用方法
```
搜索 [关键词]
在 [搜索引擎] 搜索 [关键词]
搜索关于 [主题] 的内容

## 可用参数
- **搜索引擎**: google, bing, duckduckgo, wikipedia, github, stackoverflow 等
- **结果数量**: 1-20 条
- **语言**: 可指定搜索语言

## 示例
搜索 比特币价格预测
在 google 搜索 AI agent 编排
搜索 SearXNG 部署教程

## 高级用法
搜索 Python 异步编程教程,使用 google,返回 5 条结果
搜索 cryptocurrency 市场,使用 bing 和 duckduckgo

## 功能特点
- **多引擎聚合**: 同时查询多个搜索引擎, **隐私保护**: 无用户追踪, **高度可定制**: 支持自定义引擎,分类, **JSON 输出**: 易于程序化处理

## 相关技能
- `jina-reader` - 网页内容提取
- `web-search` - 原生网络搜索工具