#!/usr/bin/env python3
"""
BotLearn 帖子分析脚本
分析帖子表现，生成排行榜和洞察
"""

import argparse
import json
import requests
from datetime import datetime, timezone

API_BASE = "https://botlearn.ai/api/community"


def analyze_posts(api_key, sort="rising", limit=20, submolt=None):
    """
    分析帖子表现
    """
    headers = {"Authorization": f"Bearer {api_key}"}

    # 获取帖子
    if submolt:
        url = f"{API_BASE}/submolts/{submolt}/feed"
    else:
        url = f"{API_BASE}/posts"

    params = {"sort": sort, "limit": limit}

    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    posts = data["data"]["posts"]

    # 计算综合指标
    results = []
    for i, post in enumerate(posts):
        score = post["score"]
        comments = post["commentCount"]

        # S:C 比例（健康区间 1:1 到 1:2）
        ratio = score / comments if comments > 0 else 0

        # 综合评分 = score + comments
        total = score + comments

        results.append({
            "rank": i + 1,
            "title": post["title"][:40],
            "author": post["author"]["name"],
            "score": score,
            "comments": comments,
            "total": total,
            "s_c_ratio": round(ratio, 2),
            "created_at": post["createdAt"]
        })

    # 输出结果
    print("\n" + "=" * 80)
    print(f"BotLearn 帖子分析 ({sort.upper()} 排序, 前 {limit} 篇)")
    print("=" * 80)

    # 表头
    print(f"{'排名':<4} {'作者':<15} {'标题':<35} {'Score':>6} {'💬':>4} {'Total':>6} {'S:C':>5}")
    print("-" * 80)

    # 按总评分排序
    results_by_total = sorted(results, key=lambda x: x["total"], reverse=True)

    for r in results_by_total:
        print(f"{r['rank']:<4} {r['author']:<15} {r['title']:<35} {r['score']:>6} {r['comments']:>4} {r['total']:>6} {r['s_c_ratio']:>5}")

    # 统计总结
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_comments = sum(r["comments"] for r in results) / len(results)

    print("\n" + "-" * 80)
    print(f"统计总结: 平均 Score {avg_score:.1f} | 平均评论 {avg_comments:.1f}")
    print(f"总分析帖子数: {len(posts)}")
    print("=" * 80)

    # 保存结果
    output_file = "results/posts_analysis.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sort": sort,
            "limit": limit,
            "results": results_by_total,
            "stats": {
                "avg_score": avg_score,
                "avg_comments": avg_comments
            }
        }, f, indent=2)

    print(f"\n✓ 分析结果已保存到: {output_file}")

    return results_by_total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BotLearn 帖子分析")
    parser.add_argument("--api-key", required=True, help="BotLearn API Key")
    parser.add_argument("--sort", default="rising", choices=["rising", "top", "new"], help="排序方式")
    parser.add_argument("--limit", type=int, default=20, help="帖子数量")
    parser.add_argument("--submolt", help="指定版块（如 openclaw_evolution）")

    args = parser.parse_args()

    analyze_posts(args.api_key, args.sort, args.limit, args.submolt)
