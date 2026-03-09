#!/bin/bash
# 综合投资监控主脚本
# 整合：加密货币、美股、流动性、情绪四层决策模型

set -e

SCRIPT_DIR="$(dirname "$0")"
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"

# Telegram 配置
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-7572458852}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

# 函数：加载配置
function load_config() {
  # 检查是否有自定义 Telegram Bot Token
  if [ -f "$OUTPUT_DIR/.telegram-config" ]; then
    source "$OUTPUT_DIR/.telegram-config"
  fi
}

# 函数：发送 Telegram 消息
function send_telegram() {
  local message="$1"

  if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  未配置 Telegram Bot Token，跳过推送"
    return 1
  fi

  local escaped_message=$(echo "$message" | sed 's/[_*`\[\](){}|>#+-!]/\\&/g')
  local formatted_message=$(echo "$message")

  local response=$(curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{
      \"chat_id\": \"$TELEGRAM_CHAT_ID\",
      \"text\": \"$formatted_message\",
      \"parse_mode\": \"Markdown\"
    }")

  if echo "$response" | jq -e '.ok' > /dev/null 2>&1; then
    echo "✅ Telegram 消息已发送"
    return 0
  else
    echo "❌ Telegram 发送失败: $response"
    return 1
  fi
}

# 函数：生成 Telegram 格式报告
function generate_telegram_report() {
  local summary_json="$1"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  local avg_score=$(echo "$summary_json" | jq -r '.avg_score // 50')
  local overall_signal=$(echo "$summary_json" | jq -r '.overall_signal // "HODL"')
  local asset_count=$(echo "$summary_json" | jq -r '.assets_monitored // 0')

  # 根据信号设置 emoji
  local signal_emoji="⏳"
  case "$overall_signal" in
    "strong buy"*) signal_emoji="🚀" ;;
    "buy"*) signal_emoji="📈" ;;
    "sell"*) signal_emoji="📉" ;;
    "strong sell"*) signal_emoji="💥" ;;
  esac

  local report="📊 *投资决策框架日报*

