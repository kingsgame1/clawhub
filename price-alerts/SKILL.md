---
name: price-alerts
description: 智能价格波动警报系统,支持加密货币,股票,外汇多市场实时监控,自定义警报规则,多渠道通知(Telegram,Email,Webhook).使用场景:(1) BTC/ETH 价格突破关键位置时立即通知,(2) 设置价格波动百分比警报(±5%),(3) 移动平均线金叉/死叉预警,(4) 24 小时/日内波动率超限警报.支持历史回测,策略优化,多资产组合监控.

# 价格波动警报系统

## 快速开始

### 配置 API 密钥
支持的免费 API:

加密货币, API=CoinGecko, 备注=免费,无 API Key
加密货币, API=Binance, 备注=基础行情免费
股票, API=Alpha Vantage, 备注=免费额度 500 次/天
外汇, API=Open Exchange Rates, 备注=免费额度 1000 次/月

### 创建配置文件
```bash
scripts/init_config.py --market crypto --symbol BTC
```

生成 `config.json`:

```json
{
 "alerts": [
 "symbol": "BTC-USD",
 "type": "price_above",
 "threshold": 75000.00,
 "notification": "telegram",
 "message": "BTC 突破 $75,000!"
 },
 "type": "change_percent",
 "threshold": 5.0,
 "notification": "telegram,email",
 "message": "BTC 涨跌幅超过 ±5%"
 }
 ],
 "check_interval": 60,
 "notification": {
 "telegram": {
 "bot_token": "YOUR_BOT_TOKEN",
 "chat_id": "YOUR_CHAT_ID"
 "email": {
 "smtp_server": "smtp.gmail.com",
 "smtp_port": 587,
 "username": "your@email.com",
 "password": "your_password"

### 启动监控
scripts/start_monitor.py --config config.json

## 警报类型

### 1. 价格突破警报
"threshold": 75000.00

触发条件:当前价格 ≥ 阈值

### 2. 价格跌破警报
"type": "price_below",
 "threshold": 65000.00

触发条件:当前价格 ≤ 阈值

### 3. 涨跌幅警报
"symbol": "ETH-USD",
 "threshold": 5.0

触发条件:|(当前价格 - 基准价格) / 基准价格| ≥ 阈值

### 4. 移动平均线警报
"type": "ma_cross",
 "ma_short": 50,
 "ma_long": 200,
 "cross_type": "golden"

触发条件:短期 MA 上穿长期 MA(金叉)或下穿(死叉)

### 5. 波动率警报
"type": "volatility",
 "threshold": 0.05,
 "period": "24h"

触发条件:24 小时波动率 ≥ 阈值

## 高级功能

### 条件组合警报
"name": "复合警报",
 "conditions": {
 "all": [
 {"symbol": "BTC-USD", "type": "price_above", "threshold": 70000},
 {"symbol": "ETH-USD", "type": "price_above", "threshold": 3500}
 ]
 "message": "BTC 和 ETH 同时突破关键位!"

支持逻辑组合:
- `all`: 所有条件都满足, `any`: 任一条件满足, `none`: 所有条件都不满足

### 时间窗口警报
"threshold": 75000,
 "time_window": {
 "start": "09:00",
 "end": "17:00",
 "timezone": "America/New_York"

只在交易时段内触发警报.

### 回调通知(Webhook)
"notification": "webhook",
 "webhook_url": "https://your-server.com/alert",
 "webhook_payload": {
 "symbol": "${symbol}",
 "price": "${price}",
 "timestamp": "${timestamp}"

# 回测过去 30 天的警报触发情况
scripts/backtest.py \
 --config config.json \
 --days 30 \
 --output backtest_results.json

# 生成回测报告
scripts/backtest_report.py \
 --input backtest_results.json \
 --output report.html

回测输出:
- 触发次数, 误报率, 善后表现(价格继续趋势概率)

## 策略优化

### A/B 测试不同阈值
scripts/optimize_thresholds.py \
 --symbol BTC-USD \
 --type price_above \
 --range 70000,80000 \
 --step 1000 \
 --days 30

输出最优阈值和回测数据.

### 市场情绪集成
"confirm_with": "fear_greed_index"

仅在市场情绪确认时才触发警报(例如恐贪指数 < 30).

## 通知渠道

# 发送测试通知
scripts/test_notification.py --channel telegram

# 发送测试邮件
scripts/test_notification.py --channel email

### Slack
"webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

## 多资产组合监控
"portfolio": {
 "BTC": 2.5,
 "ETH": 15.0,
 "USDT": 5000.0
 "type": "portfolio_change",
 "threshold": 0.05

监控整个投资组合的价值变化.

## 数据源配置

### CoinGecko(免费)
"data_source": {
 "provider": "coingecko",
 "api_key": null // 可选,有更高额度

### Binance
"provider": "binance",
 "api_key": "YOUR_API_KEY",
 "api_secret": "YOUR_API_SECRET"

### Alpha Vantage(股票)
"provider": "alpha_vantage",
 "api_key": "YOUR_API_KEY"

## 部署方案

### 开发环境
python3 scripts/start_monitor.py --config config.json

### 生产环境(systemd)
```ini
[Unit]
Description=Price Alerts Monitor
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/skills/price-alerts
ExecStart=/usr/bin/python3 /path/to/scripts/start_monitor.py --config /path/to/config.json
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "scripts/start_monitor.py", "--config", "config.json"]

