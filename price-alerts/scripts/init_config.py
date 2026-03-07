#!/usr/bin/env python3
"""
初始化配置文件
"""

import argparse
import json


def init_config(market, symbol):
    """初始化配置模板"""
    config = {
        "alerts": [
            {
                "symbol": f"{symbol}-USD",
                "type": "price_above",
                "threshold": 75000.0 if symbol.upper() == "BTC" else 4000.0,
                "notification": "telegram",
                "message": f"{symbol.upper()} 突破关键价格！"
            },
            {
                "symbol": f"{symbol}-USD",
                "type": "change_percent",
                "threshold": 5.0,
                "notification": "telegram",
                "message": f"{symbol.upper()} 涨跌幅超过 ±5%"
            }
        ],
        "check_interval": 60,
        "notification": {
            "telegram": {
                "bot_token": "YOUR_BOT_TOKEN",
                "chat_id": "YOUR_CHAT_ID"
            }
        }
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✓ 配置文件已创建: config.json")
    print(f"  市场: {market}")
    print(f"  标的: {symbol}")
    print(f"\n请编辑 config.json，填入你的 Telegram Bot Token 和 Chat ID")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化配置")
    parser.add_argument("--market", default="crypto", help="市场类型 (crypto/stock/forex)")
    parser.add_argument("--symbol", required=True, help="标的符号 (如 BTC、ETH)")

    args = parser.parse_args()

    init_config(args.market, args.symbol)
