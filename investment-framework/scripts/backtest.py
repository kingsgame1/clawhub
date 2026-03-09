#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资策略回测引擎
使用 CoinGecko 历史数据验证策略有效性
"""

import json
import requests
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class BacktestEngine:
    """回测引擎"""

    def __init__(self, api_base="https://api.coingecko.com/api/v3"):
        self.api_base = api_base
        self.request_interval = 7  # 秒，避免 API 限制

    def get_historical_data(self, coin_id: str, days: int = 90) -> List[Tuple]:
        """
        获取历史价格数据
        返回: [(timestamp, price), ...]
        """
        print(f"📥 获取 {coin_id} 过去 {days} 天的历史数据...")

        url = f"{self.api_base}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            prices = data.get("prices", [])
            result = [(datetime.fromtimestamp(ts/1000), price) for ts, price in prices]
            print(f"✅ 获取到 {len(result)} 条价格数据")

            return result
        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
            return []

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算 RSI 指标"""
        if len(prices) < period + 1:
            return 50.0

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_signals(
        self,
        current_price: float,
        price_change_24h: float,
        rsi: float,
        fear_greed: int
    ) -> Tuple[int, str]:
        """
        计算交易信号
        返回: (score, signal)
        """
        score = 50
        signals = []
        signal = "HODL"

        # RSI 信号
        if rsi <= 30:
            score += 15
            signals.append(f"RSI超卖: {rsi:.2f}")
            signal = "BUY"
        elif rsi >= 70:
            score -= 15
            signals.append(f"RSI超买: {rsi:.2f}")
            signal = "SELL"

        # 价格变化信号
        if price_change_24h <= -10:
            score += 10
            signals.append(f"暴跌: {price_change_24h:.1f}%")
            if signal == "HODL":
                signal = "BUY"
        elif price_change_24h >= 10:
            score -= 10
            signals.append(f"暴涨: {price_change_24h:.1f}%")
            if signal == "HODL":
                signal = "SELL"

        # 恐慌贪婪信号
        if fear_greed <= 20:
            score += 20
            signals.append(f"极度恐慌: {fear_greed}")
            if signal != "SELL":
                signal = "BUY"
        elif fear_greed >= 80:
            score -= 20
            signals.append(f"极度贪婪: {fear_greed}")
            if signal != "BUY":
                signal = "SELL"

        score = max(0, min(100, score))

        return score, signal

    def run_backtest(
        self,
        coin_id: str,
        initial_capital: float = 10000,
        buy_score_threshold: int = 60,
        sell_score_threshold: int = 40,
        lookback_days: int = 90
    ) -> Dict:
        """
        运行策略回测

        参数:
            coin_id: 加密货币 ID (如 "bitcoin")
            initial_capital: 初始资金 (USD)
            buy_score_threshold: 买入分数阈值
            sell_score_threshold: 卖出分数阈值
            lookback_days: 回测天数
        """
        print("\n" + "="*60)
        print(f"🧪 开始回测: {coin_id}")
        print(f"   初始资金: ${initial_capital}")
        print(f"   买入阈值: {buy_score_threshold}")
        print(f"   卖出阈值: {sell_score_threshold}")
        print(f"   回测天数: {lookback_days}")
        print("="*60)

        # 获取历史数据
        historical = self.get_historical_data(coin_id, lookback_days)
        if not historical:
            return {"error": "无法获取历史数据"}

        prices = [price for _, price in historical]
        timestamps = [ts for ts, _ in historical]

        # 回测状态
        capital = initial_capital
        holdings = 0.0
        buy_count = 0
        sell_count = 0
        trades = []

        print("\n📊 开始模拟交易...")

        for i in range(14, len(prices)):  # 需要至少14天数据计算 RSI
            current_price = prices[i]
            prev_price = prices[i-1]
            price_change_24h = ((current_price - prev_price) / prev_price) * 100

            # 计算 RSI
            rsi = self.calculate_rsi(prices[:i+1], 14)

            # 模拟恐慌贪婪指数（基于价格变化）
            fear_greed = 50
            if price_change_24h < -5:
                fear_greed = 25
            elif price_change_24h > 5:
                fear_greed = 75

            # 计算信号
            score, signal = self.calculate_signals(
                current_price,
                price_change_24h,
                rsi,
                fear_greed
            )

            # 交易逻辑
            if signal == "BUY" and score >= buy_score_threshold and capital > 0:
                # 买入
                buy_amount = capital * 0.5  # 使用 50% 资金
                holdings += buy_amount / current_price
                capital -= buy_amount
                buy_count += 1
                trades.append({
                    "date": timestamps[i].strftime("%Y-%m-%d"),
                    "action": "BUY",
                    "price": current_price,
                    "score": score,
                    "rsi": rsi,
                    "amount": buy_amount
                })
                print(f"   {timestamps[i].strftime('%Y-%m-%d')} | BUY @ ${current_price:.2f} | 评分: {score}")

            elif signal == "SELL" and score <= sell_score_threshold and holdings > 0:
                # 卖出
                sell_value = holdings * current_price
                capital += sell_value
                holdings = 0.0
                sell_count += 1
                trades.append({
                    "date": timestamps[i].strftime("%Y-%m-%d"),
                    "action": "SELL",
                    "price": current_price,
                    "score": score,
                    "rsi": rsi,
                    "value": sell_value
                })
                print(f"   {timestamps[i].strftime('%Y-%m-%d')} | SELL @ ${current_price:.2f} | 评分: {score}")

            # 请求间隔
            # sleep(self.request_interval)  # 注释掉以加快回测速度

        # 计算最终价值
        final_value = capital + (holdings * prices[-1])
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        buy_hold_return = ((prices[-1] - prices[15]) / prices[15]) * 100

        # 生成报告
        report = {
            "coin_id": coin_id,
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "buy_hold_return": buy_hold_return,
            "returns_diff": total_return - buy_hold_return,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "total_trades": buy_count + sell_count,
            "start_date": timestamps[15].strftime("%Y-%m-%d"),
            "end_date": timestamps[-1].strftime("%Y-%m-%d"),
            "start_price": prices[15],
            "end_price": prices[-1],
            "parameters": {
                "buy_threshold": buy_score_threshold,
                "sell_threshold": sell_score_threshold,
                "lookback_days": lookback_days
            },
            "trades": trades
        }

        return report

    def print_report(self, report: Dict):
        """打印回测报告"""
        print("\n" + "="*60)
        print("📈 回测报告")
        print("="*60)

        print(f"\n标的: {report['coin_id'].upper()}")
        print(f"期间: {report['start_date']} ~ {report['end_date']}")
        print(f"起始价: ${report['start_price']:.2f}")
        print(f"结束价: ${report['end_price']:.2f}")

        print("\n💰 资金变化")
        print(f"   初始资金:  ${report['initial_capital']:,.2f}")
        print(f"   最终价值:  ${report['final_value']:,.2f}")
        print(f"   总收益:    {report['total_return']:.2f}%")

        print("\n📊 vs 买入持有")
        print(f"   买入持有:   {report['buy_hold_return']:.2f}%")
        print(f"   策略差异:   {report['returns_diff']:+.2f}%")

        print("\n🔄 交易统计")
        print(f"   买入次数:   {report['buy_count']}")
        print(f"   卖出次数:   {report['sell_count']}")
        print(f"   总交易:     {report['total_trades']}")

        print("\n⚙️  参数")
        print(f"   买入阈值:   {report['parameters']['buy_threshold']}")
        print(f"   卖出阈值:   {report['parameters']['sell_threshold']}")

        # 显示最近5笔交易
        if report['trades']:
            print("\n📝 最近交易")
            for trade in report['trades'][-5:]:
                action_emoji = "🟢" if trade['action'] == "BUY" else "🔴"
                print(f"   {action_emoji} {trade['date']} | {trade['action']} @ ${trade['price']:.2f} | 评分: {trade['score']}")

        print("\n" + "="*60)


def main():
    """主函数"""
    engine = BacktestEngine()

    # 测试资产
    coins = [
        ("bitcoin", "BTC"),
        ("ethereum", "ETH"),
        ("solana", "SOL")
    ]

    output_dir = "/root/.openclaw/workspace/skills/investment-framework/data/backtests"
    import os
    os.makedirs(output_dir, exist_ok=True)

    for coin_id, symbol in coins:
        print(f"\n{'='*60}")
        print(f"回测 {symbol} ({coin_id})")
        print(f"{'='*60}")

        # 运行回测
        report = engine.run_backtest(
            coin_id=coin_id,
            initial_capital=10000,
            buy_score_threshold=60,
            sell_score_threshold=40,
            lookback_days=90
        )

        if "error" not in report:
            # 打印报告
            engine.print_report(report)

            # 保存报告
            output_file = f"{output_dir}/{symbol}-backtest-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✅ 回测报告已保存: {output_file}")

        # 等待，避免 API 限制
        print("\n⏳ 等待 7 秒以避免 API 限制...")
        import time
        time.sleep(7)

    print("\n" + "="*60)
    print("🎉 所有回测完成！")
    print("="*60)


if __name__ == "__main__":
    main()
