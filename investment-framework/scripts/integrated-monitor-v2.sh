#!/bin/bash
# 综合投资监控主脚本（修复版）
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

  local formatted_message="$message"

  local response=$(curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{
      \"chat_id\": \"$TELEGRAM_CHAT_ID\",
      \"text\": \"$formatted_message\",
      \"parse_mode\": \"HTML\"
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

  local avg_score=$(echo "$summary_json" | jq -r '.summary.avg_score // 50')
  local overall_signal=$(echo "$summary_json" | jq -r '.summary.overall_signal // "HODL"')
  local asset_count=$(echo "$summary_json" | jq -r '.summary.assets_monitored // 0')

  # 根据信号设置 emoji
  local signal_emoji="⏳"
  case "$overall_signal" in
    "STRONG BUY"*) signal_emoji="🚀" ;;
    "BUY"*) signal_emoji="📈" ;;
    "SELL"*) signal_emoji="📉" ;;
    "STRONG SELL"*) signal_emoji="💥" ;;
  esac

  # 生成操作建议
  local suggestion=""
  if echo "$overall_signal" | grep -qi "strong.*buy"; then
    suggestion="市场极度超卖，可分批建仓。建议仓位 70-80%"
  elif echo "$overall_signal" | grep -qi "buy"; then
    suggestion="市场情绪偏多，可适当加仓。建议仓位 60-70%"
  elif echo "$overall_signal" | grep -qi "strong.*sell"; then
    suggestion="市场极度超买，减仓对冲。建议仓位 20-30%"
  elif echo "$overall_signal" | grep -qi "sell"; then
    suggestion="市场情绪偏空，适当减仓。建议仓位 40-50%"
  else
    suggestion="市场处于中性，保持仓位。建议仓位 50-60%"
  fi

  # 获取四层数据（添加安全检查）
  local fear_greed="Neutral"
  local avg_rsi="50"
  local avg_mvrv="1"

  # 只有当 assets 存在且是数组时才提取数据
  local assets_count=$(echo "$summary_json" | jq 'if has("assets") then .assets | length else 0 end')
  if [ "$assets_count" -gt 0 ]; then
    # 提取第一个资产的恐慌指数
    local first_asset=$(echo "$summary_json" | jq '.assets[0] // {}')
    if echo "$first_asset" | jq -e '.indicators' >/dev/null 2>&1; then
      fear_greed=$(echo "$first_asset" | jq -r '.indicators.fear_greed.classification // "Neutral"')
    fi

    # 计算平均 RSI
    avg_rsi=$(echo "$summary_json" | jq '[.assets[]?.indicators.rsi // 50] | add / length | floor // 50')

    # 计算平均 MVRV
    avg_mvrv=$(echo "$summary_json" | jq '[.assets[]?.indicators.mvrv // 1] | add / length | . * 100 | floor / 100 // 1')
  fi

  # 构建报告
  local report="<b>📊 投资决策框架日报</b>

━━━━━━━━━━━━━━━━━━━━━
📅 <b>时间:</b> $timestamp
━━━━━━━━━━━━━━━━━━━━━

${signal_emoji} <b>综合信号:</b> $overall_signal
📈 <b>综合评分:</b> $avg_score/100
👀 <b>监控资产:</b> $asset_count 个

━━━━━━━━━━━━━━━━━━━━━
<b>🎯 四层决策模型</b>

第1层 流动性: -- (需接入美联储API)
第2层 情绪监控: $fear_greed
第3层 价值评估: $avg_mvrv
第4层 抄底模型: RSI $avg_rsi

━━━━━━━━━━━━━━━━━━━━━
<b>💡 操作建议</b>

$suggestion"

  # 添加资产详情
  local assets_count=$(echo "$summary_json" | jq 'if has("assets") then .assets | length else 0 end')
  if [ "$assets_count" -gt 0 ]; then
    report+="
━━━━━━━━━━━━━━━━━━━━━
<b>📋 资产详情</b>

"
    echo "$summary_json" | jq -r '.assets[]? | @text "| \(.symbol // "N/A") | $\(try .price.current catch "N/A") | \(try .price.change_24h catch "N/A")% | \(try .indicators.rsi catch "N/A") | \(.analysis.signal // "HODL") |"' 2>/dev/null | while IFS='|' read symbol price change rsi signal; do
      local symbol_clean=$(echo "$symbol" | xargs)
      local price_clean=$(echo "$price" | xargs)
      local change_clean=$(echo "$change" | xargs)
      local rsi_clean=$(echo "$rsi" | xargs)
      local signal_clean=$(echo "$signal" | xargs)
      
      # 计算其他指标
      local mvrv_clean=$(echo "$summary_json" | jq -r "[.assets[]? | select(.symbol == \"$symbol_clean\")] | .[0].indicators.mvrv // \"N/A\"")
      local fg_clean=$(echo "$summary_json" | jq -r "[.assets[]? | select(.symbol == \"$symbol_clean\")] | .[0].indicators.fear_greed.classification // \"N/A\"")
      local ath_change_clean=$(echo "$summary_json" | jq -r "[.assets[]? | select(.symbol == \"$symbol_clean\")] | .[0].indicators.ath_change // \"N/A\"")
      
      # 格式化涨跌幅
      local change_prefix=""
      if [ -n "$change_clean" ] && [ "$change_clean" != "N/A" ]; then
        local change_val=$(echo "$change_clean" | awk '{printf "%.2f", $1}')
        change_clean="$change_val"
      fi
      
      report+="<b>🪙 $symbol_clean</b>
• 当前价格: $price_clean"
      [ -n "$change_clean" ] && [ "$change_clean" != "N/A" ] && report+=" ($change_clean%)"
      report+="

