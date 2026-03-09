# 投资决策框架 V1 - 快速参考卡

## 三秒上手
```bash

# 运行完整监控
cd /root/.openclaw/workspace/skills/investment-framework/scripts
./liquidity-monitor.sh # 宏观流动性
./sentiment-monitor.sh # 市场情绪
./bottom-fishing.sh BTC # 比特币抄底
./generate-recommendation.sh # 综合建议
```

---

## 输出示例

### 每日市场摘要
```markdown

### 宏观环境
**流动性评分**: 90/100 安全
**建议**: 持有

### 市场情绪
**情绪评分**: 85/100 极度贪婪
**建议**: 大幅减仓或对冲

### 抄底信号
**比特币抄底**: 6/6 个指标触发
**建议**: 重仓抄底

### 综合建议
**综合评分**: 87/100
**建议操作**: 保持仓位
**目标仓位**: 70-80%

## 四层决策模型
第一层: 流动性监控 (40% 权重)
 ↓ 检查净流动性,SOFR,MOVE 指数
第二层: 情绪监控 (30% 权重)
 ↓ 检查 NAAIM,机构仓位,散户资金
第三层: 价值评估 (20% 权重)
 ↓ 评估标的基本面
第四层: 抄底模型 (10% 权重)
 ↓ 捕捉极端行情机会

## 核心指标速查

### 流动性监控
**净流动性变化**, 阈值=< -5%, 信号=预警,减持
**SOFR 利率**, 阈值=> 5.5%, 信号=减仓信号
**MOVE 指数**, 阈值=> 130, 信号=止损

### 情绪监控
| **NAAIM 暴露指数** | > 80 | 过热 |
| **机构配置** | 历史极值 | 过热 |
| **散户净买入** | > 85% | 过热 |
| **标普 500 PE** | > 25 | 估值偏高 |

### 比特币抄底模型
| **RSI 周线** | < 30 | 超跌 |
| **成交量变化** | < 1.0x | 萎缩 |
| **MVRV 比率** | < 1.0 | 市值低于实现 |
| **恐慌指数** | > 75 | 极度恐慌 |
| **现价 vs 关机价** | < 关机价 | 接近成本 |
| **LTH 占比** | > 60% | 抄底信号 |

## 使用流程

# 1. 运行所有监控
./liquidity-monitor.sh
./sentiment-monitor.sh
./bottom-fishing.sh BTC

# 2. 生成建议
./generate-recommendation.sh

# 3. 查看结果
cat data/daily-summary-$(date +%Y%m%d).md

# 每日 07:00 运行
0 7 * * * cd /root/.openclaw/workspace/skills/investment-framework/scripts && ./liquidity-monitor.sh > /dev/null 2>&1

# 每日 09:00 运行
0 9 * * * cd /root/.openclaw/workspace/skills/investment-framework/scripts && ./sentiment-monitor.sh > /dev/null 2>&1

# 每日 12:00 运行
0 12 * * * cd /root/.openclaw/workspace/skills/investment-framework/scripts && ./bottom-fishing.sh BTC > /dev/null 2>&1

# 每日 20:00 生成建议
0 20 * * * cd /root/.openclaw/workspace/skills/investment-framework/scripts && ./generate-recommendation.sh > /dev/null 2>&1

## 数据文件
data/
├── liquidity-20260223.json # 流动性监控
├── sentiment-20260223.json # 情绪监控
├── bottom-fishing-BTC-20260223.json # 抄底模型
├── recommendation-20260223.json # 综合建议
└── daily-summary-20260223.md # Markdown 摘要

## 常见问题
**Q: 指标阈值从哪里来?**
A: 来源于 XinGPT 的实践经验,后续可以根据实际使用情况调整.

**Q: 为什么流动性和情绪信号矛盾?**
A: 这是正常的.流动性是宏观环境,情绪是市场温度.最终建议会综合判断.

**Q: 是否支持其他加密货币?**
A: 当前仅支持 BTC,需要添加其他币种的评估标准.

**Q: 数据源是真实的吗?**
A: 当前使用模拟数据,需要接入真实 API.

## 接入真实数据

# 替换 liquidity-monitor.sh 中的函数
function get_net_liquidity_change() {
 curl -s "https://api.federalreserve.gov/..." | jq ...
}

function get_sofr_rate() {
 curl -s "https://www.newyorkfed.org/..." | jq ...

function get_move_index() {
 curl -s "https://markets.cboe.com/..." | jq ...

# 替换 sentiment-monitor.sh 中的函数
function get_naaim_exposure() {
 curl -s "https://naaim.org/api/..." | jq ...

function get_retail_net_buy() {
 curl -s "https://cmegroup.com/..." | jq ...

# 替换 bottom-fishing.sh 中的函数
function get_mvrv_ratio() {
 curl -s "https://api.lookintobitcoin.com/..." | jq ...

function get_fear_greed_index() {
 curl -s "https://api.alternative.me/..." | jq ...

## 相关文档
- **SKILL.md**: 完整使用指南, **README.md**: 安装与配置, **QUICK_REFERENCE.md**: 本文件

**版本**: v1.0
**下次更新**: 接入真实数据 API
**反馈**: 随时反馈使用体验,我会持续优化