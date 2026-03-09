# 投资决策框架 V2 - 安装与使用指南

## V2 新增功能

### 核心升级
- **CoinGecko API 集成** - 实时价格,历史数据,技术指标
- **多资产支持** - BTC, ETH, SOL, AAPL, GOOGL, MSFT, TSLA, NVDA
- **Telegram 自动推送** - 每日报告自动发送
- **回测引擎** - 验证策略有效性
- **综合报告** - 加密货币 + 美股统一分析

---

## 安装完成

### 文件结构
```
skills/investment-framework/
├── SKILL.md # 完整使用指南
├── QUICK_REFERENCE.md # 快速参考卡
├── INSTALL_REPORT.md # 安装报告
├── UPGRADE_REPORT_V2.md # V2 升级报告
├── scripts/
│ ├── coingecko-api.sh # CoinGecko API 模块
│ ├── crypto-monitor.sh # 加密货币监控
│ ├── stocks-monitor.sh # 美股监控
│ ├── integrated-monitor.sh # 综合监控主脚本
│ ├── backtest.py # 回测引擎
│ ├── liquidity-monitor.sh # 流动性监控(V1)
│ ├── sentiment-monitor.sh # 情绪监控(V1)
│ ├── bottom-fishing.sh # 抄底模型(V1)
│ └── generate-recommendation.sh # 生成建议(V1)
└── data/
 ├── cache/ # API 缓存
 ├── backtests/ # 回测报告
 ├── integrated-report-latest.json # 最新综合报告
 └── daily-YYYY-MM-DD.md # 每日 Markdown 日志

## 快速开始

### 1. 测试 CoinGecko API
```bash
cd /root/.openclaw/workspace/skills/investment-framework/scripts

# 测试 API 连接
./coingecko-api.sh

预期输出:
=== CoinGecko API 测试 ===

1. 测试获取 BTC 价格:
{"bitcoin":{"usd":95000,"usd_24h_change":2.5,...}}

2. 测试获取恐慌贪婪指数:
{"value": 45, "classification": "Neutral"}

 API 测试完成

# 监控所有加密货币
./crypto-monitor.sh all

# 监控单个资产
./crypto-monitor.sh single bitcoin BTC

# 监控所有美股
./stocks-monitor.sh all

# 监控单只股票
./stocks-monitor.sh single AAPL Apple

# 生成综合报告(不推送 Telegram)
./integrated-monitor.sh

# 生成综合报告 + 推送 Telegram
./integrated-monitor.sh true

# 运行回测引擎
python3 backtest.py

## 支持的资产

### 加密货币(CoinGecko API)
BTC, 名称=Bitcoin, CoinGecko ID=bitcoin
ETH, 名称=Ethereum, CoinGecko ID=ethereum
SOL, 名称=Solana, CoinGecko ID=solana

### 美股(Alpha Vantage API)
AAPL, 名称=Apple Inc., 类型=科技股
GOOGL, 名称=Alphabet Inc., 类型=科技股
MSFT, 名称=Microsoft Corp., 类型=科技股
TSLA, 名称=Tesla Inc., 类型=电动车
NVDA, 名称=NVIDIA Corp., 类型=芯片

## Telegram 推送配置

### 方法 1:使用系统配置(推荐)
创建配置文件:
cat > /root/.openclaw/workspace/skills/investment-framework/data/.telegram-config << 'EOF'
TELEGRAM_BOT_TOKEN="你的_BOT_TOKEN"
TELEGRAM_CHAT_ID="7572458852"
EOF

### 方法 2:使用环境变量
export TELEGRAM_BOT_TOKEN="你的_BOT_TOKEN"
export TELEGRAM_CHAT_ID="7572458852"

### 获取 Telegram Bot Token
1. 在 Telegram 中搜索 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称和用户名
4. 复制生成的 Token

### 获取 Chat ID
1. 在 Telegram 中搜索 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 获取你的 Chat ID

## 回测验证