## 错误处理

### API 限流
自动降级策略:
- CoinGecko 限流 → 切换到 Binance
- 轮询间隔自动加倍(60s → 120s)

### 网络断开
重试机制(指数退避):
- 尝试 1: 等待 10s
- 失败 → 记录日志,继续监控

## 参考文档
- CoinGecko API: `references/coingecko_api.md`, Binance API: `references/binance_api.md`, 回测方法论: `references/backtest_guide.md`

## 性能优化建议
1. **检查间隔**: 资产少时 30s,资产多时 60s
2. **缓存策略**: 价格缓存 2-5 秒,减少 API 调用
3. **异步处理**: 多个资产并行监控
4. **批量查询**: Binance 支持批量获取价格

## SkillPay 支付集成
本技能已集成 SkillPay 支付系统,按次付费使用.

### 费用说明
- 每次调用消耗 **1 token** (0.001 USDT)
- 1 USDT = 1000 tokens
- 扣费成功后才执行技能功能
- 余额不足时会返回充值链接

### 环境变量配置
创建 `.env` 文件(参考 `.env.example`):

# 必需:SkillPay 配置
SKILL_BILLING_API_KEY=your_skillpay_api_key_here
SKILL_ID=your_skill_id_here

# 可选:通知渠道配置
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

### Node.js 入口
使用集成的 Node.js 入口(推荐,支持自动扣费):

# 安装依赖
npm install

# 初始化配置(自动扣费)
node index.js --action=init

# 启动监控
node index.js --action=monitor --symbol BTC/USDT --threshold 5%

### 直接使用 Python 脚本(无需扣费)
如果你想跳过支付验证,可以直接运行Python脚本:

python3 scripts/init_config.py --market crypto --symbol BTC

️ **注意**: 直接使用Python脚本不会进行支付验证,仅用于本地调试或测试.

## 发布检查清单
在发布到 ClawHub 前,请确认以下项目:

- [ ] 已设置环境变量 `SKILL_BILLING_API_KEY` 和 `SKILL_ID`
- [ ] 已运行 `npm install` 安装依赖
- [ ] 已测试 `node index.js --action=init` 确认支付流程正常
- [ ] SKILL.md 已更新支付说明
- [ ] `.env.example` 包含所有必要的环境变量
- [ ] Python 脚本有执行权限 (`chmod +x scripts/*.py`)

发布后从 ClawHub 获取Skill ID,更新 `.env` 文件中的 `SKILL_ID`.

*版本: 1.0.0 | 更新日期: 2026-03-07 | 集成 SkillPay 支付*