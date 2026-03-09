#!/bin/bash
# 比特币抄底模型脚本
# 监控 6 个核心指标，输出抄底建议

set -e

# 配置
ASSET="${1:-BTC}"
SCORE=0
INDICATORS_HIT=0
INDICATORS=(
  "RSI周线<30"
  "成交量萎缩"
  "MVRV<1.0"
  "恐慌指数>75"
  "矿机关机价"
  "LTH占比上升"
)
WARNINGS=()
RECOMMENDATION="观望"

echo "=== 比特币抄底模型 ($ASSET) ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 函数：模拟获取 RSI 周线
function get_rsi_weekly() {
  # TODO: 接入 TradingView 或 CoinGecko API
  echo "28"  # <30 表示超跌
}

# 函数：模拟获取交易量变化
function get_volume_change() {
  # TODO: 接入真实 API
  echo "0.75"  # <1 表示萎缩
}

# 函数：模拟获取 MVRV 比率
function get_mvrv_ratio() {
  # TODO: 接入 Glassnode 或 lookintobitcoin.com
  echo "0.95"  # <1.0 表示市值低于实现市值
}

# 函数：模拟获取恐慌指数
function get_fear_greed_index() {
  # TODO: 接入 alternative.me 的恐惧与贪婪指数
  echo "82"  # >75 表示恐慌
}

# 函数：模拟获取矿机关机价
function get_miner_shutdown_price() {
  # TODO: 接入真实数据，如 S19 Pro 成本线
  echo "42000"  # 假设当前价格 41000
}

# 函数：模拟获取当前价格
function get_current_price() {
  # TODO: 接入 CoinGecko API
  echo "41000"
}

# 函数：模拟获取长期持有者占比
function get_lth_ratio() {
  # TODO: 接入 Glassnode 数据
  echo "62"  # >60 表示抄底信号
}

# 1. 检查 RSI 周线
echo "1. RSI 周线..."
RSI=$(get_rsi_weekly)
if [ "$RSI" -lt 30 ]; then
  INDICATORS_HIT=$((INDICATORS_HIT + 1))
  SCORE=$((SCORE + 1))
  echo "   RSI: ${RSI} < 30 ✅ 超跌信号"
else
  echo "   RSI: ${RSI} ❌"
fi
echo ""

# 2. 检查成交量变化
echo "2. 成交量变化..."
VOLUME=$(get_volume_change)
if (( $(echo "$VOLUME < 1.0" | bc -l) )); then
  INDICATORS_HIT=$((INDICATORS_HIT + 1))
  SCORE=$((SCORE + 1))
  echo "   成交量：${VOLUME} x 30日均量 ✅ 萎缩信号"
else
  echo "   成交量：${VOLUME} x 30日均量 ❌"
fi
echo ""

# 3. 检查 MVRV 比率
echo "3. MVRV 比率..."
MVRV=$(get_mvrv_ratio)
if (( $(echo "$MVRV < 1.0" | bc -l) )); then
  INDICATORS_HIT=$((INDICATORS_HIT + 1))
  SCORE=$((SCORE + 1))
  echo "   MVRV: ${MVRV} ✅ 市值低于实现市值"
else
  echo "   MVRV: ${MVRV} ❌"
fi
echo ""

# 4. 检查恐慌指数
echo "4. 社交媒体恐慌指数..."
FGI=$(get_fear_greed_index)
if [ "$FGI" -gt 75 ]; then
  INDICATORS_HIT=$((INDICATORS_HIT + 1))
  SCORE=$((SCORE + 1))
  echo "   恐慌指数: ${FGI} > 75 ✅ 极度恐慌"
else
  echo "   恐慌指数: ${FGI} ❌"
fi
echo ""

# 5. 检查矿机关机价
echo "5. 矿机关机价对比..."
SHUTDOWN=$(get_miner_shutdown_price)
CURRENT=$(get_current_price)
if (( $(echo "$CURRENT < $SHUTDOWN" | bc -l) )); then
  INDICATORS_HIT=$((INDICATORS_HIT + 1))
  SCORE=$((SCORE + 1))
  echo "   现价: $CURRENT < 关机价: $SHUTDOWN ✅ 接近成本线"
else
  echo "   现价: $CURRENT vs 关机价: $SHUTDOWN ❌"
fi
echo ""

# 6. 检查长期持有者占比
echo "6. 长期持有者（LTH）占比..."
LTH=$(get_lth_ratio)
if [ "$LTH" -gt 60 ]; then
  INDICATORS_HIT=$((INDICATORS_HIT + 1))
  SCORE=$((SCORE + 1))
  echo "   LTH 占比: ${LTH}% ✅ 抄底信号"
else
  echo "   LTH 占比: ${LTH}% ❌"
fi
echo ""

# 生成建议
if [ $INDICATORS_HIT -ge 5 ]; then
  RECOMMENDATION="重仓抄底"
  POSITION="50%"
elif [ $INDICATORS_HIT -ge 4 ]; then
  RECOMMENDATION="分批建仓"
  POSITION="30%"
elif [ $INDICATORS_HIT -ge 2 ]; then
  RECOMMENDATION="谨慎观察"
  POSITION="10%"
else
  RECOMMENDATION="观望"
  POSITION="0%"
fi

# 生成 JSON 输出
JSON_OUTPUT=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "asset": "$ASSET",
  "indicators_hit": $INDICATORS_HIT,
  "score": "$SCORE/6",
  "recommendation": "$RECOMMENDATION",
  "position": "$POSITION",
  "strategy": "$([ $INDICATORS_HIT -ge 4 ] && echo "一次性建仓" || echo "分批建仓")",
  "indicators": {
    "rsi_weekly": ${RSI},
    "volume_ratio": $VOLUME,
    "mvrv_ratio": $MVRV,
    "fear_greed_index": $FGI,
    "price_current": $CURRENT,
    "price_shutdown": $SHUTDOWN,
    "lth_ratio": ${LTH}
  },
  "thresholds": {
    "rsi_weekly": "< 30",
    "volume_ratio": "< 1.0",
    "mvrv_ratio": "< 1.0",
    "fear_greed_index": "> 75",
    "price_comparison": "< 矿机关机价",
    "lth_ratio": "> 60%"
  }
}
EOF
)

# 输出到标准输出
echo "$JSON_OUTPUT"

# 保存到文件
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"
echo "$JSON_OUTPUT" > "$OUTPUT_DIR/bottom-fishing-${ASSET}-$(date +%Y%m%d).json"

echo "✅ 已保存到: $OUTPUT_DIR/bottom-fishing-${ASSET}-$(date +%Y%m%d).json"
