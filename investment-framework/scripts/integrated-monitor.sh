#!/bin/bash
# 投资决策框架主脚本 - HTML 格式修复版

set -e

SCRIPT_DIR="$(dirname "$0")"
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"

# Telegram 配置
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-7572458852}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

# 函数：加载配置
function load_config() {
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

  # 转义 HTML 特殊字符
  local formatted_message=$(echo "$message" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')

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

  # 获取四层数据
  local fear_greed="Neutral"
  local avg_rsi="50"
  local avg_mvrv="1"

  local assets_count=$(echo "$summary_json" | jq 'if has("assets") then .assets | length else 0 end')
  if [ "$assets_count" -gt 0 ]; then
    local first_asset=$(echo "$summary_json" | jq '.assets[0] // {}')
    if echo "$first_asset" | jq -e '.indicators' >/dev/null 2>&1; then
      fear_greed=$(echo "$first_asset" | jq -r '.indicators.fear_greed.classification // "Neutral"')
    fi
    avg_rsi=$(echo "$summary_json" | jq '[.assets[]?.indicators.rsi // 50] | add / length | floor // 50')
    avg_mvrv=$(echo "$summary_json" | jq '[.assets[]?.indicators.mvrv // 1] | add / length | . * 100 | floor / 100 // 1')
  fi

  # 构建报告开头
  local report="📊 投资决策框架日报

━━━━━━━━━━━━━━━━━━━━━
📅 时间: $timestamp
━━━━━━━━━━━━━━━━━━━━━

📈 综合信号: $overall_signal $signal_emoji
📊 综合评分: $avg_score/100
👀 监控资产: $asset_count 个

━━━━━━━━━━━━━━━━━━━━━
🎯 四层决策模型

第1层 流动性: -- (需接入美联储API)
第2层 情绪监控: $fear_greed
第3层 价值评估: $avg_mvrv
第4层 抄底模型: RSI $avg_rsi

━━━━━━━━━━━━━━━━━━━━━
💡 操作建议

$suggestion"

  # 添加资产详情
  if [ "$assets_count" -gt 0 ]; then
    report+="
━━━━━━━━━━━━━━━━━━━━━
📋 资产详情

"
    # 使用 jq 生成格式化的资产详情
    echo "$summary_json" | jq -r '.assets[]? | @json' | while IFS= read -r asset_json; do
      local symbol=$(echo "$asset_json" | jq -r '.symbol // "N/A"')
      local price=$(echo "$asset_json" | jq -r 'try (.price.current | tostring) catch "N/A"')
      local change=$(echo "$asset_json" | jq -r 'try (.price.change_24h | tostring) catch "N/A"')
      local rsi=$(echo "$asset_json" | jq -r 'try (.indicators.rsi | tostring) catch "N/A"')
      local mvrv=$(echo "$asset_json" | jq -r 'try (.indicators.mvrv | tostring) catch "N/A"')
      local fg=$(echo "$asset_json" | jq -r '.indicators.fear_greed.classification // "N/A"')
      local ath_change=$(echo "$asset_json" | jq -r 'try (.indicators.ath_change | tostring) catch "N/A"')
      local score=$(echo "$asset_json" | jq -r '.analysis.score // 50')
      local signal=$(echo "$asset_json" | jq -r '.analysis.signal // "HODL"')

      # 格式化涨跌
      local change_formatted="$change"
      if [ "$change" != "N/A" ] && [ "$change" != "" ]; then
        local change_val=$(echo "$change" | awk '{printf "%.2f", $1}')
        if [ "$(echo "$change < 0" | bc -l)" -eq 1 ]; then
          change_formatted="$change_val%"
        else
          change_formatted="+$change_val%"
        fi
      fi

      # 格式化 ATH 距离
      local ath_formatted="$ath_change"
      if [ "$ath_change" != "N/A" ] && [ "$ath_change" != "" ]; then
        local ath_val=$(echo "$ath_change" | awk '{printf "%.1f", $1}')
        ath_formatted="$ath_val%"
      fi

      # RSI 状态
      local rsi_status=""
      [ "$rsi" != "N/A" ] && {
        local rsi_num=$(echo "$rsi" | awk '{printf "%.0f", $1}')
        if [ "$rsi_num" -le 30 ]; then
          rsi_status="⚠️  超卖"
        elif [ "$rsi_num" -ge 70 ]; then
          rsi_status="⚠️  超买"
        fi
      }

      # 恐慌指数 emoji
      local fg_emoji=""
      case "$fg" in
        "Extreme Fear"*) fg_emoji="🔴" ;;
        "Fear"*) fg_emoji="🟠" ;;
        "Greed"*) fg_emoji="🟢" ;;
        "Extreme Greed"*) fg_emoji="💚" ;;
      esac

      # 构建资产条目
      report+="🪙 $symbol
