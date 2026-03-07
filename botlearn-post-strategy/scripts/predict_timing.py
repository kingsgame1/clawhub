#!/usr/bin/env python3
"""
发帖时间预测器
基于历史数据，预测最佳发帖时间
"""

import argparse
import json
from datetime import datetime, timezone
from collections import defaultdict


def load_history(file_path):
    """加载历史数据"""
    with open(file_path) as f:
        return json.load(f)


def predict_timing(history, time_zone="Asia/Shanghai"):
    """预测最佳发帖时间"""
    posts = history.get("posts", [])

    print("\n" + "=" * 80)
    print(f"⏰ 最佳发帖时间预测（时区: {time_zone}）")
    print("=" * 80)

    # 分析发帖时间分布
    hour_counts = defaultdict(int)
    hour_scores = defaultdict(list)

    for post in posts:
        # 解析时间
        created_at = post.get("createdAt", "")
        if not created_at:
            continue

        # 提取 UTC 小时
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            utc_hour = dt.hour
        except:
            continue

        hour_counts[utc_hour] += 1
        hour_scores[utc_hour].append(post.get("score", 0))

    # 计算每小时的平均 Score
    hour_avg_scores = {}
    for hour in hour_counts:
        if hour_scores[hour]:
            hour_avg_scores[hour] = sum(hour_scores[hour]) / len(hour_scores[hour])

    # 找出最佳时段
    if hour_avg_scores:
        sorted_hours = sorted(hour_avg_scores.items(), key=lambda x: x[1], reverse=True)

        print("\n📊 按小时分析（UTC 时间）:")
        print(f"{'小时':<6} {'发帖数':<8} {'平均 Score':<12} {'推荐指数':<8}")
        print("-" * 60)

        for hour, avg_score in sorted_hours[:10]:
            count = hour_counts[hour]
            # 推荐指数 = 平均 Score * (1 + log(发帖数))
            rec_index = avg_score * (1 + (count > 5) * 0.5)

            star = "⭐" if avg_score > 5 else " "
            print(f"{hour:02d}:00  {count:<8} {avg_score:<12.1f} {rec_index:<8.1f} {star}")

    # 竞争对手分析
    competitors = defaultdict(list)
    for post in posts:
        author = post.get("author", {}).get("name", "Unknown")
        if author in ["HappyCapy", "Zen", "Helix"]:
            try:
                dt = datetime.fromisoformat(post["createdAt"].replace("Z", "+00:00"))
                competitors[author].append(dt.hour)
            except:
                pass

    if competitors:
        print("\n🔍 竞争对手活跃时段（UTC）:")
        for author, hours in competitors.items():
            if hours:
                avg_hour = sum(hours) / len(hours)
                print(f"  {author}: 平均活跃于 {avg_hour:02d}:00")

    # 建议
    print("\n💡 发帖建议:")

    # 避开高峰冲突
    print("  1. 避开冲突:")
    print("     - 如果 top5 帖子刚发布，等待 30-60 分钟")
    print("     - 竞争对手刚发重大帖子，延后 2 小时")

    # 抓住高峰
    print("\n  2. 抓住高峰:")
    if sorted_hours:
        best_hour = sorted_hours[0][0]
        print(f"     - UTC {best_hour:02d}:00 前后 2 小时最佳")
        print(f"     - 对应北京时间 {best_hour + 8:02d}:00（如果过夜则 -16 小时）")

    # 持续性
    print("\n  3. 持续性策略:")
    print("     - 初始阶段：每 2 小时发 1 篇")
    print("     - 数据积累后：每 1 小时发 1 篇")
    print("     - 成熟期：每 30 分钟发 1 篇，但避免刷屏")

    # 禁忌
    print("\n  4. 禁忌事项:")
    print("     ❌ 清晨（UTC 00:00-04:00）- 活跃用户少")
    print("     ❌ 刚注册时密集发帖（触发限流）")
    print("     ❌ 纯推广内容（无数据、无观点）")

    print("\n" + "=" * 80)

    return sorted_hours


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="预测发帖时间")
    parser.add_argument("--history", required=True, help="历史数据文件")
    parser.add_argument("--time-zone", default="Asia/Shanghai", help="时区")

    args = parser.parse_args()

    # 如果提供的是 analyze_posts 的输出，需要构造
    import sys
    history_data = {"posts": []}

    try:
        with open(args.history) as f:
            data = json.load(f)
            if "results" in data:
                # 转换格式
                for r in data["results"]:
                    history_data["posts"].append({
                        "createdAt": r.get("created_at", ""),
                        "score": r.get("score", 0),
                        "author": {"name": r.get("author", "")}
                    })
            else:
                history_data = data
    except:
        print(f"错误：无法读取 {args.history}")
        sys.exit(1)

    predict_timing(history_data, args.time_zone)
