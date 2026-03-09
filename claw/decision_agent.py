"""
Decision Agent - 决策代理（ClawWork 适配）
根据经济状态自动决定工作 vs 学习
"""

import json
import logging
import random
from typing import Dict, Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionAgent:
    """
    ClawMode 决策代理
        
    功能：
    - 分析当前经济状态
    - 决定今日活动（工作 vs 学习）
    - 生成决策理由
    - 考虑生存风险
    """

    def __init__(
        self,
        balance: float = 10.0,
        threshold_struggling: float = 100.0,
        threshold_stable: float = 500.0,
        conservative_mode: bool = False
    ):
        """
        初始化决策代理
        
        Args:
            balance: 当前余额
            threshold_struggling: 挣扎状态阈值
            threshold_stable: 稳定状态阈值
            conservative_mode: 保守模式（更倾向于工作）
        """
        self.balance = balance
        self.threshold_struggling = threshold_struggling
        self.threshold_stable = threshold_stable
        self.conservative_mode = conservative_mode

    def analyze_status(self) -> Dict:
        """
        分析当前经济状态
        
        Returns:
            状态分析结果
        """
        if self.balance <= 0:
            status = "bankrupt"
        elif self.balance < self.threshold_struggling:
            status = "struggling"
        elif self.balance < self.threshold_stable:
            status = "stable"
        else:
            status = "thriving"

        # 计算安全边际
        if status == "bankrupt":
            safety_margin = -self.balance
        elif status == "struggling":
            safety_margin = self.balance / self.threshold_struggling - 1
        elif status == "stable":
            safety_margin = self.balance / self.threshold_stable - 1
        else:  # thriving
            safety_margin = (self.balance - self.threshold_stable) / self.threshold_stable

        return {
            "status": status,
            "balance": self.balance,
            "safety_margin": safety_margin,
            "recommendation": self._get_recommendation(status)
        }

    def _get_recommendation(self, status: str) -> str:
        """获取状态建议"""
        recommendations = {
            "bankrupt": "紧急：需要立即工作，任何任务都可以",
            "struggling": "优先工作，减少学习投资，聚焦高回报任务",
            "stable": "平衡工作与学习，可适当投资知识",
            "thriving": "优先学习，提升长期能力，工作保持基本"
        }
        return recommendations.get(status, "未知状态")

    def decide_activity(
        self,
        balance: Optional[float] = None,
        recent_income: float = 0.0,
        recent_cost: float = 0.0
    ) -> Dict:
        """
        决定今日活动
        
        Args:
            balance: 当前余额（覆盖初始化值）
            recent_income: 最近收入
            recent_cost: 最近成本
            
        Returns:
            决策结果
        """
        if balance is not None:
            self.balance = balance

        # 分析状态
        status_info = self.analyze_status()
        status = status_info["status"]

        # 决策逻辑
        activity = None
        reasoning = ""
        priority_tasks = []

        # 基础决策
        if status == "bankrupt":
            # 破产：全力工作
            activity = "work"
            reasoning = "紧急状态：资金为负，需要立即增加收入"
            priority_tasks = ["highest_pay_task"]
            
        elif status == "struggling":
            # 挣扎：80% 工作，20% 学习
            if self.balance < self.threshold_struggling * 0.5:
                # 资金极度紧张
                activity = "work"
                reasoning = "资金告急（${:.2f}），优先确保收入".format(self.balance)
                priority_tasks = ["moltx_article", "botlearn_post"]
            else:
                # 适度紧张
                if self.conservative_mode or random.random() < 0.8:
                    activity = "work"
                    reasoning = "挣扎状态（${:.2f}），优先工作积累资金".format(self.balance)
                    priority_tasks = ["botlearn_comment", "moltx_article"]
                else:
                    activity = "learn"
                    reasoning = "学习可以提升未来工作质量"
                    priority_tasks = ["crypto_arbitrage", "options_trading"]
                    
        elif status == "stable":
            # 稳定：50% 工作，50% 学习
            if self.conservative_mode or random.random() < 0.5:
                activity = "work"
                reasoning = "稳定状态，保持工作节奏"
                priority_tasks = ["moltx_article", "crypto_research"]
            else:
                activity = "learn"
                reasoning = "稳定状态，投资知识复利"
                priority_tasks = ["skill_from_masters", "defi_strategies"]
                
        else:  # thriving
            # 繁荣：30% 工作，70% 学习
            if self.conservative_mode or random.random() < 0.3:
                activity = "work"
                reasoning = "繁荣状态维持基本工作"
                priority_tasks = ["botlearn_comment", "research"]
            else:
                activity = "learn"
                reasoning = "盈余充足，专注提升长期能力"
                priority_tasks = ["options_trading", "crypto_arbitrage", "strategy_optimization"]

        # 考虑最近收支趋势
        if recent_income > recent_cost * 2:
            # 收入良好，可以多学习
            if activity == "work":
                probability_shift = 0.3
            else:
                probability_shift = 0.0
        elif recent_cost > recent_income * 2:
            # 成本过高，需要多工作
            if activity == "learn":
                probability_shift = -0.3
            else:
                probability_shift = 0.1
        else:
            probability_shift = 0.0

        # 构建决策结果
        decision = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "reasoning": reasoning,
            "priority_tasks": priority_tasks,
            "status_analysis": status_info,
            "trend_adjustment": probability_shift
        }

        logger.info(f"🎯 决策结果: {activity.upper()}")
        logger.info(f"   原因: {reasoning}")
        logger.info(f"   优先级: {', '.join(priority_tasks)}")
        logger.info(f"   状态: {status} (${self.balance:.2f})")

        return decision

    def get_learning_topics(self, activity: str) -> List[str]:
        """
        获取推荐学习主题
        
        Args:
            activity: 当前活动（仅在学习时使用）
            
        Returns:
            学习主题列表
        """
        learning_topics = {
            "immediate": [
                "crypto_arbitrage_basics",
                "defi_yield_farming",
                "options_basic_concepts"
            ],
            "intermediate": [
                "technical_analysis",
                "funding_rate_arbitrage",
                "options_strategies"
            ],
            "advanced": [
                "market_making",
                "derivatives_pricing",
                "ai_trading_systems"
            ]
        }
        
        # 根据余额确定学习深度
        if self.balance < self.threshold_struggling:
            return learning_topics["immediate"]
        elif self.balance < self.threshold_stable:
            return learning_topics["intermediate"]
        else:
            return learning_topics["advanced"]

    def should_work(self, balance: Optional[float] = None) -> bool:
        """
        快速判断是否应该工作
        
        Args:
            balance: 当前余额
            
        Returns:
            是否应该工作
        """
        if balance is not None:
            self.balance = balance
            
        status = self.analyze_status()["status"]
        
        # 破产和挣扎状态应该工作
        if status in ["bankrupt", "struggling"]:
            return True
        # 稳定状态 50% 概率工作
        elif status == "stable":
            return random.random() < 0.5
        # 繁荣状态 30% 概率工作
        else:  # thriving
            return random.random() < 0.3

    def get_work_capacity(self, balance: Optional[float] = None) -> int:
        """
        获取今日可工作数量
        
        Args:
            balance: 当前余额
            
        Returns:
            建议工作数量
        """
        if balance is not None:
            self.balance = balance
            
        status = self.analyze_status()["status"]
        
        if status == "bankrupt":
            return 5  # 全力工作
        elif status == "struggling":
            return 3  # 高强度工作
        elif status == "stable":
            return 2  # 正常工作
        else:  # thriving
            return 1  # 轻量工作


