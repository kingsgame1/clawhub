#!/bin/bash
# CoinGecko API 集成模块
# 免费 API，无需密钥

set -e

# CoinGecko API 基础 URL
CG_API_BASE="https://api.coingecko.com/api/v3"

# 请求间隔（秒，避免超限）
REQUEST_INTERVAL=7

# 缓存目录
CACHE_DIR="/root/.openclaw/workspace/skills/investment-framework/cache"
mkdir -p "$CACHE_DIR"

# 函数：带缓存的 API 请求
function cg_request() {
  local endpoint=$1
  local cache_file="$CACHE_DIR/$(echo $endpoint | sed 's|/|_|g').json"
  local cache_ttl=300  # 5分钟缓存

  # 检查缓存
  if [ -f "$cache_file" ]; then
    local cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file")))
    if [ $cache_age -lt $cache_ttl ]; then
      # 使用缓存
      cat "$cache_file"
      return 0
    fi
  fi

  # 发送请求
  echo "🔄 请求 CoinGecko API: $endpoint" >&2
  local response=$(curl -s --fail "$CG_API_BASE$endpoint")

  if [ $? -ne 0 ]; then
    echo "❌ API 请求失败: $endpoint" >&2
    # 尝试使用缓存（如果存在）
    if [ -f "$cache_file" ]; then
      echo "⚠️  使用过期缓存数据" >&2
      cat "$cache_file"
      return 0
    fi
    return 1
  fi

  # 保存到缓存
  echo "$response" > "$cache_file"

  # 输出响应
  echo "$response"

  # 请求间隔
  sleep $REQUEST_INTERVAL
}

# 函数：获取市场价格
function get_price() {
  local coin_id=$1
  local currency=${2:-usd}
  local data=$(cg_request "/simple/price?ids=$coin_id&vs_currencies=$currency&include_24hr_change=true&include_24hr_vol=true")
  echo "$data"
}

# 函数：获取市场历史数据（用于回测）
function get_market_chart() {
  local coin_id=$1
  local currency=${2:-usd}
  local days=${3:-30}
  local data=$(cg_request "/coins/$coin_id/market_chart?vs_currency=$currency&days=$days")
  echo "$data"
}

# 函数：获取市场详情（RSI、MVRV 等指标）
function get_market_data() {
  local coin_id=$1
  local days=${2:-1}
  local data=$(cg_request "/coins/$coin_id/market_chart?vs_currency=usd&days=$days&interval=daily")
  echo "$data"
}

# 函数：计算 RSI（相对强弱指标）
function calculate_rsi() {
  local prices_json=$1
  local period=${2:-14}

  # 提取价格数组
  local prices=$(echo "$prices_json" | jq -r '.prices[][1]')

  # 计算价格变化
  local changes=()
  local prev=""
  for price in $prices; do
    if [ -n "$prev" ]; then
      local change=$(echo "scale=6; $price - $prev" | bc)
      changes+=("$change")
    fi
    prev="$price"
  done

  # 计算涨跌
  local gains=()
  local losses=()
  for change in "${changes[@]}"; do
    if [ $(echo "$change > 0" | bc) -eq 1 ]; then
      gains+=("$change")
      losses+=("0")
    else
      gains+=("0")
      local loss=$(echo "scale=6; $change * -1" | bc)
      losses+=("$loss")
    fi
  done

  # 简化版 RSI 计算（使用最后 $period 个数据点）
  local recent_gains=("${gains[@]: -$period}")
  local recent_losses=("${losses[@]: -$period}")

  local avg_gain=0
  local avg_loss=0
  for i in "${!recent_gains[@]}"; do
    avg_gain=$(echo "scale=6; $avg_gain + ${recent_gains[$i]}" | bc)
    avg_loss=$(echo "scale=6; $avg_loss + ${recent_losses[$i]}" | bc)
  done

  avg_gain=$(echo "scale=6; $avg_gain / $period" | bc)
  avg_loss=$(echo "scale=6; $avg_loss / $period" | bc)

  if [ $(echo "$avg_loss == 0" | bc) -eq 1 ]; then
    echo "100.00"
  else
    local rs=$(echo "scale=2; $avg_gain / $avg_loss" | bc)
    local rsi=$(echo "scale=2; 100 - (100 / (1 + $rs))" | bc)
    echo "$rsi"
  fi
}

# 函数：获取恐慌贪婪指数（API 可能有，但需要付费）
function get_fear_greed_index() {
  # CoinGecko 的免费 API 不直接提供
  # 使用 alternative.me 的免费 API
  local data=$(curl -s "https://api.alternative.me/fng/?limit=1" 2>/dev/null)

  if [ $? -eq 0 ]; then
    local value=$(echo "$data" | jq -r '.data[0].value // 50')
    local classification=$(echo "$data" | jq -r '.data[0].value_classification // "Neutral"')
    echo "{\"value\": $value, \"classification\": \"$classification\"}"
  else
    echo "{\"value\": 50, \"classification\": \"Neutral (API Unavailable)\"}"
  fi
}

# 函数：获取加密货币市值排名前 N
function get_top_coins() {
  local limit=${1:-20}
  local currency=${2:-usd}
  local data=$(cg_request "/coins/markets?vs_currency=$currency&order=market_cap_desc&per_page=$limit&page=1&sparkline=false&price_change_percentage=24h")
  echo "$data"
}

# 函数：计算 MVRV（Market Value to Realized Value）
# 注意：这需要链上数据，CoinGecko API 不直接提供
# 这里使用市值对比 ATH（历史最高价）作为简化替代
function calculate_mvrv_simplified() {
  local current_price=$1
  local ath_price=$2
  echo "scale=4; $current_price / $ath_price" | bc
}

# 导出函数供其他脚本使用
export -f cg_request
export -f get_price
export -f get_market_chart
export -f get_market_data
export -f calculate_rsi
export -f get_fear_greed_index
export -f get_top_coins
export -f calculate_mvrv_simplified

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "=== CoinGecko API 测试 ==="

  echo ""
  echo "1. 测试获取 BTC 价格:"
  btc_price=$(get_price "bitcoin" "usd")
  echo "$btc_price" | jq '.'

  echo ""
  echo "2. 测试获取恐慌贪婪指数:"
  fg=$(get_fear_greed_index)
  echo "$fg" | jq '.'

  echo ""
  echo "3. 测试获取市值前 5:"
  top5=$(get_top_coins 5)
  echo "$top5" | jq -r '.[].symbol | ascii_upcase' | head -5

  echo ""
  echo "✅ API 测试完成"
fi
