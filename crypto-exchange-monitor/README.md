# 加密货币交易所监控技能
 **基于 skill-from-masters 方法论构建**

---

## 功能
- WebSocket 实时价格监控, WebSocket 订单簿深度流, REST API 获取资金费率, 滑点自动计算, 可配置阈值告警, 多交易所支持, 异步,高并发架构

## ️ 架构设计

### 设计原则(来自 Martin Fowler + DevOps 最佳实践)
分离关注点, 说明=采集 → 处理 → 存储 → 告警, 实现=Adapter + Monitor 分离
单一职责, 说明=每个适配器只负责一个交易所, 实现=`ExchangeAdapter` 基类
开闭原则, 说明=开放扩展,关闭修改, 实现=继承 `ExchangeAdapter`
错误恢复, 说明=容错,重试,日志, 实现=`_on_error()` + logging

### 避坑机制(Anti-Patterns)
- 轮询间隔过导致限流: 使用 WebSocket 实时流
- 硬编码 API 端点: 配置化(`__init__` 参数)
- 不处理连接失败: `_on_error()` 回调
- 内存泄漏: 限制历史数据长度

## 代码结构
```
skills/crypto-exchange-monitor/
├── core.py # 核心框架
├── exchanges/ # 交易所适配器
│ ├── binance.py # Binance(示例)
│ ├── lighter.py # Lighter(待实现)
│ └── extended.py # Extended(待实现)
├── README.md # 本文件
└── requirements.txt # 依赖

## 快速开始

### 安装依赖
```bash
pip install websockets requests

### 基本用法
```python
import asyncio
from core import CryptoMonitor, BinanceAdapter

async def main():
 # 创建监控器
 monitor = CryptoMonitor()

 # 添加交易所
 binance = BinanceAdapter(api_key="your_key", api_secret="your_secret")
 monitor.add_exchange(binance)

 # 启动
 await monitor.start()

 # 订阅 EUR/USD 价格
 await binance.subscribe_price("EURUSDT")

 # 运行
 await asyncio.sleep(60) # 监控 60 秒

 # 停止
 await monitor.stop()

asyncio.run(main())

# 深度 10
await binance.subscribe_orderbook("EURUSDT", depth=10)

### 获取资金费率
funding = binance.fetch_funding_rate("EURUSDT")
print(f"资金费率: {funding.rate:.4%}")

# 价格低于 1.05 或高于 1.10 时告警
monitor.set_price_threshold(
 exchange="Binance",
 symbol="EURUSDT",
 min_price=1.05,
 max_price=1.10
)

## 支持的交易所

### 已支持
Binance, 状态= 完成, 备注=示例实现

### ⏳ 待实现
Lighter, 状态= 待 API, 需要信息=WebSocket 端点,REST API,认证方式
Extended, 状态= 待 API, 需要信息=API 文档,Cloudflare 绕过方案

## 添加新交易所

### 步骤
1. **创建适配器类**,继承 `ExchangeAdapter`:

# exchanges/your_exchange.py
from core import ExchangeAdapter, ExchangeType

class YouExchangeAdapter(ExchangeAdapter):
 def __init__(self, api_key=None, api_secret=None):
 super().__init__(
 name="YourExchange",
 exchange_type=ExchangeType.CEX, # 或 DEX
 rest_api_base="https://api.yourexchange.com",
 websocket_url="wss://api.yourexchange.com/ws",
 api_key=api_key,
 api_secret=api_secret

 async def connect(self):
 # 连接 WebSocket
 pass

 async def disconnect(self):
 # 断开连接

 async def subscribe_price(self, symbol: str):
 # 订阅价格

 async def subscribe_orderbook(self, symbol: str, depth: int):
 # 订阅订单簿

 def fetch_funding_rate(self, symbol: str):
 # 获取资金费率

2. **实现必需方法**:
 - `disconnect()`, `subscribe_price(symbol)`, `subscribe_orderbook(symbol, depth)`, `fetch_funding_rate(symbol)`

3. **使用适配器**:
from exchanges.you_exchange import YouExchangeAdapter

adapter = YouExchangeAdapter(api_key="your_key")
monitor.add_exchange(adapter)

## 监控示例

### 示例 1:监控 EUR/USD 价格
async def monitor_eurusd():
 binance = BinanceAdapter()

 # 自定义回调
 def on_price(update):
 print(f"EUR/USD: ${update.price:.4f}")

 binance.on_price = on_price

 await asyncio.sleep(3600) # 1 小时

# 买单时记录 entry_price
entry_price = 1.0850

# 卖出时记录 exit_price
exit_price = 1.0845

# 计算滑点
slippage = binance.calculate_slippage("EURUSDT", entry_price, exit_price)
print(f"滑点: {slippage.slippage_pct:.4}%")

# 设置阈值
monitor.set_price_threshold("Binance", "EURUSDT", min_price=1.08, max_price=1.09)

# 监控中会自动检查告警

## 数据模型

### PriceUpdate
@dataclass
class PriceUpdate:
 exchange: str # 交易所名称
 symbol: str # 交易对(EURUSDT)
 price: float # 价格
 timestamp: datetime
 source: str # 数据源

### OrderBookUpdate
class OrderBookUpdate:
 exchange: str
 symbol: str
 bids: List[OrderBookEntry] # 买单(价格从高到低)
 asks: List[OrderBookEntry] # 卖单(价格从低到高)

### FundingRate
class FundingRate:
 rate: float # 费率(如 0.0001)
 next_funding_time: datetime # 下次结算时间

## ️ 配置

# 可选:从环境变量加载 API 密钥
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"

### 日志等级
import logging
logging.getLogger("CryptoMonitor").setLevel(logging.DEBUG)

## 错误处理

### 连接失败
- 自动重连(未来版本)
- 回调 `on_error()` 通知

### API 限流
- 指数退避
- 日志记录

### 数据验证
- 价格有效性检查
- 时间戳验证

## 待办事项

### Lighter 适配器
需要提供:
- [ ] WebSocket 端点
- [ ] REST API 文档
- [ ] 认证方式(API Key/Secret)
- [ ] 订阅消息格式

### Extended 适配器
- [ ] API 文档链接
- [ ] Cloudflare 绕过方案
- [ ] 认证方式

### 增强功能
- [ ] 自动重连
- [ ] 数据持久化(SQLite/PostgreSQL)
- [ ] Telegram 通知集成
- [ ] Prometheus 指标导出
- [ ] Web Dashboard

## 致谢
- **skill-from-masters** - 方法论框架
- Martin Fowler - 架构设计原则
- DevOps 社区 - 监控最佳实践

## 许可证
MIT License

**创建时间**: 2026-02-16
**创建人**: SilverMoon
**技能版本**: 0.1.0