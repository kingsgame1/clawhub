#!/usr/bin/env python3
"""
加密货币交易所监控技能框架

基于 skill-from-masters 方法论创建，整合 DevOps 监控最佳实践。

功能：
- 支持 WebSocket 实时价格/订单簿监控
- 支持 REST API 获取资金费率等数据
- 滑点计算和告警阈值
- 可扩展的交易所适配器

作者: SilverMoon
创建时间: 2026-02-16
"""

import asyncio
import websockets
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# 配置和常量
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CryptoMonitor")


class ExchangeType(Enum):
    """交易所类型"""
    CEX = "centralized"  # 中心化交易所
    DEX = "decentralized"  # 去中心化交易所


# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class PriceUpdate:
    """价格更新"""
    exchange: str
    symbol: str
    price: float
    timestamp: datetime
    source: str = "websocket"


@dataclass
class OrderBookEntry:
    """订单簿条目"""
    price: float
    quantity: float
    timestamp: datetime


@dataclass
class OrderBookUpdate:
    """订单簿更新"""
    exchange: str
    symbol: str
    bids: List[OrderBookEntry]  # 买单
    asks: List[OrderBookEntry]  # 卖单
    timestamp: datetime


@dataclass
class FundingRate:
    """资金费率"""
    exchange: str
    symbol: str
    rate: float
    next_funding_time: datetime
    timestamp: datetime


@dataclass
class SlippageCalculation:
    """滑点计算结果"""
    exchange: str
    symbol: str
    entry_price: float
    exit_price: float
    slippage_pct: float
    timestamp: datetime


# ============================================================================
# 基类：交易所适配器
# ============================================================================

