#!/usr/bin/env python3
"""
价格监控主程序
"""

import argparse
import json
import time
import requests
from pathlib import Path
from datetime import datetime


class PriceMonitor:
    """价格监控器"""

    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.previous_prices = {}

    def load_config(self, config_file):
        """加载配置"""
        with open(config_file) as f:
            return json.load(f)

    def get_price(self, symbol):
        """获取价格（CoinGecko 免费 API）"""
        # 映射到 CoinGecko ID
        symbol_map = {
            "BTC-USD": "bitcoin",
            "ETH-USD": "ethereum",
        }

        coin_id = symbol_map.get(symbol, symbol.lower().replace("-usd", ""))

        resp = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"}
        )
        resp.raise_for_status()

        data = resp.json()
        return data[coin_id]["usd"]

    def check_alerts(self):
        """检查并触发警报"""
        for alert in self.config.get("alerts", []):
            symbol = alert["symbol"]
            alert_type = alert["type"]
            threshold = alert["threshold"]

            try:
                current_price = self.get_price(symbol)

                # 保存之前的价格
                if symbol not in self.previous_prices:
                    self.previous_prices[symbol] = current_price
                    continue

                previous_price = self.previous_prices[symbol]

                # 检查警报条件
                triggered = False

                if alert_type == "price_above":
                    triggered = current_price >= threshold
                elif alert_type == "price_below":
                    triggered = current_price <= threshold
                elif alert_type == "change_percent":
                    change = abs((current_price - previous_price) / previous_price) * 100
                    triggered = change >= threshold

                # 触发警报
                if triggered:
                    self.send_notification(alert, current_price)

                # 更新价格
                self.previous_prices[symbol] = current_price

            except Exception as e:
                print(f"错误: {e}")

    def send_notification(self, alert, price):
        """发送通知"""
        message = alert.get("message", "价格警报")

        # Telegram 通知
        telegram = self.config.get("notification", {}).get("telegram", {})
        if telegram:
            bot_token = telegram.get("bot_token")
            chat_id = telegram.get("chat_id")

            if bot_token and chat_id:
                full_message = f"{message}\n\n当前价格: ${price}"
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

                requests.post(url, data={
                    "chat_id": chat_id,
                    "text": full_message
                })

                print(f"✓ 警报已发送: {message}")

    def run(self):
        """运行监控"""
        interval = self.config.get("check_interval", 60)

        print(f"价格监控已启动，检查间隔: {interval} 秒")
        print(f"警报数量: {len(self.config.get('alerts', []))}")

        while True:
            try:
                self.check_alerts()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n监控已停止")
                break
            except Exception as e:
                print(f"错误: {e}，继续监控...")
                time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="价格监控")
    parser.add_argument("--config", required=True, help="配置文件路径")

    args = parser.parse_args()

    monitor = PriceMonitor(args.config)
    monitor.run()