class DecisionEngine:
    """
    决策引擎 - 整合所有决策逻辑
        
    功能：
    - 协调 DecisionAgent
    - 执行决策
    - 记录决策历史
    - 生成决策建议
    """

    def __init__(self, tracker=None):
        """
        初始化
        
        Args:
            tracker: EconomicTracker 实例
        """
        self.agent = DecisionAgent()
        self.tracker = tracker
        self.decision_history = []

    def make_daily_decision(self) -> Dict:
        """
        做出每日决策
        
        Returns:
            完整决策结果
        """
        # 获取当前余额
        balance = self.tracker.get_balance() if self.tracker else 10.0
        
        # 计算最近趋势
        recent_income = 0.0
        recent_cost = 0.0
        if self.tracker:
            summary = self.tracker.get_summary()
            recent_cost = summary.get("daily_cost", 0.0)
            recent_income = summary.get("total_income", 0.0) - summary.get("total_token_cost", 0.0)

        # 决策
        decision = self.agent.decide_activity(
            balance=balance,
            recent_income=recent_income,
            recent_cost=recent_cost
        )

        # 记录历史
        self.decision_history.append(decision)

        return decision

    def get_decision_summary(self) -> Dict:
        """
        获取决策摘要
        
        Returns:
            摘要信息
        """
        if not self.decision_history:
            return {"error": "No decisions made yet"}

        work_count = sum(1 for d in self.decision_history if d["activity"] == "work")
        learn_count = sum(1 for d in self.decision_history if d["activity"] == "learn")

        return {
            "total_decisions": len(self.decision_history),
            "work_count": work_count,
            "learn_count": learn_count,
            "work_ratio": work_count / len(self.decision_history),
            "recent_activity": self.decision_history[-1]["activity"],
            "recommended_topics": self.agent.get_learning_topics(
                self.decision_history[-1]["activity"]
            )
        }


if __name__ == "__main__":
    # 测试代码
    print("\n🧪 测试 Decision Agent...")
    
    agent = DecisionAgent()
    
    # 测试不同余额状态
    test_balances = [0, 50, 250, 600]
    
    for balance in test_balances:
        agent.balance = balance
        print(f"\n💰 余额: ${balance:.2f}")
        
        status = agent.analyze_status()
        print(f"   状态: {status['status']}")
        print(f"   建议: {status['recommendation']}")
        
        decision = agent.decide_activity(balance=balance)
        print(f"   决策: {decision['activity'].upper()}")
        print(f"   原因: {decision['reasoning']}")
    
    # 测试决策引擎
    print("\n🧪 测试 Decision Engine...")
    
    from economic_tracker import EconomicTracker
    tracker = EconomicTracker(initial_balance=10.0)
    tracker.initialize()
    tracker.add_income(5.0, "test", 0.8)
    
    engine = DecisionEngine(tracker=tracker)
    decision = engine.make_daily_decision()
    
    print(f"\n📊 决策摘要:")
    summary = engine.get_decision_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
