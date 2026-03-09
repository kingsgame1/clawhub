#!/usr/bin/env python3
"""
SearXNG 搜索客户端
支持多引擎网络搜索，返回结构化结果
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class SearXNGClient:
    """SearXNG 搜索客户端"""

    # 公共 SearXNG 实例列表（按稳定性排序）
    PUBLIC_INSTANCES = [
        "https://search.wdyl.org",
        "https://searx.be",
        "https://searxng.zhenyapeng.com",
    ]

    def __init__(self, base_url: Optional[str] = None):
        """
        初始化客户端

        Args:
            base_url: SearXNG 实例地址，如果为 None 则自动选择
        """
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = self._find_available_instance()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def _find_available_instance(self) -> str:
        """查找可用的公共实例"""
        for instance in self.PUBLIC_INSTANCES:
            try:
                response = requests.get(
                    f"{instance}/search",
                    params={"q": "test", "format": "json"},
                    timeout=5
                )
                if response.status_code == 200 and "results" in response.text[:200]:
                    print(f"✅ 使用 SearXNG 实例: {instance}")
                    return instance
            except Exception:
                continue

        print("⚠️  未找到可用的公共实例，使用默认配置")
        return "https://search.wdyl.org"

    def search(
        self,
        query: str,
        engines: Optional[List[str]] = None,
        categories: Optional[str] = None,
        language: str = "en",
        time_range: Optional[str] = None,
        safe_search: int = 0,
        page: int = 1,
        format: str = "json",
        limit: int = 10
    ) -> Dict:
        """
        执行搜索

        Args:
            query: 搜索关键词
            engines: 搜索引擎列表，如 ["google", "bing", "duckduckgo"]
            categories: 搜索分类，如 "general", "images", "videos", "news"
            language: 搜索语言，如 "zh-CN", "en", "all"
            time_range: 时间范围，如 "day", "week", "month", "year"
            safe_search: 安全搜索等级 (0-2)
            page: 页码
            format: 返回格式，"json" 或 "html"
            limit: 返回结果数量

        Returns:
            搜索结果字典
        """
        params = {
            "q": query,
            "format": format,
            "language": language,
            "pageno": page,
            "safesearch": safe_search,
        }

        if engines:
            params["engines"] = ",".join(engines)

        if categories:
            params["category"] = categories

        if time_range:
            params["time_range"] = time_range

        try:
            url = f"{self.base_url}/search"
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}",
                    "query": query,
                    "instance": self.base_url
                }

            results = response.json()

            # 格式化结果
            return self._format_results(results, limit)

        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "返回的不是有效的 JSON 格式。可能实例使用了反爬虫保护。",
                "query": query,
                "instance": self.base_url,
                "suggestion": "建议：使用 Docker 自建 SearXNG 实例，或使用 OpenClaw 的原生 web_search 工具。"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "query": query,
                "instance": self.base_url
            }

    def _format_results(self, raw_results: Dict, limit: int) -> Dict:
        """格式化搜索结果"""
        formatted = {
            "success": True,
            "query": raw_results.get("query"),
            "results": [],
            "answers": [],
            "infoboxes": [],
            "suggestions": [],
            "engines": []
        }

        # 提取搜索结果
        for result in raw_results.get("results", [])[:limit]:
            formatted["results"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "engine": result.get("engine", ""),
                "score": result.get("score", 0),
                "category": result.get("category", "")
            })

        # 提取直接答案
        for answer in raw_results.get("answers", []):
            formatted["answers"].append({
                "answer": answer.get("content", ""),
                "engine": answer.get("engine", "")
            })

        # 提取信息框
        for infobox in raw_results.get("infoboxes", []):
            formatted["infoboxes"].append({
                "title": infobox.get("infobox", ""),
                "content": infobox.get("content", ""),
                "attributes": infobox.get("attributes", {})
            })

        # 提取搜索建议
        for suggestion in raw_results.get("suggestions", []):
            formatted["suggestions"].append(suggestion)

        # 提取使用的引擎
        formatted["engines"] = list(set(r.get("engine", "") for r in raw_results.get("results", [])))

        return formatted

    def search_images(self, query: str, limit: int = 10) -> Dict:
        """搜索图片"""
        return self.search(
            query=query,
            categories="images",
            limit=limit
        )

    def search_videos(self, query: str, limit: int = 10) -> Dict:
        """搜索视频"""
        return self.search(
            query=query,
            categories="videos",
            limit=limit
        )

    def search_news(self, query: str, limit: int = 10) -> Dict:
        """搜索新闻"""
        return self.search(
            query=query,
            categories="news",
            limit=limit
        )

    def format_output(self, results: Dict, show_details: bool = False) -> str:
        """将搜索结果格式化为易读的文本"""
        if not results.get("success"):
            output = [f"❌ 搜索失败"]
            output.append(f"查询: {results.get('query', 'N/A')}")
            output.append(f"实例: {results.get('instance', 'N/A')}")
            output.append(f"原因: {results.get('error', 'unknown')}")

            if results.get("suggestion"):
                output.append(f"\n💡 建议: {results['suggestion']}")

            return "\n".join(output)

        lines = []
        query = results.get("query", "")

        # 标题
        lines.append(f"\n🔍 SearXNG 搜索: {query}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # 直接答案
        if results.get("answers"):
            lines.append("💡 直接答案:")
            for answer in results["answers"]:
                lines.append(f"  • {answer['answer']}")
            lines.append("")

        # 信息框
        if results.get("infoboxes"):
            for infobox in results["infoboxes"]:
                lines.append(f"📋 {infobox['title']}")
                lines.append(f"   {infobox['content']}")
                lines.append("")

        # 搜索结果
        if results.get("results"):
            lines.append(f"📊 搜索结果 ({len(results['results'])} 条):")

            for i, result in enumerate(results["results"], 1):
                lines.append(f"\n{i}. {result['title']}")
                lines.append(f"   🔗 {result['url']}")

                if result.get("content"):
                    content = result['content'][:150] if len(result['content']) > 150 else result['content']
                    lines.append(f"   {content}...")

                if show_details:
                    lines.append(f"   来源: {result.get('engine', 'unknown')} | 评分: {result.get('score', 0)}")

            lines.append("")

        # 搜索建议
        if results.get("suggestions"):
            lines.append("💭 相关搜索:")
            for suggestion in results["suggestions"][:5]:
                lines.append(f"  • {suggestion}")
            lines.append("")

        # 使用的引擎
        if results.get("engines"):
            lines.append(f"🔧 使用引擎: {', '.join(results['engines'])}")

        return "\n".join(lines)


def main():
    """演示用法"""
    print("=" * 60)
    print("🔍 SearXNG 搜索测试")
    print("=" * 60)

    client = SearXNGClient()

    # 示例 1: 基本搜索
    print("\n测试 1: 基本搜索 'OpenClaw'")
    print("-" * 60)
    results = client.search("OpenClaw", limit=3)
    print(client.format_output(results))

    # 示例 2: 简单测试
    print("\n测试 2: 搜索 'AI agent'")
    print("-" * 60)
    results = client.search("AI agent", limit=2)
    print(client.format_output(results))


if __name__ == "__main__":
    main()
