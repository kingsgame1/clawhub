#!/bin/bash
# 美股监控脚本（使用 Alpha Vantage 免费API）
# 支持苹果、Google 等美股

set -e

# 配置
# Alpha Vantage 免费密钥（注册后获取，每秒限制 5 次请求，每日 500 次请求）
# 如果没有密钥，使用模拟数据
AV_API_KEY="${ALPHA_VANTAGE_KEY:-demo}"

API_BASE="https://www.alphavantage.co/query"

OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"

# 美股资产配置（SYMBOL:NAME）
STOCKS=(
  "AAPL:Apple"
  "GOOGL:Google"
  "MSFT:Microsoft"
  "TSLA:Tesla"
  "NVDA:NVIDIA"
)

# 函数：获取股票价格
function get_stock_price() {
  local symbol=$1
  local api_key=$2

  # 使用 GLOBAL_QUOTE 获取实时价格
  local url="$API_BASE?function=GLOBAL_QUOTE&symbol=$symbol&apikey=$api_key"
  local response=$(curl -s "$url")

  # 检查 API 限制
  if echo "$response" | grep -q "Thank you for using Alpha Vantage"; then
    echo "error: API limit reached"
    return 1
  fi

  # 检查是否有有效数据
  if ! echo "$response" | jq -e '.["Global Quote"]' > /dev/null 2>&1; then
    echo "error: invalid response"
    return 1
  fi

  echo "$response"
}

# 函数：获取技术指标（RSI）
function get_rsi() {
  local symbol=$1
  local api_key=$2
  local interval=${3:-daily}
  local time_period=${4:-14}

  local url="$API_BASE?function=RSI&symbol=$symbol&interval=$interval&time_period=$time_period&series_type=close&apikey=$api_key"
  local response=$(curl -s "$url")

  echo "$response"
}

# 函数：获取股票历史数据
function get_stock_history() {
  local symbol=$1
  local api_key=$2
  local outputsize=${3:-compact}  # compact=100天, full=20年

  local url="$API_BASE?function=TIME_SERIES_DAILY_ADJUSTED&symbol=$symbol&outputsize=$outputsize&apikey=$api_key"
  local response=$(curl -s "$url")

  echo "$response"
}

