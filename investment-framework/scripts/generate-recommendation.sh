#!/bin/bash
# 综合投资建议生成脚本
# 整合流动性、情绪、抄底指标，输出最终建议

set -e

# 配置
DATA_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
DATE=$(date +%Y%m%d)

echo "=== 综合投资建议 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查数据文件是否存在
LIQUIDITY_FILE="$DATA_DIR/liquidity-$DATE.json"
SENTIMENT_FILE="$DATA_DIR/sentiment-$DATE.json"
BOTTOM_FILE="$DATA_DIR/bottom-fishing-BTC-$DATE.json"

if [ ! -f "$LIQUIDITY_FILE" ]; then
  echo "⚠️  流动性数据不存在，先运行 liquidity-monitor.sh"
  exit 1
fi

if [ ! -f "$SENTIMENT_FILE" ]; then
  echo "⚠️  情绪数据不存在，先运行 sentiment-monitor.sh"
  exit 1
fi

# 读取 JSON 数据
LIQUIDITY=$(cat "$LIQUIDITY_FILE")
SENTIMENT=$(cat "$SENTIMENT_FILE")

# 默认值
BOTTOM_SCORE=0
BOTTOM_RECOMMENDATION="观望"

if [ -f "$BOTTOM_FILE" ]; then
  BOTTOM=$(cat "$BOTTOM_FILE")
  BOTTOM_SCORE=$(echo "$BOTTOM" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['indicators_hit'])")
  BOTTOM_RECOMMENDATION=$(echo "$BOTTOM" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['recommendation'])")
fi

# 提取指标
LIQUIDITY_SCORE=$(echo "$LIQUIDITY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['score'])")
LIQUIDITY_LEVEL=$(echo "$LIQUIDITY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['level'])")
LIQUIDITY_REC=$(echo "$LIQUIDITY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['recommendation'])")

SENTIMENT_SCORE=$(echo "$SENTIMENT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['score'])")
SENTIMENT_LEVEL=$(echo "$SENTIMENT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['level'])")
SENTIMENT_EMOJI=$(echo "$SENTIMENT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['emoji'])")
SENTIMENT_REC=$(echo "$SENTIMENT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['recommendation'])")

# 计算综合评分
# 流动性权重 40%，情绪权重 60%
TOTAL_SCORE=$(python3 -c "
liquid = $LIQUIDITY_SCORE
sentiment = $SENTIMENT_SCORE
total = int(liquid * 0.4 + sentiment * 0.6)
print(total)
")

# 生成综合建议
TOTAL_RECOMMENDATION="持有"
TOTAL_POSITION="70%"

# 流动性优先
if [[ "$LIQUIDITY_LEVEL" == *"危险"* ]]; then
  TOTAL_RECOMMENDATION="清仓避险"
  TOTAL_POSITION="0-20%"
elif [[ "$LIQUIDITY_LEVEL" == *"预警"* ]]; then
  TOTAL_RECOMMENDATION="大幅减仓"
  TOTAL_POSITION="30-50%"
fi

# 情绪调整 + 抄底信号
if [ $TOTAL_SCORE -lt 30 ]; then
  if [ $BOTTOM_SCORE -ge 4 ]; then
    TOTAL_RECOMMENDATION="分批抄底"
    TOTAL_POSITION="50-70%"
  else
    TOTAL_RECOMMENDATION="谨慎建仓"
    TOTAL_POSITION="40-60%"
  fi
elif [ $TOTAL_SCORE -gt 70 ]; then
  if [ $BOTTOM_SCORE -ge 4 ]; then
    TOTAL_RECOMMENDATION="保持仓位"
    TOTAL_POSITION="70-80%"
  else
    TOTAL_RECOMMENDATION="逐步减仓"
    TOTAL_POSITION="50-70%"
  fi
fi

# 输出摘要
echo "📊 每日市场摘要 | $(date '+%Y-%m-%d')"
echo ""
echo "### 宏观环境"
echo "**流动性评分**: $LIQUIDITY_SCORE/100 $LIQUIDITY_LEVEL"
echo "**建议**: $LIQUIDITY_REC"
echo ""

echo "### 市场情绪"
echo "**情绪评分**: $SENTIMENT_SCORE/100 $SENTIMENT_EMOJI $SENTIMENT_LEVEL"
echo "**建议**: $SENTIMENT_REC"
echo ""

if [ -f "$BOTTOM_FILE" ]; then
  echo "### 抄底信号"
  echo "**比特币抄底**: $BOTTOM_SCORE/6 个指标触发"
  echo "**建议**: $BOTTOM_RECOMMENDATION"
  echo ""
fi

echo "### 综合建议"
echo "**综合评分**: $TOTAL_SCORE/100"
echo "**建议操作**: $TOTAL_RECOMMENDATION"
echo "**目标仓位**: $TOTAL_POSITION"
echo ""

# 生成 Markdown 输出
MARKDOWN_OUTPUT=$(cat <<EOF
# 📊 每日市场摘要 | $(date '+%Y-%m-%d %H:%M')

---

## 宏观环境

**流动性评分**: $LIQUIDITY_SCORE/100 **$LIQUIDITY_LEVEL**

**建议**: $LIQUIDITY_REC

---

## 市场情绪

**情绪评分**: $SENTIMENT_SCORE/100 $SENTIMENT_EMOJI **$SENTIMENT_LEVEL**

**建议**: $SENTIMENT_REC

---

$(if [ -f "$BOTTOM_FILE" ]; then echo "
## 抄底信号

**比特币抄底**: $BOTTOM_SCORE/6 个指标触发 ✅

**建议**: $BOTTOM_RECOMMENDATION
"; fi)

---

## 综合建议

**综合评分**: $TOTAL_SCORE/100

**建议操作**: $TOTAL_RECOMMENDATION

**目标仓位**: $TOTAL_POSITION

---

*数据来源: 投资决策框架 V1*
*生成时间: $(date '+%H:%M:%S')*
EOF
)

# 保存 Markdown
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
echo "$MARKDOWN_OUTPUT" > "$OUTPUT_DIR/daily-summary-$DATE.md"
echo "✅ Markdown 已保存到: $OUTPUT_DIR/daily-summary-$DATE.md"

# 生成 JSON 输出
JSON_OUTPUT=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "date": "$DATE",
  "liquidity": {
    "score": $LIQUIDITY_SCORE,
    "level": "$LIQUIDITY_LEVEL",
    "recommendation": "$LIQUIDITY_REC"
  },
  "sentiment": {
    "score": $SENTIMENT_SCORE,
    "level": "$SENTIMENT_LEVEL",
    "emoji": "$SENTIMENT_EMOJI",
    "recommendation": "$SENTIMENT_REC"
  },
  "bottom_fishing": {
    "enabled": $([ -f "$BOTTOM_FILE" ] && echo "true" || echo "false"),
    "score": $BOTTOM_SCORE,
    "recommendation": "$BOTTOM_RECOMMENDATION"
  },
  "recommendation": {
    "score": $TOTAL_SCORE,
    "action": "$TOTAL_RECOMMENDATION",
    "position": "$TOTAL_POSITION"
  }
}
EOF
)

echo "$JSON_OUTPUT" > "$OUTPUT_DIR/recommendation-$DATE.json"
echo "✅ JSON 已保存到: $OUTPUT_DIR/recommendation-$DATE.json"

echo ""
echo "📋 建议摘要:"
echo "   操作: $TOTAL_RECOMMENDATION"
echo "   仓位: $TOTAL_POSITION"
