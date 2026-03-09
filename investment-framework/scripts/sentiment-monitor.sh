#!/bin/bash
# 市场情绪监控脚本
# 检查 NAAIM 暴露指数、机构仓位、散户资金流向、估值水平

set -e

# 配置
SCORE=50  # 基础分 50（中性）
WARNINGS=()
GREED_COUNT=0
PANIC_COUNT=0
RECOMMENDATION="持有"

echo "=== 市场情绪监控 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 函数：模拟获取 NAAIM 暴露指数
function get_naaim_exposure() {
  # TODO: 接入真实 API
  # 0-100，>80 表示贪婪，<20 表示恐慌
  echo "85"
}

# 函数：模拟获取机构股票配置比例
function get_institutional_equity() {
  # TODO: 接入 State Street 数据
  echo "历史极值"
}

# 函数：模拟获取散户净买入额
function get_retail_net_buy() {
  # TODO: 接入 J.P. Morgan 数据
  # 返回历史百分位
  echo "92"
}

# 函数：模拟获取标普 500 远期市盈率
function get_sp500_forward_pe() {
  # TODO: 接入真实数据
  echo "23.5"
}

# 函数：输出情绪等级
function get_sentiment_level() {
  local score=$1
  if [ "$score" -ge 80 ]; then
    echo "极度贪婪"
  elif [ "$score" -ge 60 ]; then
    echo "贪婪"
  elif [ "$score" -ge 40 ]; then
    echo "中性"
  elif [ "$score" -ge 20 ]; then
    echo "恐慌"
  else
    echo "极度恐慌"
  fi
}

function get_sentiment_emoji() {
  local level="$1"
  case "$level" in
    "极度贪婪") echo "🤑" ;;
    "贪婪") echo "😊" ;;
    "中性") echo "😐" ;;
    "恐慌") echo "😰" ;;
    "极度恐慌") echo "😱" ;;
    *) echo "❓" ;;
  esac
}

# 1. 检查 NAAIM 暴露指数
echo "1. NAAIM 暴露指数..."
NAAIM=$(get_naaim_exposure)

if [ "$NAAIM" -gt 90 ]; then
  SCORE=$((SCORE + 20))
  GREED_COUNT=$((GREED_COUNT + 1))
  WARNINGS+=("NAAIM 暴露指数 ${NAAIM} > 90，过热")
elif [ "$NAAIM" -gt 80 ]; then
  SCORE=$((SCORE + 10))
  GREED_COUNT=$((GREED_COUNT + 1))
  WARNINGS+=("NAAIM 暴露指数 ${NAAIM} > 80，偏向过热")
elif [ "$NAAIM" -lt 20 ]; then
  SCORE=$((SCORE - 20))
  PANIC_COUNT=$((PANIC_COUNT + 1))
  WARNINGS+=("NAAIM 暴露指数 ${NAAIM} < 20，极度谨慎")
elif [ "$NAAIM" -lt 40 ]; then
  SCORE=$((SCORE - 10))
  PANIC_COUNT=$((PANIC_COUNT + 1))
  WARNINGS+=("NAAIM 暴露指数 ${NAAIM} < 40，偏向谨慎")
fi

echo "   NAAIM 暴露指数: ${NAAIM}/100"
echo ""

# 2. 检查机构股票配置比例
echo "2. 机构股票配置比例..."
INSTITUTIONAL=$(get_institutional_equity)

if [[ "$INSTITUTIONAL" == *"历史极值"* ]]; then
  SCORE=$((SCORE + 15))
  GREED_COUNT=$((GREED_COUNT + 1))
  WARNINGS+=("机构股票配置处于历史极值，过热信号")
elif [[ "$INSTITUTIONAL" == *"历史低位"* ]]; then
  SCORE=$((SCORE - 15))
  PANIC_COUNT=$((PANIC_COUNT + 1))
  WARNINGS+=("机构股票配置处于历史低位，谨慎信号")
fi

echo "   机构配置: $INSTITUTIONAL"
echo ""

# 3. 检查散户净买入额
echo "3. 散户净买入额..."
RETAIL=$(get_retail_net_buy)

if [ "$RETAIL" -gt 85 ]; then
  SCORE=$((SCORE + 10))
  GREED_COUNT=$((GREED_COUNT + 1))
  WARNINGS+=("散户净买入 ${RETAIL}% 历史水平，过热")
elif [ "$RETAIL" -lt 15 ]; then
  SCORE=$((SCORE - 10))
  PANIC_COUNT=$((PANIC_COUNT + 1))
  WARNINGS+=("散户净买入 ${RETAIL}% 历史水平，恐慌")
fi

echo "   散户净买入: ${RETAIL}% 历史水平"
echo ""

# 4. 检查标普 500 远期市盈率
echo "4. 标普 500 远期市盈率..."
PE=$(get_sp500_forward_pe)

if (( $(echo "$PE > 25" | bc -l) )); then
  SCORE=$((SCORE + 10))
  GREED_COUNT=$((GREED_COUNT + 1))
  WARNINGS+=("标普 500 PE ${PE}，估值偏高")
elif (( $(echo "$PE < 15" | bc -l) )); then
  SCORE=$((SCORE - 10))
  PANIC_COUNT=$((PANIC_COUNT + 1))
  WARNINGS+=("标普 500 PE ${PE}，估值偏低")
fi

echo "   标普 500 PE: ${PE}"
echo ""

# 计算最终分数（基准 50）
if [ $SCORE -gt 100 ]; then
  SCORE=100
fi
if [ $SCORE -lt 0 ]; then
  SCORE=0
fi

# 生成建议
if [ $GREED_COUNT -ge 3 ]; then
  RECOMMENDATION="大幅减仓或对冲"
elif [ $GREED_COUNT -ge 1 ]; then
  RECOMMENDATION="减仓"
elif [ $PANIC_COUNT -ge 3 ]; then
  RECOMMENDATION="反向操作：增持"
elif [ $PANIC_COUNT -ge 1 ]; then
  RECOMMENDATION="分批建仓"
fi

# 生成 JSON 输出
SENTIMENT_LEVEL=$(get_sentiment_level $SCORE)
SENTIMENT_EMOJI=$(get_sentiment_emoji "$SENTIMENT_LEVEL")

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
  "level": "$SENTIMENT_LEVEL",
  "emoji": "$SENTIMENT_EMOJI",
  "recommendation": "$RECOMMENDATION",
  "indicators": {
    "naaim_exposure": $NAAIM,
    "institutional_equity": "$INSTITUTIONAL",
    "retail_net_buy": $RETAIL,
    "sp500_forward_pe": $PE
  },
  "counts": {
    "greed_signals": $GREED_COUNT,
    "panic_signals": $PANIC_COUNT
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
echo "$JSON_OUTPUT" > "$OUTPUT_DIR/sentiment-$(date +%Y%m%d).json"

echo "✅ 已保存到: $OUTPUT_DIR/sentiment-$(date +%Y%m%d).json"
