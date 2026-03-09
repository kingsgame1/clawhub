"""
Task Evaluator - 任务质量评估器（ClawWork 适配）
评估 Moltx Article 和 BotLearn 互动的质量，计算报酬
"""

import json
import logging
from typing import Dict, Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskEvaluator:
    """
    任务评估器
        
    功能：
    - 评估 Moltx Article 质量（基于 likes/comments）
    - 评估 BotLearn 互动质量（基于互动数据）
    - 计算任务报酬（应用质量阈值）
    """

    def __init__(self, min_threshold: float = 0.6):
        """
        初始化评估器
        
        Args:
            min_threshold: 质量阈值（默认 0.6）
        """
        self.min_threshold = min_threshold

        # 任务基础价值（美元）
        self.base_values = {
            "moltx_article": 10.0,
            "moltx_comment": 2.0,
            "botlearn_comment": 2.0,
            "botlearn_post": 15.0,
            "crypto_research": 20.0,
            "strategy_optimization": 50.0
        }

    def evaluate_moltx_article(
        self,
        article_id: str,
        likes: int = 0,
        comments: List[Dict] = None,
        shares: int = 0
    ) -> Dict[str, float]:
        """
        评估 Moltx Article 质量
        
        Args:
            article_id: Article ID
            likes: 点赞数
            comments: 评论列表 [{"agent_id": "...", "content": "..."}]
            shares: 分享数
            
        Returns:
            评估结果 {"quality_score": float, "calculated_payment": float}
        """
        if comments is None:
            comments = []

        # 质量评分计算（0-1）
        # 基础分 0.3（发布就有价值）
        # 点赞奖励：最多 0.3（每点赞 +0.02，上限 15赞）
        # 评论奖励：最多 0.3（每评论 +0.05，上限 6 条）
        # 分享奖励：最多 0.1（每分享 +0.02，上限 5 次分享）

        quality_score = 0.0

        # 基础分
        quality_score += 0.3

        # 点赞奖励
        likes_bonus = min(likes * 0.02, 0.3)
        quality_score += likes_bonus

        # 评论奖励
        comments_bonus = min(len(comments) * 0.05, 0.3)
        quality_score += comments_bonus

        # 分享奖励
        shares_bonus = min(shares * 0.02, 0.1)
        quality_score += shares_bonus

        # 上限 1.0
        quality_score = min(quality_score, 1.0)

        # 计算报酬
        base_value = self.base_values.get("moltx_article", 10.0)
        calculated_payment = self._apply_threshold(base_value, quality_score)

        logger.info(f"📝 Moltx Article 评估: {article_id}")
        logger.info(f"   质量: {quality_score:.2f} (likes={likes}, comments={len(comments)})")
        logger.info(f"   报酬: ${calculated_payment:.2f} (base=${base_value:.2f})")

        return {
            "quality_score": quality_score,
            "calculated_payment": calculated_payment,
            "base_value": base_value,
            "metrics": {
                "likes": likes,
                "comments": len(comments),
                "shares": shares
            }
        }

    def evaluate_botlearn_interaction(
        self,
        activity_type: str,
        activity_id: str,
        likes_received: int = 0,
        replies_received: int = 0,
        content_length: int = 0
    ) -> Dict[str, float]:
        """
        评估 BotLearn 互动质量
        
        Args:
            activity_type: 活动类型 ("comment" 或 "post")
            activity_id: 活动 ID
            likes_received: 收到的点赞数
            replies_received: 收到的回复数
            content_length: 内容长度（字符数）
            
        Returns:
            评估结果
        """
        # 质量评分
        quality_score = 0.0

        # 基础分 0.2
        quality_score += 0.2

        # 内容长度奖励（有意义的内容至少 50 字符）
        if content_length >= 50:
            quality_score += 0.1
            if content_length >= 150:
                quality_score += 0.1

        # 互动奖励
        likes_bonus = min(likes_received * 0.05, 0.3)
        quality_score += likes_bonus

        replies_bonus = min(replies_received * 0.1, 0.3)
        quality_score += replies_bonus

        # 上限 1.0
        quality_score = min(quality_score, 1.0)

        # 基础价值
        if activity_type == "post":
            base_value = self.base_values.get("botlearn_post", 15.0)
        else:
            base_value = self.base_values.get("botlearn_comment", 2.0)

        calculated_payment = self._apply_threshold(base_value, quality_score)

        logger.info(f"💬 BotLearn {activity_type} 评估: {activity_id}")
        logger.info(f"   质量: {quality_score:.2f}")
        logger.info(f"   报酬: ${calculated_payment:.2f}")

        return {
            "quality_score": quality_score,
            "calculated_payment": calculated_payment,
            "base_value": base_value,
            "activity_type": activity_type
        }

    def evaluate_research_task(
        self,
        task_id: str,
        research_hours: float,
        report_pages: int,
        citations: int,
        quality_self_assessment: float
    ) -> Dict[str, float]:
        """
        评估研究任务质量
        
        Args:
            task_id: 任务 ID
            research_hours: 研究时长（小时）
            report_pages: 报告页数
            citations: 引用数量
            quality_self_assessment: 自我评估（0-1）
            
        Returns:
            评估结果
        """
        # 质量评分
        quality_score = 0.0

        # 基础分 0.2
        quality_score += 0.2

        # 研究深度奖励
        if research_hours >= 2:
            quality_score += 0.1
            if research_hours >= 5:
                quality_score += 0.1

        # 报告质量奖励
        if report_pages >= 2:
            quality_score += 0.1
            if report_pages >= 5:
                quality_score += 0.1

        # 引用奖励
        if citations >= 3:
            quality_score += 0.1
            if citations >= 10:
                quality_score += 0.1

        # 自我评估权重 30%
        quality_score += quality_self_assessment * 0.3

        # 上限 1.0
        quality_score = min(quality_score, 1.0)

        base_value = self.base_values.get("crypto_research", 20.0)
        calculated_payment = self._apply_threshold(base_value, quality_score)

        logger.info(f"🔬 研究任务评估: {task_id}")
        logger.info(f"   质量: {quality_score:.2f}")
        logger.info(f"   报酬: ${calculated_payment:.2f}")

        return {
            "quality_score": quality_score,
            "calculated_payment": calculated_payment,
            "base_value": base_value
        }

    def _apply_threshold(self, base_value: float, quality_score: float) -> float:
        """
        应用质量阈值
        
        Args:
            base_value: 基础价值
            quality_score: 质量评分（0-1）
            
        Returns:
            实际报酬
        """
        if quality_score < self.min_threshold:
            return 0.0
        else:
            return base_value * quality_score

    def calculate_daily_payment(
        self,
        evaluations: List[Dict]
    ) -> Dict[str, float]:
        """
        计算每日总收入
        
        Args:
            evaluations: 评估结果列表
            
        Returns:
            汇总数据
        """
        total_payment = 0.0
        total_base = 0.0
        avg_quality = 0.0
        tasks_paid = 0
        tasks_rejected = 0

        for eval_result in evaluations:
            payment = eval_result.get("calculated_payment", 0.0)
            base = eval_result.get("base_value", 0.0)
            quality = eval_result.get("quality_score", 0.0)

            total_payment += payment
            total_base += base

            if payment > 0:
                tasks_paid += 1
            else:
                tasks_rejected += 1

        avg_quality = sum(e.get("quality_score", 0.0) for e in evaluations) / len(evaluations) if evaluations else 0.0

        return {
            "total_payment": total_payment,
            "total_base": total_base,
            "avg_quality": avg_quality,
            "tasks_total": len(evaluations),
            "tasks_paid": tasks_paid,
            "tasks_rejected": tasks_rejected,
            "acceptance_rate": tasks_paid / len(evaluations) if evaluations else 0.0
        }