━━━━━━━━━━━━━━━━━━━━━
📅 时间: \`$timestamp\`
━━━━━━━━━━━━━━━━━━━━━

${signal_emoji} *综合信号*: \`$overall_signal\`
📈 *综合评分*: \`$avg_score\`/100
👀 *监控资产*: \`$asset_count\` 个"

  # 添加资产详情
  local assets=$(echo "$summary_json" | jq -r '.assets[]? | @json')
  if [ -n "$assets" ]; then
    report+=""


    report+="━━━━━━━━━━━━━━━━━━━━━
*资产详情*
"

    echo "$summary_json" | jq -r '.assets[]? | "\(.symbol): \(.analysis.score)/100 - \(.analysis.signal)"' | while read line; do
      report+="$line
"
    done
  fi

  report+="
━━━━━━━━━━━━━━━━━━━━━"

  # 添加四层分析
  report+="

*🎯 四层决策模型*
"

  local crypto_count=$(echo "$summary_json" | jq '[.assets[]? | select(.coin_id != null)] | length')
  local stock_count=$(echo "$summary_json" | jq '[.assets[]? | select(.symbol? and (.coin_id == null or .coin_id == ""))] | length')

  report+="第1层 流动性: \`--\` (需接入美联储API)
第2层 情绪监控: \`$(echo "$summary_json" | jq -r '.assets[0].indicators.fear_greed.classification // "Neutral")' \`
第3层 价值评估: \`$(echo "$summary_json" | jq -r 'map(.indicators.mvrv // 1) | add / length | . * 100 | floor / 100')\`
第4层 抄底模型: \`$(echo "$summary_json" | jq -r 'map(.indicators.rsi // 50) | add / length | floor')\`"

  report+="
━━━━━━━━━━━━━━━━━━━━━

💡 *操作建议*

if echo "$overall_signal" | grep -q "buy"; then
  if echo "$overall_signal" | grep -q "strong"; then
    report+="当前市场处于超卖状态，可考虑分批建仓。建议仓位：70-80%"
  else
    report+="市场情绪偏多，可适当加仓。建议仓位：60-70%"
  fi
elif echo "$overall_signal" | grep -q "sell"; then
  if echo "$overall_signal" | grep -q "strong"; then
    report+="市场过热，建议减仓或对冲。建议仓位：20-30%"
  else
    report+="市场情绪偏空，可适当减仓。建议仓位：40-50%"
  fi
else
  report+="市场处于中性状态，建议保持现有仓位。建议仓位：50-60%"
fi

━━━━━━━━━━━━━━━━━━━━━"

  report+="

*⚠️ 免责声明*: 本报告仅供参考，不构成投资建议。投资有风险，需谨慎决策。"

  echo "$report"
}

# 函数：运行加密货币监控
function run_crypto_monitor() {
  echo "🪙 运行加密货币监控..."
  bash "$SCRIPT_DIR/crypto-monitor.sh" all
}

# 函数：运行美股监控
function run_stocks_monitor() {
  echo "📈 运行美股监控..."
  bash "$SCRIPT_DIR/stocks-monitor.sh" all
}

# 函数：合并所有监控结果
function merge_reports() {
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local crypto_report=""
  local stocks_report=""
  local liquid_report=""
  local sentiment_report=""

  # 读取各报告
  if [ -f "$OUTPUT_DIR/crypto-monitor-latest.json" ]; then
    crypto_report=$(cat "$OUTPUT_DIR/crypto-monitor-latest.json")
  fi

  if [ -f "$OUTPUT_DIR/stocks-monitor-latest.json" ]; then
    stocks_report=$(cat "$OUTPUT_DIR/stocks-monitor-latest.json")
  fi

  # 计算综合评分
  local all_assets=()
  local total_score=0
  local asset_count=0

  # 合并加密货币资产
  if [ -n "$crypto_report" ]; then
    echo "$crypto_report" | jq -c '.assets[]?' | while read -r asset; do
      local score=$(echo "$asset" | jq -r '.analysis.score')
      total_score=$((total_score + score))
      asset_count=$((asset_count + 1))
      all_assets+=("$asset")
    done
  fi

  # 合并美股资产
  if [ -n "$stocks_report" ]; then
    echo "$stocks_report" | jq -c '.stocks[]?' | while read -r asset; do
      local score=$(echo "$asset" | jq -r '.analysis.score')
      total_score=$((total_score + score))
      asset_count=$((asset_count + 1))
      all_assets+=("$asset")
    done
  fi

  # 计算平均分
  local avg_score=0
  [ $asset_count -gt 0 ] && avg_score=$((total_score / asset_count))

  # 生成综合信号
  local overall_signal="HODL"
  [ $avg_score -ge 70 ] && overall_signal="STRONG BUY"
  [ $avg_score -ge 60 ] && [ $avg_score -lt 70 ] && overall_signal="BUY"
  [ $avg_score -le 30 ] && overall_signal="STRONG SELL"
  [ $avg_score -gt 30 ] && [ $avg_score -le 40 ] && overall_signal="SELL"

  # 生成所有资产的 JSON 数组
  local all_assets_json="[]"
  if [ ${#all_assets[@]} -gt 0 ]; then
    all_assets_json=$(printf '%s\n' "${all_assets[@]}" | jq -s .)
  fi

  # 生成最终报告
  local final_report=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "summary": {
    "avg_score": $avg_score,
    "overall_signal": "$overall_signal",
    "assets_monitored": $asset_count
  },
  "assets": $all_assets_json
}
EOF
  )

  # 保存综合报告
  local output_file="$OUTPUT_DIR/integrated-report-$(date +%Y%m%d-%H%M%S).json"
  echo "$final_report" | jq '.' > "$output_file"
  echo "✅ 综合报告已保存: $output_file"

  # 保存最新版本
  echo "$final_report" | jq '.' > "$OUTPUT_DIR/integrated-report-latest.json"

  echo "$final_report"
}

# 函数：生成 Markdown 日志
function generate_markdown_log() {
  local summary_json="$1"
  local date=$(date +%Y-%m-%d)
  local output_file="$OUTPUT_DIR/daily-${date}.md"

  local avg_score=$(echo "$summary_json" | jq -r '.avg_score')
  local overall_signal=$(echo "$summary_json" | jq -r '.overall_signal')
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  cat > "$output_file" <<EOF
# 投资决策框架日报

**日期**: $date
**时间**: $timestamp

---

## 📊 综合摘要

| 指标 | 数值 |
|------|------|
| 综合评分 | $avg_score/100 |
| 综合信号 | $overall_signal |
| 监控资产数 | $(echo "$summary_json" | jq -r '.assets_monitored') |

---

## 🪙 加密货币

$(echo "$summary_json" | jq -r '.assets[]? | select(.coin_id != null) | "- **\(.symbol)**: \(.analysis.score)/100 - \(.analysis.signal) - 价格: \$\(.price.current) - RSI: \(.indicators.rsi)"' | sed 's/null/-/g')

---

## 📈 美股

$(echo "$summary_json" | jq -r '.assets[]? | select(.symbol? and (.coin_id == null or .coin_id == "")) | "- **\(.symbol)**: \(.analysis.score)/100 - \(.analysis.signal) - 价格: \$\(.price.current) - RSI: \(.indicators.rsi)"' | sed 's/null/-/g')

---

## 🎯 操作建议

$([ "$avg_score" -ge 70 ] && echo "⚠️ 市场超卖，可考虑分批建仓。建议仓位：70-80%")
$([ "$avg_score" -ge 60 ] && [ "$avg_score" -lt 70 ] && echo "📈 市场偏多，可适当加仓。建议仓位：60-70%")
$([ "$avg_score" -le 30 ] && echo "💥 市场过热，建议减仓。建议仓位：20-30%")
$([ "$avg_score" -gt 30 ] && [ "$avg_score" -le 40 ] && echo "📉 市场偏空，可适当减仓。建议仓位：40-50%")
$([ "$avg_score" -gt 40 ] && [ "$avg_score" -lt 60 ] && echo "⏳ 市场中性，保持仓位。建议仓位：50-60%")

---

## 📋 四层决策模型

| 层级 | 指标 | 状态 |
|------|------|------|
| 第1层 | 流动性监控 | 需接入美联储数据 |
| 第2层 | 情绪监控 | $(echo "$summary_json" | jq -r '.assets[0].indicators.fear_greed.classification // "Neutral")' |
| 第3层 | 价值评估 | 检查资产基本面 |
| 第4层 | 抄底模型 | RSI、恐慌指数 |

---

*报告生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)*
EOF

  echo "✅ Markdown 日志已保存: $output_file"
}

# 主函数
function main() {
  load_config

  local send_telegram=${1:-false}

  echo "━━━━━━━━━━━━━━━━━━"
  echo "🚀 投资决策框架 V2"
  echo "━━━━━━━━━━━━━━━━━━"
  echo ""

  # 1. 运行加密货币监控
  run_crypto_monitor
  echo ""

  # 2. 运行美股监控
  run_stocks_monitor
  echo ""

  # 3. 合并报告
  local summary=$(merge_reports)
  echo ""
  echo "━━━━━━━━━━━━━━━━━━"
  echo "📊 综合分析结果"
  echo "━━━━━━━━━━━━━━━━━━"

  local avg_score=$(echo "$summary" | jq -r '.avg_score')
  local overall_signal=$(echo "$summary" | jq -r '.overall_signal')

  printf "%-20s %s\n" "综合评分:" "${avg_score}/100"
  printf "%-20s %s\n" "综合信号:" "$overall_signal"
  printf "%-20s %s\n" "监控资产:" "$(echo "$summary" | jq -r '.assets_monitored') 个"
  echo "━━━━━━━━━━━━━━━━━━"

  # 4. 生成 Markdown 日志
  generate_markdown_log "$summary"

  # 5. 发送 Telegram（如果启用）
  if [ "$send_telegram" = "true" ]; then
    echo ""
    echo "📤 发送 Telegram 报告..."
    local telegram_report=$(generate_telegram_report "$summary")
    send_telegram "$telegram_report"
  fi

  echo ""
  echo "✅ 监控完成！"
  echo ""
  echo "📁 报告位置: $OUTPUT_DIR/"
  echo "   - 综合报告: integrated-report-latest.json"
  echo "   - 日志: daily-$(date +%Y-%m-%d).md"
}

# 执行
main "$@"
