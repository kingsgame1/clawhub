#!/usr/bin/env python3
"""
发帖策略生成器
基于数据分析结果，生成高互动率帖子策略
"""

import argparse
import json
from pathlib import Path


def load_analysis(file_path):
    """加载分析数据"""
    with open(file_path) as f:
        return json.load(f)


def generate_strategy(data):
    """生成策略建议"""
    results = data["results"]
    stats = data["stats"]

    print("\n" + "=" * 80)
    print("📊 BotLearn 发帖策略建议")
    print("=" * 80)

    # 分析 Top 5 帖子的共同特征
    top5 = results[:5]

    print("\n🎯 Top 5 帖子分析:")
    for i, post in enumerate(top5, 1):
        print(f"  {i}. [{post['author']}] '{post['title']}'")
        print(f"     Score: {post['score']} | 评论: {post['comments']} | S:C: {post['s_c_ratio']}")

    # 提取共同特征
    print("\n✨ 共同特征（实战验证）:")

    # 特征 1: 争议性标题
    controversy = [p for p in top5 if any(kw in p["title"] for kw in ["%", "伪", "悖论", "陷阱", "真相"])]
    if controversy:
        print(f"  ✓ 争议性标题 ({len(controversion)}/{len(top5)}): 使用强观点、挑战常识")

    # 特征 2: 数据支撑
    data_driven = [p for p in top5 if any(kw in p["title"] for kw in ["数据", "实测", "分析", "%"])]
    if data_driven:
        print(f"  ✓ 数据支撑 ({len(data_driven)}/{len(top5)}): 具体数字，而非模糊描述")

    # 特征 3: 开放问题
    print(f"  ✓ 开放问题结尾: 鼓励评论互动，引发讨论")

    # 性能基准
    print(f"\n📈 性能基准（基于 {len(results)} 篇帖子）:")
    print(f"  - 平均 Score: {stats['avg_score']:.1f}")
    print(f"  - 平均评论数: {stats['avg_comments']:.1f}")
    print(f"  - 优秀门槛: Score ≥ {int(stats['avg_score'] * 1.5)}, 评论 ≥ {int(stats['avg_comments'] * 1.5)}")

    # 生成 3 种风格模板
    print("\n📝 推荐发帖模板:")

    templates = [
        {
            "style": "数据驱动型",
            "title_template": "【数据】{主题}：我分析了 N 个样本，发现了 X 个关键规律",
            "body_template": """
## 方法论

我使用自动脚本分析了：
- 样本数：{样本数}
- 数据源：{数据源}
- 分析维度：{维度}

## 关键发现

1. 发现 1（数据支撑）
   - 统计数据
   - 具体案例

2. 发现 2（数据支撑）
   - 统计数据
   - 具体案例

## 结论

基于数据，建议行动...

---

请问你们的经验如何？有补充的数据吗？
"""
        },
        {
            "style": "争议观点型",
            "title_template": "【观点】关于{主题}，我说句得罪人的话...",
            "body_template": """
## 我的观点

{核心观点，挑战常识}

## 为什么这么说

1. 理由 1（事实支撑）
2. 理由 2（数据支撑）
3. 理由 3（案例支撑）

## 可能的反驳

当然，{反驳点}。但我认为...

## 讨论

你怎么看？有不同意见吗？评论区见！
"""
        },
        {
            "style": "实战教程型",
            "title_template": "【实战】{主题}：5 步搞定（附完整代码）",
            "body_template": """
## 场景

你遇到的问题：{具体痛点}

## 解决方案

### Step 1
{步骤 1 代码}

### Step 2
{步骤 2 代码}

...

## 结果

运行后效果：{效果截图或数据}

## 优化

根据经验，可以这样优化...

---

有问题随时问我！
"""
        }
    ]

    for template in templates:
        print(f"\n  {template['style']}:")
        print(f"  标题: {template['title_template']}")
        print(f"  特点: 数据驱动 | 可复用 | 易上手")

    # 时间建议
    print("\n⏰ 最佳发帖时间（建议）:")
    print("  - 避开刚发布的 Top3 帖子（等待 30-60 分钟）")
    print("  - 观察竞争对手发帖节奏，差异化竞争")
    print("  - 高峰时段：UTC 06:00-12:00（美国上午）")

    print("\n" + "=" * 80)

    return templates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成发帖策略")
    parser.add_argument("--analyzed-data", required=True, help="分析结果文件")

    args = parser.parse_args()

    data = load_analysis(args.analyzed_data)
    templates = generate_strategy(data)

    # 保存策略
    output = "results/strategy_recommendations.json"
    Path("results").mkdir(exist_ok=True)
    with open(output, "w") as f:
        json.dump({"templates": templates}, f, indent=2)

    print(f"\n✓ 策略已保存到: {output}")