• RSI(14): $rsi_clean"
      [ -n "$ath_change_clean" ] && [ "$ath_change_clean" != "N/A" ] && report+=" | 距离ATH: $ath_change_clean%"
      report+="

• MVRV: $mvrv_clean | 恐慌指数: $fg_clean
• 评分: \($echo "$summary_json" | jq -r "[.assets[]? | select(.symbol == \"$symbol_clean\")] | .[0].analysis.score // \"N/A\"")/100 | 信号: \($signal_clean)

"
    done
  fi

  report+="
━━━━━━━━━━━━━━━━━━━━━

<i>⚠️ 免责声明: 本报告仅供参考，不构成投资建议。投资有风险，需谨慎决策。</i>"

  echo "$report"
}

# 函数：运行加密货币监控
function run_crypto_monitor() {
  echo "🪙 运行加密货币监控..."
  bash "$SCRIPT_DIR/crypto-monitor.sh" all 2>/dev/null | tail -20
}

# 函数：运行美股监控
function run_stocks_monitor() {
  echo "📈 运行美股监控..."
  bash "$SCRIPT_DIR/stocks-monitor.sh" all 2>/dev/null | tail -20
}

# 函数：合并所有监控结果
function merge_reports() {
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local crypto_report=""
  local stocks_report=""

  # 读取各报告
  [ -f "$OUTPUT_DIR/crypto-monitor-latest.json" ] && crypto_report=$(cat "$OUTPUT_DIR/crypto-monitor-latest.json" 2>/dev/null)
  [ -f "$OUTPUT_DIR/stocks-monitor-latest.json" ] && stocks_report=$(cat "$OUTPUT_DIR/stocks-monitor-latest.json" 2>/dev/null)

  # 计算综合评分
  local all_assets_json="[]"
  local total_score=0
  local asset_count=0

  # 提取所有资产
  if [ -n "$crypto_report" ]; then
    local crypto_assets_array=$(echo "$crypto_report" | jq -c '.assets // []')
    if [ "$crypto_assets_array" != "[]" ]; then
      all_assets_json=$(echo "$all_assets_json" | jq --argjson a "$crypto_assets_array" '. + $a')
    fi
  fi

  if [ -n "$stocks_report" ]; then
    local stocks_assets_array=$(echo "$stocks_report" | jq -c '.stocks // []')
    if [ "$stocks_assets_array" != "[]" ]; then
      all_assets_json=$(echo "$all_assets_json" | jq --argjson a "$stocks_assets_array" '. + $a')
    fi
  fi

  # 计算平均分
  local asset_count=$(echo "$all_assets_json" | jq 'length')
  local total_score=$(echo "$all_assets_json" | jq '[.[].analysis.score // 50] | add // 0')
  local avg_score=0
  [ $asset_count -gt 0 ] && avg_score=$((total_score / asset_count))

  # 生成综合信号
  local overall_signal="HODL"
  [ $avg_score -ge 70 ] && overall_signal="STRONG BUY"
  [ $avg_score -ge 60 ] && [ $avg_score -lt 70 ] && overall_signal="BUY"
  [ $avg_score -le 30 ] && overall_signal="STRONG SELL"
  [ $avg_score -gt 30 ] && [ $avg_score -le 40 ] && overall_signal="SELL"

  # 生成最终报告
  cat <<EOF
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
}

# 函数：生成 Markdown 日志
function generate_markdown_log() {
  local summary_json="$1"
  local date=$(date +%Y-%m-%d)
  local output_file="$OUTPUT_DIR/daily-${date}.md"

  local avg_score=$(echo "$summary_json" | jq -r '.summary.avg_score')
  local overall_signal=$(echo "$summary_json" | jq -r '.summary.overall_signal')
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  cat > "$output_file" <<EOF
# 投资决策框架日报

**日期:** $date
**时间:** $timestamp

---

## 📊 综合摘要

| 指标 | 数值 |
|------|------|
| 综合评分 | $avg_score/100 |
| 综合信号 | $overall_signal |
| 监控资产数 | $(echo "$summary_json" | jq -r '.summary.assets_monitored') |

---

## 🪙 加密货币

$(echo "$summary_json" | jq -r '.assets[]? | select(.coin_id != null) | "- **\(.symbol)**: \(.analysis.score // 50)/100 - \(.analysis.signal // "HODL")"' || echo "*暂无数据*")

---

## 📈 美股

$(echo "$summary_json" | jq -r '.assets[]? | select(.symbol? and (.coin_id == null or .coin_id == "")) | "- **\(.symbol // "N/A")**: \(.analysis.score // 50)/100 - \(.analysis.signal // "HODL")"' || echo "*暂无数据*")

---

**生成时间:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
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
  echo "📊 合成综合报告..."
  local summary=$(merge_reports)
  echo ""

  # 保存综合报告
  local output_file="$OUTPUT_DIR/integrated-report-$(date +%Y%m%d-%H%M%S).json"
  echo "$summary" | jq '.' > "$output_file"
  echo "✅ 综合报告已保存: $output_file"

  echo "$summary" | jq '.' > "$OUTPUT_DIR/integrated-report-latest.json"

  # 显示摘要
  local avg_score=$(echo "$summary" | jq -r '.summary.avg_score')
  local overall_signal=$(echo "$summary" | jq -r '.summary.overall_signal')
  local assets_count=$(echo "$summary" | jq -r '.summary.assets_monitored')

  echo ""
  echo "━━━━━━━━━━━━━━━━━━"
  echo "📊 综合分析结果"
  echo "━━━━━━━━━━━━━━━━━━"
  printf "%-20s %s\n" "综合评分:" "${avg_score}/100"
  printf "%-20s %s\n" "综合信号:" "$overall_signal"
  printf "%-20s %s\n" "监控资产:" "${assets_count} 个"
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