class ExchangeAdapter:
    """交易所适配器基类"""

    def __init__(
        self,
        name: str,
        exchange_type: ExchangeType,
        rest_api_base: Optional[str] = None,
        websocket_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        self.name = name
        self.exchange_type = exchange_type
        self.rest_api_base = rest_api_base
        self.websocket_url = websocket_url
        self.api_key = api_key
        self.api_secret = api_secret

        # 回调函数
        self.on_price: Optional[Callable[[PriceUpdate], None]] = None
        self.on_orderbook: Optional[Callable[[OrderBookUpdate], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None

    # ==================== 抽象方法 ====================

    async def connect(self) -> None:
        """连接到交易所"""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """断开连接"""
        raise NotImplementedError

    async def subscribe_price(self, symbol: str) -> None:
        """订阅价格"""
        raise NotImplementedError

    async def subscribe_orderbook(self, symbol: str, depth: int = 10) -> None:
        """订阅订单簿"""
        raise NotImplementedError

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRate]:
        """获取资金费率"""
        raise NotImplementedError

    # ==================== 实用方法 ====================

    def calculate_slippage(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float
    ) -> SlippageCalculation:
        """计算滑点"""
        slippage_pct = ((exit_price - entry_price) / entry_price) * 100
        return SlippageCalculation(
            exchange=self.name,
            symbol=symbol,
            entry_price=entry_price,
            exit_price=exit_price,
            slippage_pct=slippage_pct,
            timestamp=datetime.now()
        )

    async def _websocket_loop(self, symbols: List[str]):
        """WebSocket 主循环（子类实现）"""
        raise NotImplementedError

    def _call_price_callback(self, update: PriceUpdate):
        """调用价格回调"""
        if self.on_price:
            try:
                self.on_price(update)
            except Exception as e:
                logger.error(f"价格回调错误: {e}")
                if self.on_error:
                    self.on_error(e)

    def _call_orderbook_callback(self, update: OrderBookUpdate):
        """调用订单簿回调"""
        if self.on_orderbook:
            try:
                self.on_orderbook(update)
            except Exception as e:
                logger.error(f"订单簿回调错误: {e}")
                if self.on_error:
                    self.on_error(e)


# ============================================================================
# 示例：Binance 适配器（可参考实现 Lighter/Extended）
# ============================================================================

class BinanceAdapter(ExchangeAdapter):
    """Binance 交易所适配器（示例）"""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        super().__init__(
            name="Binance",
            exchange_type=ExchangeType.CEX,
            rest_api_base="https://api.binance.com",
            websocket_url="wss://stream.binance.com:9443/ws",
            api_key=api_key,
            api_secret=api_secret
        )
        self.ws_connection = None

    async def connect(self) -> None:
        """连接 WebSocket"""
        logger.info(f"连接到 {self.name}...")
        try:
            self.ws_connection = await websockets.connect(self.websocket_url)
            logger.info(f"已连接到 {self.name}")
        except Exception as e:
            logger.error(f"连接失败: {e}")
            if self.on_error:
                self.on_error(e)
            raise

    async def disconnect(self) -> None:
        """断开连接"""
        if self.ws_connection:
            await self.ws_connection.close()
            logger.info(f"已断开 {self.name}")

    async def subscribe_price(self, symbol: str) -> None:
        """订阅价格"""
        # 转换格式（如 BTCUSDT -> btcusdt）
        stream = f"{symbol.lower()}@trade"
        payload = {
            "method": "SUBSCRIBE",
            "params": [stream],
            "id": 1
        }
        await self.ws_connection.send(json.dumps(payload))
        logger.info(f"订阅价格: {symbol}")

        # 启动监听
        asyncio.create_task(self._listen_price(symbol))

    async def _listen_price(self, symbol: str):
        """监听价格"""
        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                if "p" in data:  # 价格字段
                    price = float(data["p"])
                    update = PriceUpdate(
                        exchange=self.name,
                        symbol=symbol.upper(),
                        price=price,
                        timestamp=datetime.now()
                    )
                    self._call_price_callback(update)
        except Exception as e:
            logger.error(f"价格监听错误: {e}")
            if self.on_error:
                self.on_error(e)

    async def subscribe_orderbook(self, symbol: str, depth: int = 10):
        """订阅订单簿"""
        stream = f"{symbol.lower()}@depth{depth}"
        payload = {
            "method": "SUBSCRIBE",
            "params": [stream],
            "id": 2
        }
        await self.ws_connection.send(json.dumps(payload))
        logger.info(f"订阅订单簿: {symbol} (depth={depth})")

        asyncio.create_task(self._listen_orderbook(symbol))

    async def _listen_orderbook(self, symbol: str):
        """监听订单簿"""
        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                if "b" in data and "a" in data:
                    bids = [
                        OrderBookEntry(
                            price=float(p[0]),
                            quantity=float(p[1]),
                            timestamp=datetime.now()
                        )
                        for p in data["b"][:10]
                    ]
                    asks = [
                        OrderBookEntry(
                            price=float(p[0]),
                            quantity=float(p[1]),
                            timestamp=datetime.now()
                        )
                        for p in data["a"][:10]
                    ]
                    update = OrderBookUpdate(
                        exchange=self.name,
                        symbol=symbol.upper(),
                        bids=bids,
                        asks=asks,
                        timestamp=datetime.now()
                    )
                    self._call_orderbook_callback(update)
        except Exception as e:
            logger.error(f"订单簿监听错误: {e}")
            if self.on_error:
                self.on_error(e)

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRate]:
        """获取资金费率"""
        try:
            url = f"{self.rest_api_base}/fapi/v1/fundingRate"
            params = {"symbol": symbol.upper(), "limit": 1}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()[0]

            return FundingRate(
                exchange=self.name,
                symbol=symbol.upper(),
                rate=float(data["fundingRate"]),
                next_funding_time=datetime.fromtimestamp(int(data["fundingTime"]) / 1000),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"获取资金费率失败: {e}")
            return None


# ============================================================================
# 监控器
# ============================================================================

class CryptoMonitor:
    """加密货币监控器"""

    def __init__(self):
        self.exchanges: Dict[str, ExchangeAdapter] = {}
        self.price_history: Dict[str, List[PriceUpdate]] = {}
        self.thresholds: Dict[str, Dict[str, float]] = {}

    def add_exchange(self, adapter: ExchangeAdapter):
        """添加交易所"""
        self.exchanges[adapter.name] = adapter

        # 注册回调
        adapter.on_price = self._on_price_update
        adapter.on_orderbook = self._on_orderbook_update
        adapter.on_error = self._on_error

        logger.info(f"已添加交易所: {adapter.name}")

    async def start(self):
        """启动监控"""
        logger.info("启动监控器...")

        # 连接所有交易所
        for exchange in self.exchanges.values():
            await exchange.connect()

        logger.info("监控器已启动")

    async def stop(self):
        """停止监控"""
        logger.info("停止监控器...")

        # 断开所有交易所
        for exchange in self.exchanges.values():
            await exchange.disconnect()

        logger.info("监控器已停止")

    # ==================== 回调处理 ====================

    def _on_price_update(self, update: PriceUpdate):
        """价格更新回调"""
        key = f"{update.exchange}:{update.symbol}"

        # 保存历史
        if key not in self.price_history:
            self.price_history[key] = []
        self.price_history[key].append(update)

        # 限制历史长度（最近 1000 条）
        if len(self.price_history[key]) > 1000:
            self.price_history[key] = self.price_history[key][-1000:]

        # 检查阈值告警
        self._check_price_threshold(update)

        logger.info(f"价格更新: {update.exchange} {update.symbol} = ${update.price:.4f}")

    def _on_orderbook_update(self, update: OrderBookUpdate):
        """订单簿更新回调"""
        if update.bids and update.asks:
            best_bid = update.bids[0].price
            best_ask = update.asks[0].price
            spread = ((best_ask - best_bid) / best_bid) * 100
            logger.info(
                f"订单簿: {update.exchange} {update.symbol} "
                f"买一=${best_bid:.4f} 卖一=${best_ask:.4f} 价差={spread:.4f}%"
            )

    def _on_error(self, error: Exception):
        """错误处理"""
        logger.error(f"监控错误: {error}")

    # ==================== 阈值告警 ====================

    def set_price_threshold(
        self,
        exchange: str,
        symbol: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ):
        """设置价格阈值"""
        key = f"{exchange}:{symbol}"
        self.thresholds[key] = {
            "min": min_price,
            "max": max_price
        }
        logger.info(f"设置阈值: {exchange} {symbol} [{min_price}, {max_price}]")

    def _check_price_threshold(self, update: PriceUpdate):
        """检查价格阈值"""
        key = f"{update.exchange}:{update.symbol}"

        if key in self.thresholds:
            threshold = self.thresholds[key]

            if threshold.get("min") and update.price < threshold["min"]:
                logger.warning(
                    f"价格低于阈值: {update.exchange} {update.symbol} "
                    f"当前=${update.price:.4f} 阈值=${threshold['min']:.4f}"
                )

            if threshold.get("max") and update.price > threshold["max"]:
                logger.warning(
                    f"价格高于阈值: {update.exchange} {update.symbol} "
                    f"当前=${update.price:.4f} 阈值=${threshold['max']:.4f}"
                )


# ============================================================================
# Lighter/Extended 适配器（待实现）
# ============================================================================

class LighterAdapter(ExchangeAdapter):
    """
    Lighter 交易所适配器

    TODO: 需要用户提供：
    1. WebSocket 端点
    2. REST API 端点
    3. 认证方式（如有）
    4. API 文档链接
    """

    async def connect(self) -> None:
        # TODO: 实现
        pass

    async def disconnect(self) -> None:
        # TODO: 实现
        pass

    async def subscribe_price(self, symbol: str) -> None:
        # TODO: 实现
        pass

    async def subscribe_orderbook(self, symbol: str, depth: int = 10):
        # TODO: 实现
        pass

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRate]:
        # TODO: 实现
        pass