• 当前价格: \$$price ($change_formatted)
• RSI(14): $rsi $rsi_status"
      [ "$ath_formatted" != "N/A" ] && report+=" | 距离ATH: $ath_formatted"
      report+="
• MVRV: $mvrv | 恐慌指数: $fg $fg_emoji
• 评分: $score/100 | 信号: $signal

"
    done
  fi

  # 市场概况
  report+="━━━━━━━━━━━━━━━━━━━━━
📈 市场概况

• 24h加密货币总市值: 数据不可用
• 恐慌指数: $fear_greed
• 市场情绪: "

  case "$fear_greed" in
    "Extreme Fear"*) report+="极度恐慌" ;;
    "Fear"*) report+="恐慌" ;;
    "Neutral"*) report+="中性" ;;
    "Greed"*) report+="贪婪" ;;
    "Extreme Greed"*) report+="极度贪婪" ;;
    *) report+="$fear_greed" ;;
  esac

  # 自动化信息
  report+="
━━━━━━━━━━━━━━━━━━━━━
🔄 自动化配置

✅ 定时任务: 已设置 (每4小时自动推送)
⏰ 下次推送: \$(date -d \"+4 hours\" \"+%Y-%m-%d %H:%M\") (4小时后)
📁 日志文件: /tmp/investment-monitor.log
━━━━━━━━━━━━━━━━━━━━━

⚠️  免责声明: 本报告仅供参考，不构成投资建议。投资有风险，需谨慎决策。"

  echo "$report"
}

# 函数：运行加密货币监控
function run_crypto_monitor() {
  echo "🪙 运行加密货币监控..."
  bash "$SCRIPT_DIR/crypto-monitor.sh" all 2>/dev/null | tail -10
}

# 函数：运行美股监控
function run_stocks_monitor() {
  echo "📈 运行美股监控..."
  bash "$SCRIPT_DIR/stocks-monitor.sh" all 2>/dev/null | tail -10
}

# 函数：合并所有监控结果
function merge_reports() {
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local crypto_report=""
  local stocks_report=""

  [ -f "$OUTPUT_DIR/crypto-monitor-latest.json" ] && crypto_report=$(cat "$OUTPUT_DIR/crypto-monitor-latest.json" 2>/dev/null)
  [ -f "$OUTPUT_DIR/stocks-monitor-latest.json" ] && stocks_report=$(cat "$OUTPUT_DIR/stocks-monitor-latest.json" 2>/dev/null)

  local all_assets_json="[]"

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

  local asset_count=$(echo "$all_assets_json" | jq 'length')
  local total_score=$(echo "$all_assets_json" | jq '[.[].analysis.score // 50] | add // 0')
  local avg_score=0
  [ $asset_count -gt 0 ] && avg_score=$((total_score / asset_count))

  local overall_signal="HODL"
  [ $avg_score -ge 70 ] && overall_signal="STRONG BUY"
  [ $avg_score -ge 60 ] && [ $avg_score -lt 70 ] && overall_signal="BUY"
  [ $avg_score -le 30 ] && overall_signal="STRONG SELL"
  [ $avg_score -gt 30 ] && [ $avg_score -le 40 ] && overall_signal="SELL"

  cat <<EOF
{"timestamp": "$timestamp",
 "summary": {"avg_score": $avg_score,
             "overall_signal": "$overall_signal",
             "assets_monitored": $asset_count},
 "assets": $all_assets_json}
EOF
}

# 主函数
function main() {
  load_config
  local send_telegram=${1:-false}

  echo "━━━━━━━━━━━━━━━━━━"
  echo "🚀 投资决策框架 V2 (HTML fix)"
  echo "━━━━━━━━━━━━━━━━━━"
  echo ""

  run_crypto_monitor
  echo ""
  run_stocks_monitor
  echo ""

  echo "📊 合成综合报告..."
  local summary=$(merge_reports)
  echo ""

  local output_file="$OUTPUT_DIR/integrated-report-$(date +%Y%m%d-%H%M%S).json"
  echo "$summary" | jq '.' > "$output_file"
  echo "✅ 综合报告已保存: $output_file"

  echo "$summary" | jq '.' > "$OUTPUT_DIR/integrated-report-latest.json"

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

  if [ "$send_telegram" = "true" ]; then
    echo ""
    echo "📤 发送 Telegram 报告..."
    local telegram_report=$(generate_telegram_report "$summary")
    send_telegram "$telegram_report"
  fi

  echo ""
  echo "✅ 监控完成！"
}

main "$@"