### 回测报告示例
 开始回测: bitcoin
 初始资金: $10,000
 买入阈值: 60
 卖出阈值: 40
 回测天数: 90

 回测报告
━━━━━━━━━━━━━━━━━━

标的: BTC
期间: 2024-11-24 ~ 2025-02-23
起始价: $65,000.00
结束价: $95,000.00

 资金变化
 初始资金: 10,000.00
 最终价值: 12,500.00
 总收益: 25.00%

 vs 买入持有
 买入持有: 46.15%
 策略差异: -21.15%

 交易统计
 买入次数: 3
 卖出次数: 2
 总交易: 5

## 定时任务设置

### 方法 1:使用 Cron(推荐)
编辑 crontab:
crontab -e

添加以下行:

# CoinGecko 免费版:每 4 小时运行一次(避免超限)
0 */4 * * * cd /root/.openclaw/workspace/skills/investment-framework/scripts && ./integrated-monitor.sh true >> /tmp/investment-monitor.log 2>&1

# 创建 Cron Job
cron add -j '{
 "name": "Investment Framework Monitor",
 "schedule": {
 "kind": "every",
 "everyMs": 14400000
 },
 "payload": {
 "kind": "systemEvent",
 "text": "cd /root/.openclaw/workspace/skills/investment-framework/scripts && ./integrated-monitor.sh true"
 "sessionTarget": "main",
 "enabled": true
}'

## 监控指标说明

### 四层决策模型
| 层级 | 指标 | 说明 |
| 第1层 | 流动性监控 | 净流动性,SOFR,MOVE 指数(需接入美联储数据)|
| 第2层 | 情绪监控 | NAAIM,恐慌贪婪指数,机构仓位 |
| 第3层 | 价值评估 | ROE,市值,现金流 |
| 第4层 | 抄底模型 | RSI,MVRV,恐慌指数 |

### 信号说明
STRONG BUY, 含义=市场极度超卖,强烈建议买入, 建议仓位=70-80%
BUY, 含义=市场偏低,可适当加仓, 建议仓位=60-70%
HODL, 含义=市场中性,保持仓位, 建议仓位=50-60%
SELL, 含义=市场偏高,可适当减仓, 建议仓位=40-50%
STRONG SELL, 含义=市场极度超买,建议减仓或对冲, 建议仓位=20-30%

## 常见问题

### Q: CoinGecko API 限制?
A: 免费版每分钟 10 次请求,每天 100 次请求.建议每 4 小时运行一次.

### Q: 美股数据不准确?
A: Alpha Vantage 每秒限制 5 次请求,如需高频数据,建议使用付费 API.

### Q: 如何添加新资产?
A: 在 `crypto-monitor.sh` 或 `stocks-monitor.sh` 中修改 `ASSETS` 或 `STOCKS` 数组.

### Q: 回测结果不理想?
A: 策略参数可能需要优化.尝试调整 `buy_score_threshold` 和 `sell_score_threshold`.

## 最佳实践
1. **定期运行** - 建议每 4-6 小时运行一次综合监控
2. **关注信号** - 当综合评分 ≥ 70 或 ≤ 30 时关注
3. **分散投资** - 不要单一信号做决策,参考多个指标
4. **回测验证** - 新策略先回测,确认有效性后再投入
5. **风险控制** - 设置止损,控制单一资产仓位

## 未来规划
- [ ] 接入美联储真实数据(SOFR,MOVE 指数)
- [ ] 接入 NAAIM 机构仓位数据
- [ ] 添加更多技术指标(MACD,布林带,KDJ)
- [ ] 机器学习优化策略参数
- [ ] Web 界面展示
- [ ] 移动端通知(Push,Email)

## 支持
如遇问题,请查看:
- 错误日志:`/tmp/investment-monitor.log`, API 缓存:`data/cache/`, 回测报告:`data/backtests/`

**版本**: V2.0
**更新日期**: 2026-02-23
**作者**: 银月 (SilverMoon)