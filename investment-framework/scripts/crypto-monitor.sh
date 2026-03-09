#!/bin/bash
# 加密资产智能监控 (CoinGecko API 集成) - 稳健版 v4
# 支持 BTC, ETH 等资产，实时价格、RSI、MVRV 等指标

set -e

# 加载 API 模块
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/coingecko-api.sh"

# 配置
ASSETS=(
  "bitcoin:BTC"
  "ethereum:ETH"
  "solana:SOL"
)
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"

# 函数：生成资产报告 JSON（只输出 JSON 到 stdout）
function generate_asset_json() {
  local coin_id=$1
  local symbol=$2

  # 获取当前价格
  local price_data=$(get_price "$coin_id" "usd")
  local current_price=$(echo "$price_data" | jq -r ".\"$coin_id\".usd // null")
  local price_change_24h=$(echo "$price_data" | jq -r ".\"$coin_id\".usd_24h_change // null")

  if [ "$current_price" = "null" ] || [ -z "$current_price" ]; then
    return 1
  fi

  # 获取历史数据（用于计算 RSI）
  local rsi="null"
  local history_data=$(get_market_data "$coin_id" 30 2>/dev/null || true)
  if [ -n "$history_data" ]; then
    rsi=$(calculate_rsi "$history_data" 14 2>/dev/null || echo "null")
  fi

  # 获取市场详情（包含 ATH）
  local market_detail=$(cg_request "/coins/$coin_id?localization=false&tickers=false&community_data=false&developer_data=false" 2>/dev/null || echo "{\"market_data\":{}}")
  local ath=$(echo "$market_detail" | jq -r '.market_data.ath.usd // null')
  local ath_change=$(echo "$market_detail" | jq -r '.market_data.ath_change_percentage.usd // null')
  local market_cap=$(echo "$market_detail" | jq -r '.market_data.market_cap.usd // null')

  # 计算 MVRV 简化版
  local mvrv="null"
  if [ "$ath" != "null" ] && [ -n "$ath" ]; then
    mvrv=$(calculate_mvrv_simplified "$current_price" "$ath" 2>/dev/null || echo "null")
  fi

  # 获取恐慌贪婪指数
  local fg=$(get_fear_greed_index 2>/dev/null || echo '{"value":50,"classification":"Neutral"}')
  local fg_value=$(echo "$fg" | jq -r '.value')
  local fg_class=$(echo "$fg" | jq -r '.classification')

  # 计算评分和信号
  local score=50
  local signal="hodl"

  # RSI 信号
  if [ "$rsi" != "null" ]; then
    local rsi_num=$(echo "$rsi" | awk '{printf "%.0f", $1}')
    if [ "$rsi_num" -le 30 ]; then
      score=$((score + 15))
      signal="buy"
    elif [ "$rsi_num" -ge 70 ]; then
      score=$((score - 15))
      signal="sell"
    fi
  fi

  # 24h 涨跌信号
  local change_num=$(echo "$price_change_24h" | awk '{printf "%.0f", $1}')
  if [ "$change_num" -le -10 ]; then
    score=$((score + 10))
    if [ "$signal" = "hodl" ]; then
      signal="buy"
    fi
  elif [ "$change_num" -ge 10 ]; then
    score=$((score - 10))
    if [ "$signal" = "hodl" ]; then
      signal="sell"
    fi
  fi

  # 恐慌贪婪信号
  local fg_num=$(echo "$fg_value" | awk '{printf "%.0f", $1}')
  if [ "$fg_num" -le 20 ]; then
    score=$((score + 20))
    if [ "$signal" != "sell" ]; then
      signal="buy"
    fi
  elif [ "$fg_num" -ge 80 ]; then
    score=$((score - 20))
    if [ "$signal" != "buy" ]; then
      signal="sell"
    fi
  fi

  # 限制分数范围
  if [ $score -lt 0 ]; then score=0; fi
  if [ $score -gt 100 ]; then score=100; fi

  # 生成 signals 数组
  local signals_json="[]"
  if [ "$rsi" != "null" ] && [ "$sig_num" -le 30 ]; then
    signals_json=$(echo "$signals_json" | jq --arg v "RSI超卖: $rsi" '. + [$v]')
  fi
  if [ "$fg_num" -le 20 ]; then
    signals_json=$(echo "$signals_json" | jq --arg v "极度恐慌: $fg_class" '. + [$v]')
  fi

  # 输出 JSON
  cat <<EOF
{
  "symbol": "$symbol",
  "coin_id": "$coin_id",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "price": {
    "current": $current_price,
    "change_24h": $price_change_24h
  },
  "indicators": {
    "rsi": $rsi,
    "mvrv": $mvrv,
    "fear_greed": {
      "value": $fg_value,
      "classification": "$fg_class"
    },
    "ath": $ath,
    "ath_change": $ath_change,
    "market_cap": $market_cap
  },
  "analysis": {
    "score": $score,
    "signal": "$signal",
    "signals": $signals_json
  }
}
EOF
}

