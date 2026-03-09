#!/bin/bash
# 宏观流动性监控脚本
# 检查净流动性、SOFR、MOVE 指数，输出评分和建议

set -e

# 配置
SCORE=0
WARNINGS=()
RECOMMENDATION="持有"

echo "=== 宏观流动性监控 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 函数：模拟获取净流动性变化
function get_net_liquidity_change() {
  # TODO: 接入真实 API
  # 暂时返回模拟数据
  echo "1.2"  # 正数表示流动在增加
}

# 函数：模拟获取 SOFR 利率
function get_sofr_rate() {
  # TODO: 接入真实 API
  echo "5.3"
}

# 函数：模拟获取 MOVE 指数
function get_move_index() {
  # TODO: 接入真实 API
  echo "115"
}

# 函数：输出等级描述
function get_level_desc() {
  local score=$1
  if [ "$score" -ge 80 ]; then
    echo "安全"
  elif [ "$score" -ge 60 ]; then
    echo "正常"
  elif [ "$score" -ge 40 ]; then
    echo "预警"
  else
    echo "危险"
  fi
}

# 1. 检查净流动性变化
echo "1. 净流动性变化..."
LIQUIDITY_CHANGE=$(get_net_liquidity_change)
LIQUIDITY_ABS=$(echo "$LIQUIDITY_CHANGE" | awk '{printf "%.1f", ($1<0?-$1:$1)}')

if (( $(echo "$LIQUIDITY_CHANGE < -5" | bc -l) )); then
  SCORE=$((SCORE - 30))
  WARNINGS+=("净流动性单周下降 ${LIQUIDITY_CHANGE}%")
  RECOMMENDATION="减持"
elif (( $(echo "$LIQUIDITY_CHANGE < -3" | bc -l) )); then
  SCORE=$((SCORE - 10))
  WARNINGS+=("净流动性单周下降 ${LIQUIDITY_CHANGE}%")
fi

echo "   净流动性: ${LIQUIDITY_CHANGE}%"
echo ""

# 2. 检查 SOFR 利率
echo "2. SOFR 利率..."
SOFR=$(get_sofr_rate)

if (( $(echo "$SOFR > 5.5" | bc -l) )); then
  SCORE=$((SCORE - 20))
  WARNINGS+=("SOFR 突破 5.5%")
  RECOMMENDATION="减仓"
elif (( $(echo "$SOFR > 5.0" | bc -l) )); then
  SCORE=$((SCORE - 10))
  WARNINGS+=("SOFR 超过 5.0%")
fi

echo "   SOFR: ${SOFR}%"
echo ""

# 3. 检查 MOVE 指数
echo "3. MOVE 指数（美债波动率）..."
MOVE=$(get_move_index)

if (( $(echo "$MOVE > 130" | bc -l) )); then
  SCORE=$((SCORE - 25))
  WARNINGS+=("MOVE 指数 ${MOVE}，波动率过高")
  RECOMMENDATION="清仓"
elif (( $(echo "$MOVE > 115" | bc -l) )); then
  SCORE=$((SCORE - 10))
  WARNINGS+=("MOVE 指数 ${MOVE}，波动率偏高")
fi

echo "   MOVE 指数: ${MOVE}"
echo ""

# 计算最终分数（基准 100）
SCORE=$((100 + SCORE))
if [ $SCORE -gt 100 ]; then
  SCORE=100
fi

# 生成 JSON 输出
LEVEL=$(get_level_desc $SCORE)

# 创建 warnings 数组作为 JSON 字符串
WARNINGS_JSON=""
if [ ${#WARNINGS[@]} -eq 0 ]; then
  WARNINGS_JSON="[]"
else
  FIRST=1
  for warning in "${WARNINGS[@]}"; do
    if [ -z "$FIRST" ]; then
      WARNINGS_JSON="${WARNINGS_JSON}, "
    fi
    WARNINGS_JSON="${WARNINGS_JSON}\"${warning}\""
    FIRST=""
  done
  WARNINGS_JSON="[${WARNINGS_JSON}]"
fi

JSON_OUTPUT=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "score": $SCORE,
  "level": "$LEVEL",
  "recommendation": "$RECOMMENDATION",
  "thresholds": {
    "net_liquidity_change": "${LIQUIDITY_CHANGE}%",
    "sofr": "${SOFR}%",
    "move_index": $MOVE
  },
  "warnings": ${WARNINGS_JSON}
}
EOF
)

# 输出到标准输出
echo "$JSON_OUTPUT"

# 保存到文件
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"
echo "$JSON_OUTPUT" > "$OUTPUT_DIR/liquidity-$(date +%Y%m%d).json"

echo "✅ 已保存到: $OUTPUT_DIR/liquidity-$(date +%Y%m%d).json"