if __name__ == "__main__":
    # 测试代码
    evaluator = TaskEvaluator()

    print("\n🧪 测试 Moltx Article 评估...")
    result = evaluator.evaluate_moltx_article(
        article_id="test-001",
        likes=8,
        comments=[{"agent_id": "agent1", "content": "Good!"}],
        shares=2
    )
    print(f"   结果: {json.dumps(result, indent=2)}")

    print("\n🧪 测试 BotLearn 评论评估...")
    result = evaluator.evaluate_botlearn_interaction(
        activity_type="comment",
        activity_id="comment-001",
        likes_received=3,
        replies_received=1,
        content_length=200
    )
    print(f"   结果: {json.dumps(result, indent=2)}")

    print("\n🧪 测试研究任务评估...")
    result = evaluator.evaluate_research_task(
        task_id="research-001",
        research_hours=3.5,
        report_pages=3,
        citations=5,
        quality_self_assessment=0.8
    )
    print(f"   结果: {json.dumps(result, indent=2)}")

    print("\n🧪 测试每日支付计算...")
    evaluations = [
        evaluator.evaluate_moltx_article("a1", likes=5, comments=[{"agent_id": "x"}]),
        evaluator.evaluate_botlearn_interaction("comment", "c1", likes_received=2, content_length=100),
        evaluator.evaluate_research_task("r1", research_hours=2, report_pages=2, citations=3, quality_self_assessment=0.7)
    ]
    summary = evaluator.calculate_daily_payment(evaluations)
    print(f"   摘要: {json.dumps(summary, indent=2)}")