class ExtendedAdapter(ExchangeAdapter):
    """
    Extended 交易所适配器

    TODO: 需要用户提供：
    1. Cloudflare 绕过方案
    2. API 文档
    3. 认证方式
    """

    async def connect(self) -> None:
        # TODO: 实现
        pass

    async def disconnect(self) -> None:
        # TODO: 实现
        pass

    async def subscribe_price(self, symbol: str) -> None:
        # TODO: 实现
        pass

    async def subscribe_orderbook(self, symbol: str, depth: int = 10):
        # TODO: 实现
        pass

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRate]:
        # TODO: 实现
        pass


# ============================================================================
# 主程序（示例）
# ============================================================================

async def main():
    """主程序示例"""

    # 创建监控器
    monitor = CryptoMonitor()

    # 示例：添加 Binance（需要 Lighter/Extended 时参考此实现）
    # binance = BinanceAdapter(api_key="your_api_key", api_secret="your_api_secret")
    # monitor.add_exchange(binance)

    # TODO: 添加 Lighter（待 API 信息）
    # lighter = LighterAdapter()
    # monitor.add_exchange(lighter)

    # TODO: 添加 Extended（待 API 信息）
    # extended = ExtendedAdapter()
    # monitor.add_exchange(extended)

    # 设置阈值示例
    # monitor.set_price_threshold("Binance", "BTCUSDT", min_price=50000, max_price=60000)

    # 启动
    await monitor.start()

    # 订阅示例
    # await binance.subscribe_price("BTCUSDT")
    # await binance.subscribe_orderbook("BTCUSDT", depth=10)

    # 运行 10 秒
    await asyncio.sleep(10)

    # 停止
    await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