# 函数：显示资产信息
function display_asset_info() {
  local json=$1
  local symbol=$(echo "$json" | jq -r '.symbol')
  local price=$(echo "$json" | jq -r '.price.current')
  local change=$(echo "$json" | jq -r '.price.change_24h')
  local rsi=$(echo "$json" | jq -r '.indicators.rsi')
  local mvrv=$(echo "$json" | jq -r '.indicators.mvrv')
  local fg_class=$(echo "$json" | jq -r '.indicators.fear_greed.classification')
  local score=$(echo "$json" | jq -r '.analysis.score')
  local signal=$(echo "$json" | jq -r '.analysis.signal')

  echo "=== 分析 $symbol ==="
  echo "当前价格: \$${price}"
  echo "24h 涨跌: ${change}%"
  echo "RSI(14): $rsi"
  echo "MVRV: $mvrv"
  echo "恐慌贪婪指数: $fg_class"
  echo ""
  echo "📊 评分: $score/100 | 信号: $signal"
  echo ""
}

# 函数：生成多资产摘要
function generate_multi_summary() {
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local assets_array=()
  local total_score=0
  local asset_count=0

  echo "=== 多资产监控摘要 ==="
  echo "时间: $timestamp"
  echo ""

  for asset_pair in "${ASSETS[@]}"; do
    local coin_id="${asset_pair%%:*}"
    local symbol="${asset_pair##*:}"

    # 获取 JSON （输出到 stdout）
    echo -en "获取 $symbol 数据..." >&2
    local asset_json=$(generate_asset_json "$coin_id" "$symbol" 2>/dev/null)

    if [ -n "$asset_json" ] && [ $? -eq 0 ]; then
      # 验证 JSON 是否有效
      if echo "$asset_json" | jq -e . >/dev/null 2>&1; then
        echo " ✓" >&2
        # 显示信息
        display_asset_info "$asset_json" >&2

        assets_array+=("$asset_json")
        asset_count=$((asset_count + 1))
        total_score=$((total_score + $(echo "$asset_json" | jq -r '.analysis.score')))
      else
        echo " ✗ (无效JSON)" >&2
      fi
    else
      echo " ✗ (API错误)" >&2
    fi
  done

  # 计算平均分数
  local avg_score=0
  if [ $asset_count -gt 0 ]; then
    avg_score=$((total_score / asset_count))
  fi

  # 生成综合信号
  local overall_signal="hodl"
  if [ $avg_score -ge 70 ]; then
    overall_signal="strong buy"
  elif [ $avg_score -ge 60 ]; then
    overall_signal="buy"
  elif [ $avg_score -le 30 ]; then
    overall_signal="strong sell"
  elif [ $avg_score -le 40 ]; then
    overall_signal="sell"
  fi

  # 生成最终 JSON
  local all_assets_json="[]"
  if [ ${#assets_array[@]} -gt 0 ]; then
    all_assets_json=$(printf '%s\n' "${assets_array[@]}" | jq -s .)
  fi

  local final_json=$(cat <<EOF
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

  # 保存到文件
  local output_file="$OUTPUT_DIR/crypto-monitor-$(date +%Y%m%d-%H%M%S).json"
  echo "$final_json" | jq '.' > "$output_file"
  echo "✅ 报告已保存: $output_file" >&2

  # 同时保存最新版本
  echo "$final_json" | jq '.' > "$OUTPUT_DIR/crypto-monitor-latest.json"

  echo "" >&2
  echo "━━━━━━━━━━━━━━━━━━" >&2
  echo "📈 综合评分: $avg_score/100" >&2
  echo "🎯 综合信号: $overall_signal" >&2
  echo "━━━━━━━━━━━━━━━━━━" >&2

  # 输出最终 JSON 到 stdout
  echo "$final_json"
}

# 主函数
function main() {
  case "${1:-all}" in
    "all")
      generate_multi_summary
      ;;
    "single")
      if [ -z "$2" ]; then
        echo "用法: $0 single <coin_id> <symbol>" >&2
        exit 1
      fi
      local json=$(generate_asset_json "$2" "$3")
      if [ -n "$json" ]; then
        echo "$json" | jq '.'
      fi
      ;;
    *)
      echo "用法: $0 [all|single] [coin_id] [symbol]" >&2
      exit 1
      ;;
  esac
}

# 执行
main "$@"
