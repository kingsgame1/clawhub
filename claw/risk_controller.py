#!/usr/bin/env python3
"""
Risk Control System - 风险控制系统（ClawWork 适配）
破产保护、成本预警、应急模式
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskController:
    """
    风险控制器
        
    功能：
    - 破产保护机制
    - 成本预警
    - 自动紧急模式
    - 风险阈值管理
    """

    def __init__(
        self,
        bankruptcy_threshold: float = 0.0,
        warning_threshold: float = 5.0,
        safety_margin: float = 10.0,
        daily_cost_budget: float = 0.05
    ):
        """
        初始化
        
        Args:
            bankruptcy_threshold: 破产阈值
            warning_threshold: 警告阈值
            safety_margin: 安全边际
            daily_cost_budget: 每日成本预算（美元）
        """
        self.bankruptcy_threshold = bankruptcy_threshold
        self.warning_threshold = warning_threshold
        self.safety_margin = safety_margin
        self.daily_cost_budget = daily_cost_budget

        # 风险记录
        self.risk_alerts = []
        self.emergency_mode = False
        self.blocked_operations = []

    def assess_risk(
        self,
        balance: float,
        daily_cost: float,
        daily_income: float
    ) -> Dict:
        """
        评估当前风险
        
        Args:
            balance: 当前余额
            daily_cost: 今日成本
            daily_income: 今日收入
            
        Returns:
            风险评估结果
        """
        risk_level = "low"
        alerts = []
        actions = []

        # 检查破产
        if balance <= self.bankruptcy_threshold:
            risk_level = "critical"
            alerts.append({
                "type": "bankruptcy",
                "severity": "critical",
                "message": f"⚠️ 破产预警：余额 {balance:.2f} <= {self.bankruptcy_threshold}",
                "action": "EMERGENCY_MODE",
                "timestamp": datetime.now().isoformat()
            })
            actions.append("activate_emergency_mode")
            self.emergency_mode = True

        # 检查警告
        elif balance < self.warning_threshold:
            risk_level = "high"
            alerts.append({
                "type": "low_balance",
                "severity": "high",
                "message": f"⚠️ 资金告急：余额 {balance:.2f} < {self.warning_threshold}",
                "action": "PRIORITIZE_WORK",
                "timestamp": datetime.now().isoformat()
            })
            actions.append("prioritize_high_pay_tasks")

        # 检查日成本
        cost_ratio = daily_cost / daily_income if daily_income > 0 else 1.0
        if cost_ratio > 0.8:
            alert_severity = "high" if cost_ratio > 1.0 else "medium"
            alerts.append({
                "type": "high_cost",
                "severity": alert_severity,
                "message": f"⚠️ 成本过高：今日成本 {daily_cost:.4f} 是收入的 {cost_ratio:.1%}",
                "action": "REDUCE_COSTS",
                "timestamp": datetime.now().isoformat()
            })
            actions.append("reduce_token_usage")

        # 检查成本超预算
        if daily_cost > self.daily_cost_budget:
            alerts.append({
                "type": "budget_exceeded",
                "severity": "high",
                "message": f"⚠️ 预算超支：今日成本 {daily_cost:.4f} > 预算 {self.daily_cost_budget:.4f}",
                "action": "STOP_EXPENSIVE_OPERATIONS",
                "timestamp": datetime.now().isoformat()
            })
            actions.append("block_expensive_tasks")
            self.blocked_operations.append("high_llm_usage")

        # 记录警报
        self.risk_alerts.extend(alerts)

        return {
            "risk_level": risk_level,
            "balance": balance,
            "cost_ratio": cost_ratio if daily_income > 0 else 1.0,
            "alerts": alerts,
            "recommended_actions": actions,
            "emergency_mode": self.emergency_mode
        }

    def should_allow_operation(
        self,
        operation: str,
        estimated_cost: float,
        balance: float
    ) -> Dict:
        """
        判断是否允许执行操作
        
        Args:
            operation: 操作类型（e.g., "llm_call", "api_request"）
            estimated_cost: 预估成本
            balance: 当前余额
            
        Returns:
            允许结果
        """
        # 紧急模式只允许高价值工作
        if self.emergency_mode:
            if operation not in ["moltx_article", "botlearn_post"]:
                return {
                    "allowed": False,
                    "reason": "紧急模式：只允许高价值工作",
                    "emergency_active": True
                }

        # 成本检查
        if balance - estimated_cost < self.bankruptcy_threshold:
            return {
                "allowed": False,
                "reason": f"操作后余额会破产：{balance:.2f} - {estimated_cost:.4f} < {self.bankruptcy_threshold}",
                "blocked_by": "balance_check"
            }

        # 阻止操作列表
        if operation in self.blocked_operations:
            return {
                "allowed": False,
                "reason": f"操作已被阻止：{operation}",
                "blocked_by": "risk_control"
            }

        # 允许
        return {
            "allowed": True,
            "reason": "操作允许",
            "estimated_remaining": balance - estimated_cost
        }

    def activate_emergency_mode(self) -> None:
        """激活紧急模式"""
        self.emergency_mode = True
        logger.warning("🚨 紧急模式已激活")
        logger.warning("   - 只允许高价值工作（moltx_article, botlearn_post）")
        logger.warning("   - 暂停所有学习任务")
        logger.warning("   - 最小化 LLM 使用")

    def deactivate_emergency_mode(self) -> None:
        """解除紧急模式"""
        self.emergency_mode = False
        logger.info("✅ 紧急模式已解除")

    def block_operation(self, operation: str, reason: str = "") -> None:
        """
        阻止操作
        
        Args:
            operation: 操作类型
            reason: 原因
        """
        self.blocked_operations.append(operation)
        logger.warning(f"🚫 已阻止操作: {operation} ({reason})")

    def unblock_operation(self, operation: str) -> None:
        """
        解除阻止
        
        Args:
            operation: 操作类型
        """
        if operation in self.blocked_operations:
            self.blocked_operations.remove(operation)
            logger.info(f"✅ 已解除阻止: {operation}")

    def get_risk_summary(self) -> Dict:
        """
        获取风险摘要
        
        Returns:
            摘要信息
        """
        # 统计警报
        alert_counts = {}
        for alert in self.risk_alerts:
            alert_type = alert["type"]
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1

        # 最新警报
        recent_alerts = self.risk_alerts[-5:] if self.risk_alerts else []

        return {
            "emergency_mode": self.emergency_mode,
            "blocked_operations": self.blocked_operations,
            "total_alerts": len(self.risk_alerts),
            "alert_counts": alert_counts,
            "recent_alerts": recent_alerts
        }

    def generate_risk_report(self) -> str:
        """
        生成风险报告
        
        Returns:
            Markdown 报告
        """
        summary = self.get_risk_summary()

        report = "# 🛡️ 风险控制报告\n\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## 系统状态\n\n"
        report += f"- 紧急模式: {'🚨 激活' if summary['emergency_mode'] else '✅ 未激活'}\n"
        report += f"- 阻止的操作: {', '.join(summary['blocked_operations']) or '无'}\n"
        report += f"- 总警报数: {summary['total_alerts']}\n\n"

        if summary['alert_counts']:
            report += "## 警报统计\n\n"
            for alert_type, count in summary['alert_counts'].items():
                report += f"- {alert_type}: {count} 次\n"
            report += "\n"

        if summary['recent_alerts']:
            report += "## 最近警报\n\n"
            for alert in reversed(summary['recent_alerts']):
                severity_icon = "🔴" if alert["severity"] == "critical" else "🟠" if alert["severity"] == "high" else "🟡"
                report += f"{severity_icon} **{alert['type']}** ({alert.get('timestamp', '')[:16]})\n"
                report += f"   {alert['message']}\n"
                report += f"   行动: {alert['action']}\n\n"

        return report


class RiskEngine:
    """
    风险引擎 - 整合风险控制
        
    功能：
    - 协调 RiskController
    - 执行风险检查
    - 生成风险报告
    """

    def __init__(self, controller: Optional[RiskController] = None):
        """
        初始化
        
        Args:
            controller: RiskController 实例
        """
        self.controller = controller or RiskController()

    def check_and_alert(
        self,
        balance: float,
        daily_cost: float,
        daily_income: float
    ) -> Dict:
        """
        检查并警告风险
        
        Args:
            balance: 当前余额
            daily_cost: 今日成本
            daily_income: 今日收入
            
        Returns:
            风险评估结果
        """
        result = self.controller.assess_risk(
            balance=balance,
            daily_cost=daily_cost,
            daily_income=daily_income
        )

        # 如果有紧急情况，发送警告
        if result["risk_level"] == "critical":
            logger.error("🚨 CRITICAL RISK DETECTED!")
            for alert in result["alerts"]:
                logger.error(f"   {alert['message']}")

        return result

    def authorize_operation(
        self,
        operation: str,
        estimated_cost: float,
        balance: float
    ) -> bool:
        """
        授权操作
        
        Args:
            operation: 操作类型
            estimated_cost: 预估成本
            balance: 当前余额
            
        Returns:
            是否允许
        """
        result = self.controller.should_allow_operation(
            operation=operation,
            estimated_cost=estimated_cost,
            balance=balance
        )

        if not result["allowed"]:
            logger.warning(f"🚫 操作被阻止: {operation}")
            logger.warning(f"   原因: {result['reason']}")

        return result["allowed"]


# 全局实例
_risk_controller = RiskController()
_risk_engine = RiskEngine(_risk_controller)


def get_risk_controller() -> RiskController:
    """获取全局风险控制器"""
    return _risk_controller


def get_risk_engine() -> RiskEngine:
    """获取全局风险引擎"""
    return _risk_engine


if __name__ == "__main__":
    # 测试代码
    print("\n🧪 测试风险控制系统...")

    controller = RiskController()

    print("\n📊 测试风险评估...")
    result = controller.assess_risk(
        balance=3.0,
        daily_cost=0.03,
        daily_income=0.05
    )
    print(f"   风险等级: {result['risk_level']}")
    print(f"   警报数量: {len(result['alerts'])}")
    print(f"   推荐行动: {', '.join(result['recommended_actions'])}")

    print("\n🔐 测试操作授权...")
    # 紧急模式下
    controller.activate_emergency_mode()

    auth1 = controller.should_allow_operation(
        operation="moltx_article",
        estimated_cost=0.01,
        balance=5.0
    )
    print(f"   Moltx Article: {'✅ 允许' if auth1['allowed'] else '🚫 拒绝'} ({auth1.get('reason', '')})")

    auth2 = controller.should_allow_operation(
        operation="learning_task",
        estimated_cost=0.01,
        balance=5.0
    )
    print(f"   Learning Task: {'✅ 允许' if auth2['allowed'] else '🚫 拒绝'} ({auth2.get('reason', '')})")

    print("\n📄 生成风险报告...")
    report = controller.generate_risk_report()
    print(report)
