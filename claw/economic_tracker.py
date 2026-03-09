"""
Economic Tracker - 轻量级经济追踪系统（ClawWork 适配）
追踪 Agent 的经济状态：余额、成本、收入、生存状态
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class EconomicTracker:
    """
    简化版经济追踪器
        
    功能：
    - 追踪 LLM Token 成本
    - 追踪 API 调用成本
    - 记录收入来源（Moltx、BotLearn 等）
    - 计算生存状态（Thriving/Stable/Struggling/Bankrupt）
    - 保存到 JSONL 文件
    """

    def __init__(
        self,
        signature: str = "silvermoon",
        initial_balance: float = 10.0,
        input_token_price: float = 2.5,   # $2.5 per 1M tokens
        output_token_price: float = 10.0,  # $10 per 1M tokens
        data_path: Optional[str] = None,
        min_evaluation_threshold: float = 0.6
    ):
        """
        初始化经济追踪器
        
        Args:
            signature: Agent 签名/名称
            initial_balance: 初始余额（美元）
            input_token_price: 输入 token 价格（每百万）
            output_token_price: 输出 token 价格（每百万）
            data_path: 数据存储路径
            min_evaluation_threshold: 质量评估阈值（默认 0.6）
        """
        self.signature = signature
        self.initial_balance = initial_balance
        self.input_token_price = input_token_price
        self.output_token_price = output_token_price
        self.min_evaluation_threshold = min_evaluation_threshold

        # 设置数据路径
        if data_path:
            self.data_path = data_path
        else:
            self.data_path = "/root/.openclaw/workspace/data/economic"

        self.balance_file = os.path.join(self.data_path, "balance.jsonl")
        self.token_costs_file = os.path.join(self.data_path, "costs.jsonl")
        self.income_file = os.path.join(self.data_path, "income.jsonl")

        # 确保目录存在
        os.makedirs(self.data_path, exist_ok=True)

        # 当前状态
        self.current_balance = initial_balance
        self.total_token_cost = 0.0
        self.total_income = 0.0
        self.session_cost = 0.0
        self.daily_cost = 0.0

        # 任务追踪
        self.current_task_id: Optional[str] = None
        self.task_costs: Dict[str, float] = {
            "llm_tokens": 0.0,
            "api_search": 0.0,
            "moltx_api": 0.0,
            "botlearn_api": 0.0
        }

    def initialize(self) -> None:
        """初始化追踪器：加载现有状态或创建新状态"""
        if os.path.exists(self.balance_file):
            self._load_latest_state()
            print(f"📊 已加载 {self.signature} 的经济状态")
            print(f"   余额: ${self.current_balance:.2f}")
            print(f"   总成本: ${self.total_token_cost:.4f}")
        else:
            self._save_balance_record(
                date="initialization",
                balance=self.initial_balance,
                cost_delta=0.0,
                income_delta=0.0
            )
            print(f"✅ 已初始化 {self.signature} 的经济追踪器")
            print(f"   初始余额: ${self.initial_balance:.2f}")

    def _load_latest_state(self) -> None:
        """从文件加载最新经济状态"""
        with open(self.balance_file, "r") as f:
            lines = f.readlines()
            if lines:
                record = json.loads(lines[-1])  # 最后一行
                self.current_balance = record["balance"]
                self.total_token_cost = record["total_token_cost"]
                self.total_income = record["total_income"]

    def _save_balance_record(
        self,
        date: str,
        balance: float,
        cost_delta: float,
        income_delta: float,
        description: str = ""
    ) -> None:
        """保存余额记录到文件"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "date": date,
            "balance": balance,
            "cost_delta": cost_delta,
            "income_delta": income_delta,
            "total_token_cost": self.total_token_cost,
            "total_income": self.total_income,
            "survival_status": self.get_survival_status(),
            "description": description
        }

        with open(self.balance_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def track_llm_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        session_id: Optional[str] = None
    ) -> float:
        """
        追踪 LLM Token 使用成本
        
        Args:
            input_tokens: 输入 token 数量
            output_tokens: 输出 token 数量
            session_id: 会话 ID（可选）
            
        Returns:
            该次调用的成本（美元）
        """
        input_cost = (input_tokens / 1_000_000.0) * self.input_token_price
        output_cost = (output_tokens / 1_000_000.0) * self.output_token_price
        total_cost = input_cost + output_cost

        # 更新追踪状态
        self.current_balance -= total_cost
        self.total_token_cost += total_cost
        self.session_cost += total_cost
        self.daily_cost += total_cost
        self.task_costs["llm_tokens"] += total_cost

        # 记录到数据文件
        cost_record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "llm_cost",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "session_id": session_id,
            "task_id": self.current_task_id,
            "balance_after": self.current_balance
        }

        with open(self.token_costs_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(cost_record) + "\n")

        return total_cost

    def track_api_cost(
        self,
        cost: float,
        api_name: str,
        api_type: str = "other",
        session_id: Optional[str] = None
    ) -> float:
        """
        追踪 API 调用成本
        
        Args:
            cost: 成本（美元）
            api_name: API 名称
            api_type: API 类型 (search/moltx/botlearn/other)
            session_id: 会话 ID（可选）
            
        Returns:
            该次调用的成本
        """
        # 更新追踪状态
        self.current_balance -= cost
        self.total_token_cost += cost
        self.session_cost += cost
        self.daily_cost += cost
        
        # 记录到对应类型
        if api_type in self.task_costs:
            self.task_costs[api_type] += cost
        else:
            self.task_costs["other"] = self.task_costs.get("other", 0.0) + cost

        # 记录到数据文件
        cost_record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "api_cost",
            "api_name": api_name,
            "api_type": api_type,
            "cost": cost,
            "session_id": session_id,
            "task_id": self.current_task_id,
            "balance_after": self.current_balance
        }

        with open(self.token_costs_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(cost_record) + "\n")

        return cost

    def add_income(
        self,
        amount: float,
        source: str,
        quality_score: float = 1.0,
        description: str = ""
    ) -> float:
        """
        添加收入
        
        Args:
            amount: 收入金额
            source: 收入来源 (moltx/botlearn/trading/other)
            quality_score: 质量评分（0-1，影响实际支付）
            description: 描述
            
        Returns:
            实际收到的金额（低于阈值则返回 0）
        """
        # 应用质量阈值
        if quality_score < self.min_evaluation_threshold:
            actual_payment = 0.0
            print(f"⚠️  质量低于阈值（{quality_score:.2f} < {self.min_evaluation_threshold:.2f}）")
            print(f"   未支付: {source}")
        else:
            actual_payment = amount * quality_score
            self.current_balance += actual_payment
            self.total_income += actual_payment
            print(f"💰 收入: +${actual_payment:.2f}（来源: {source}, 评分: {quality_score:.2f}）")
            print(f"   当前余额: ${self.current_balance:.2f}")

        # 记录到数据文件
        income_record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": source,
            "amount": amount,
            "quality_score": quality_score,
            "actual_payment": actual_payment,
            "description": description,
            "balance_after": self.current_balance
        }

        with open(self.income_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(income_record) + "\n")

        return actual_payment

    def get_survival_status(self) -> str:
        """
        获取生存状态
        
        Returns:
            生存状态: "thriving", "stable", "struggling", "bankrupt"
        """
        if self.current_balance <= 0:
            return "bankrupt"
        elif self.current_balance < 100:
            return "struggling"
        elif self.current_balance < 500:
            return "stable"
        else:
            return "thriving"

    def get_balance(self) -> float:
        """获取当前余额"""
        return self.current_balance

    def get_summary(self) -> Dict:
        """获取经济摘要"""
        return {
            "signature": self.signature,
            "balance": self.current_balance,
            "total_token_cost": self.total_token_cost,
            "total_income": self.total_income,
            "session_cost": self.session_cost,
            "daily_cost": self.daily_cost,
            "net_profit": self.total_income - self.total_token_cost,
            "survival_status": self.get_survival_status()
        }

    def reset_session(self) -> None:
        """重置会话追踪"""
        self.session_cost = 0.0

    def save_daily_state(self, date: Optional[str] = None) -> None:
        """
        保存每日状态
        
        Args:
            date: 日期（YYYY-MM-DD），默认为今天
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        self._save_balance_record(
            date=date,
            balance=self.current_balance,
            cost_delta=self.daily_cost,
            income_delta=0.0 if not hasattr(self, '_daily_income') else self._daily_income,
            description="daily_state"
        )

        # 重置每日追踪
        self.daily_cost = 0.0
        self.session_cost = 0.0

        print(f"💾 已保存 {date} 的每日状态")
        print(f"   余额: ${self.current_balance:.2f}")
        print(f"   状态: {self.get_survival_status()}")

    def generate_daily_report(self, date: Optional[str] = None) -> str:
        """
        生成每日报告（Markdown 格式）
        
        Args:
            date: 日期（YYYY-MM-DD），默认为今天
            
        Returns:
            Markdown 格式的报告
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # 读取当日数据
        daily_costs = self._get_daily_costs(date)
        daily_income = self._get_daily_income(date)

        report = f"""
# 📊 银月经济日报 - {date}

## 💰 资金状态
- 当前余额: **${self.current_balance:.2f}**
- 生存状态: **{self.get_survival_status().upper()}**
- 总成本累计: **${self.total_token_cost:.4f}**
- 总收入累计: **${self.total_income:.2f}**
- 净利润: **${self.total_income - self.total_token_cost:.2f}**

## 💸 今日成本
- LLM Tokens: **${daily_costs.get('llm_tokens', 0.0):.4f}**
- API 调用: **${daily_costs.get('api', 0.0):.4f}**
- **总计: ${sum(daily_costs.values()):.4f}**

## 💰 今日收入
| 来源 | 金额 | 评分 |
|------|------|------|
"""
        for income in daily_income:
            report += f"| {income['source']} | ${income['actual_payment']:.2f} | {income['quality_score']:.2f} |\n"

        total_daily_income = sum(i['actual_payment'] for i in daily_income)
        report += f"| **总计** | **${total_daily_income:.2f}** | - |\n"

        # 生存状态建议
        status = self.get_survival_status()
        if status == "bankrupt":
            status_hint = "⚠️ **紧急状态**: 需要立即增加收入来源"
        elif status == "struggling":
            status_hint = "📉 **挣扎状态**: 优先工作，减少学习投资"
        elif status == "stable":
            status_hint = "📊 **稳定状态**: 保持工作/学习平衡"
        else:  # thriving
            status_hint = "🚀 **繁荣状态**: 优先学习，提升长期能力"

        report += f"""
## 🚀 状态建议
{status_hint}

## 📊 费用占比
- LLM Tokens: {daily_costs.get('llm_tokens', 0.0) / sum(daily_costs.values()) * 100:.1f}%
- API Calls: {daily_costs.get('api', 0.0) / sum(daily_costs.values()) * 100:.1f}%

---
*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return report

    def _get_daily_costs(self, date: str) -> Dict[str, float]:
        """获取指定日期的成本"""
        daily_costs = {"llm_tokens": 0.0, "api": 0.0}

        if not os.path.exists(self.token_costs_file):
            return daily_costs

        with open(self.token_costs_file, "r") as f:
            for line in f:
                record = json.loads(line)
                if record.get("date") == date:
                    if record["type"] == "llm_cost":
                        daily_costs["llm_tokens"] += record["total_cost"]
                    elif record["type"] == "api_cost":
                        daily_costs["api"] += record["cost"]

        return daily_costs

    def _get_daily_income(self, date: str) -> List[Dict]:
        """获取指定日期的收入"""
        daily_income = []

        if not os.path.exists(self.income_file):
            return daily_income

        with open(self.income_file, "r") as f:
            for line in f:
                record = json.loads(line)
                if record.get("date") == date:
                    daily_income.append(record)

        return daily_income

    def generate_cost_footer(self) -> str:
        """
        生成成本 footer（附在消息末尾）
        
        Returns:
            成本信息字符串
        """
        return (
            f"\n\n---\n"
            f"💰 Cost: ${self.session_cost:.4f} | "
            f"Balance: ${self.current_balance:.2f} | "
            f"Status: {self.get_survival_status()}"
        )


if __name__ == "__main__":
    # 测试代码
    tracker = EconomicTracker(initial_balance=10.0)
    tracker.initialize()

    print("\n🧪 测试追踪 LLM 成本...")
    cost = tracker.track_llm_cost(input_tokens=5000, output_tokens=1000)
    print(f"   调用成本: ${cost:.6f}")

    print("\n🧪 测试追踪 API 成本...")
    cost = tracker.track_api_cost(cost=0.0016, api_name="Tavily Search", api_type="search")
    print(f"   调用成本: ${cost:.6f}")

    print("\n🧪 测试添加收入...")
    payment = tracker.add_income(amount=10.0, source="moltx", quality_score=0.8)
    print(f"   实际收到: ${payment:.2f}")

    print("\n📊 摘要:")
    summary = tracker.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    print("\n📄 每日报告:")
    print(tracker.generate_daily_report())