# 函数：生成股票报告
function generate_stock_report() {
  local symbol=$1
  local name=$2
  local api_key=$3

  echo "=== 分析 $name ($symbol) ==="

  # 获取价格数据
  local price_data=$(get_stock_price "$symbol" "$api_key")

  if echo "$price_data" | grep -q "error"; then
    echo "⚠️  API 限制或错误，使用模拟数据"
    price_data='{"Global Quote":{"01. symbol":"'"$symbol"'","02. open":"150.00","03. high":"155.00","04. low":"148.00","05. price":"152.00","06. volume":"10000000","07. latest trading day":"2026-02-23","08. previous close":"150.00","09. change":"2.00","10. change percent":"1.33%"}}'
  fi

  local current_price=$(echo "$price_data" | jq -r '.["Global Quote"]["05. price"]')
  local open_price=$(echo "$price_data" | jq -r '.["Global Quote"]["02. open"]')
  local high_price=$(echo "$price_data" | jq -r '.["Global Quote"]["03. high"]')
  local low_price=$(echo "$price_data" | jq -r '.["Global Quote"]["04. low"]')
  local volume=$(echo "$price_data" | jq -r '.["Global Quote"]["06. volume"]')
  local change=$(echo "$price_data" | jq -r '.["Global Quote"]["09. change"]')
  local change_percent=$(echo "$price_data" | jq -r '.["Global Quote"]["10. change percent"]' | sed 's/%//')

  echo "当前价格: \$${current_price}"
  echo "开盘价: \$${open_price}"
  echo "日内最高: \$${high_price}"
  echo "日内最低: \$${low_price}"
  echo "交易量: $(echo "scale=0; $volume / 1000000" | bc)M"
  echo "涨跌: \$${change} (${change_percent}%)"

  # 获取 RSI
  local rsi="50.0"
  local rsi_data=$(get_rsi "$symbol" "$api_key" "daily" "14")

  if ! echo "$rsi_data" | grep -q "error" && echo "$rsi_data" | jq -e '.["Technical Analysis: RSI"]' > /dev/null 2>&1; then
    rsi=$(echo "$rsi_data" | jq -r '.["Technical Analysis: RSI"] | to_entries[0].value["RSI"] // "50.0"')
  else
    rsi="50.0"
  fi

  echo "RSI(14): $rsi"

  # 计算评分和信号
  local score=50
  local signals=()
  local signal=" hodl "

  # RSI 信号
  local rsi_num=$(echo "$rsi" | awk '{printf "%.0f", $1}')
  if [ "$rsi_num" -le 30 ]; then
    score=$((score + 15))
    signals+=("RSI超卖: $rsi")
    [ "$signal" = " hodl " ] && signal="buy"
  elif [ "$rsi_num" -ge 70 ]; then
    score=$((score - 15))
    signals+=("RSI超买: $rsi")
    [ "$signal" = " hodl " ] && signal="sell"
  fi

  # 价格变化信号
  local change_num=$(echo "$change_percent" | awk '{printf "%.0f", $1}')
  if [ "$change_num" -le -5 ]; then
    score=$((score + 10))
    signals+=("单日下跌${change_num}%")
    [ "$signal" = " hodl " ] && signal="buy"
  elif [ "$change_num" -ge 5 ]; then
    score=$((score - 10))
    signals+=("单日上涨${change_num}%")
    [ "$signal" = " hodl " ] && signal="sell"
  fi

  # 高低差分析
  local range=$(echo "scale=2; ($high_price - $low_price) / $open_price * 100" | bc)
  if [ $(echo "$range > 3" | bc) -eq 1 ]; then
    signals+=("日内波动大: ${range}%")
  fi

  # 限制分数范围
  [ $score -lt 0 ] && score=0
  [ $score -gt 100 ] && score=100

  # 生成 JSON
  local signals_json="[]"
  [ ${#signals[@]} -gt 0 ] && signals_json=$(printf '%s\n' "${signals[@]}" | jq -R . | jq -s .)

  local json_output=$(cat <<EOF
{
  "symbol": "$symbol",
  "name": "$name",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "price": {
    "current": $current_price,
    "open": $open_price,
    "high": $high_price,
    "low": $low_price,
    "change": $change,
    "change_percent": $change_percent,
    "volume": $(printf "%.0f" $volume)
  },
  "indicators": {
    "rsi": $(printf "%.2f" $rsi),
    "daily_range": $(printf "%.2f" $range)
  },
  "analysis": {
    "score": $score,
    "signal": "$signal",
    "signals": $signals_json
  }
}
EOF
  )

  echo ""
  echo "📊 评分: $score/100 | 信号: $signal"
  [ ${#signals[@]} -gt 0 ] && printf '%s\n' "${signals[@]}" | sed 's/^/🚨 /' | sed 's/^/   /'
  echo ""
}

# 函数：生成多股票摘要
function generate_multi_stock_summary() {
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local stocks_array=()
  local total_score=0
  local stock_count=0

  echo "=== 美股监控摘要 ==="
  echo "时间: $timestamp"
  echo ""

  for stock_pair in "${STOCKS[@]}"; do
    local symbol="${stock_pair%%:*}"
    local name="${stock_pair##*:}"

    generate_stock_report "$symbol" "$name" "$AV_API_KEY"

    local report=$(generate_stock_report "$symbol" "$name" "$AV_API_KEY" 2>/dev/null)
    if [ $? -eq 0 ]; then
      stocks_array+=("$report")
      stock_count=$((stock_count + 1))
      local score=$(echo "$report" | jq -r '.analysis.score')
      total_score=$((total_score + score))
    fi
  done

  # 综合分析
  local avg_score=0
  [ $stock_count -gt 0 ] && avg_score=$((total_score / stock_count))

  local overall_signal="hodl"
  [ $avg_score -ge 70 ] && overall_signal="strong buy"
  [ $avg_score -ge 60 ] && overall_signal="buy"
  [ $avg_score -le 30 ] && overall_signal="strong sell"
  [ $avg_score -le 40 ] && overall_signal="sell"

  local all_stocks_json=$(printf '%s\n' "${stocks_array[@]}" | jq -s . 2>/dev/null || echo "[]")

  local final_json=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "summary": {
    "avg_score": $avg_score,
    "overall_signal": "$overall_signal",
    "stocks_monitored": $stock_count
  },
  "stocks": $all_stocks_json
}
EOF
  )

  local output_file="$OUTPUT_DIR/stocks-monitor-$(date +%Y%m%d-%H%M%S).json"
  echo "$final_json" | jq '.' > "$output_file"
  echo "✅ 报告已保存: $output_file"

  echo "$final_json" | jq '.' > "$OUTPUT_DIR/stocks-monitor-latest.json"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━"
  echo "📈 综合评分: $avg_score/100"
  echo "🎯 综合信号: $overall_signal"
  echo "━━━━━━━━━━━━━━━━━━"

  echo "$final_json" | jq '.'
}

# 主函数
function main() {
  case "${1:-all}" in
    "all")
      generate_multi_stock_summary
      ;;
    "single")
      [ -z "$2" ] && { echo "用法: $0 single <symbol> <name>"; exit 1; }
      generate_stock_report "$2" "$3" "$AV_API_KEY"
      ;;
    *)
      echo "用法: $0 [all|single] [symbol] [name]"
      exit 1
      ;;
  esac
}

main "$@"
