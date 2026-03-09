#!/bin/bash
# 加密资产智能监控 (CoinGecko API 集成) - 修复版
# 支持 BTC, ETH 等资产，实时价格、RSI、MVRV 等指标

set -e

# 加载 API 模块
source "$(dirname "$0")/coingecko-api.sh"

# 配置
ASSETS=(
  "bitcoin:BTC"
  "ethereum:ETH"
  "solana:SOL"
)
OUTPUT_DIR="/root/.openclaw/workspace/skills/investment-framework/data"
mkdir -p "$OUTPUT_DIR"

# 函数：生成资产报告 JSON（只输出 JSON 到 stdout）
function generate_asset_report_json() {
  local coin_id=$1
  local symbol=$2

  # 获取当前价格
  local price_data=$(get_price "$coin_id" "usd")
  local current_price=$(echo "$price_data" | jq -r ".\"$coin_id\".usd // null")
  local price_change_24h=$(echo "$price_data" | jq -r ".\"$coin_id\".usd_24h_change // null")
  local total_volume=$(echo "$price_data" | jq -r ".\"$coin_id\".usd_24h_vol // null")

  if [ "$current_price" = "null" ] || [ -z "$current_price" ]; then
    echo '{"error": "无法获取价格数据"}' >&2
    return 1
  fi

  # 获取历史数据（用于计算 RSI）
  local rsi="N/A"
  local history_data=$(get_market_data "$coin_id" 30)
  if [ $? -eq 0 ]; then
    rsi=$(calculate_rsi "$history_data" 14)
  fi

  # 获取市场详情（包含 ATH）
  local market_detail=$(cg_request "/coins/$coin_id?localization=false&tickers=false&community_data=false&developer_data=false" 2>/dev/null || echo "{\"market_data\":{}}")
  local ath=$(echo "$market_detail" | jq -r '.market_data.ath.usd // null')
  local ath_change=$(echo "$market_detail" | jq -r '.market_data.ath_change_percentage.usd // null')
  local market_cap=$(echo "$market_detail" | jq -r '.market_data.market_cap.usd // null')

  # 计算 MVRV 简化版
  local mvrv="null"
  if [ "$ath" != "null" ] && [ -n "$ath" ]; then
    mvrv=$(calculate_mvrv_simplified "$current_price" "$ath")
  fi

  # 获取恐慌贪婪指数
  local fg=$(get_fear_greed_index)
  local fg_value=$(echo "$fg" | jq -r '.value')
  local fg_class=$(echo "$fg" | jq -r '.classification')

  # 计算评分和信号
  local score=50
  local signals=()
  local signal="hodl"

  # RSI 信号
  if [ "$rsi" != "N/A" ]; then
    local rsi_num=$(echo "$rsi" | awk '{printf "%.0f", $1}')
    if [ "$rsi_num" -le 30 ]; then
      score=$((score + 15))
      signals+=("RSI超卖: $rsi")
      signal="buy"
    elif [ "$rsi_num" -ge 70 ]; then
      score=$((score - 15))
      signals+=("RSI超买: $rsi")
      signal="sell"
    fi
  fi

  # 24h 涨跌信号
  local change_num=$(echo "$price_change_24h" | awk '{printf "%.0f", $1}')
  if [ "$change_num" -le -10 ]; then
    score=$((score + 10))
    signals+=("暴跌${change_num}%")
    if [ "$signal" = "hodl" ]; then
      signal="buy"
    fi
  elif [ "$change_num" -ge 10 ]; then
    score=$((score - 10))
    signals+=("暴涨${change_num}%")
    if [ "$signal" = "hodl" ]; then
      signal="sell"
    fi
  fi

  # 恐慌贪婪信号
  if [ "$fg_value" -le 20 ]; then
    score=$((score + 20))
    signals+=("极度恐慌: $fg_class")
    if [ "$signal" != "sell" ]; then
      signal="buy"
    fi
  elif [ "$fg_value" -ge 80 ]; then
    score=$((score - 20))
    signals+=("极度贪婪: $fg_class")
    if [ "$signal" != "buy" ]; then
      signal="sell"
    fi
  fi

  # 限制分数范围
  if [ $score -lt 0 ]; then score=0; fi
  if [ $score -gt 100 ]; then score=100; fi

  # 生成 JSON 输出
  local signals_json="[]"
  if [ ${#signals[@]} -gt 0 ]; then
    signals_json=$(printf '%s\n' "${signals[@]}" | jq -R . | jq -s .)
  fi

  cat <<EOF
{
  "symbol": "$symbol",
  "coin_id": "$coin_id",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "price": {
    "current": $current_price,
    "change_24h": $price_change_24h,
    "volume_24h": null
  },
  "indicators": {
    "rsi": ${rsi:-null},
    "mvrv": ${mvrv:-null},
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

# 函数：显示资产报告（带文本输出）
function display_asset_report() {
  local coin_id=$1
  local symbol=$2

  # 获取 JSON 数据
  local json_data=$(generate_asset_report_json "$coin_id" "$symbol")
  if [ $? -ne 0 ]; then
    echo "❌ 无法获取 $symbol 数据"
    return 1
  fi

  # 打印文本信息
  echo "=== 分析 $symbol ==="
  local current_price=$(echo "$json_data" | jq -r '.price.current')
  local price_change=$(echo "$json_data" | jq -r '.price.change_24h')
  local rsi=$(echo "$json_data" | jq -r '.indicators.rsi')
  local ath=$(echo "$json_data" | jq -r '.indicators.ath')
  local ath_change=$(echo "$json_data" | jq -r '.indicators.ath_change')
  local mvrv=$(echo "$json_data" | jq -r '.indicators.mvrv')
  local fg_value=$(echo "$json_data" | jq -r '.indicators.fear_greed.value')
  local fg_class=$(echo "$json_data" | jq -r '.indicators.fear_greed.classification')
  local score=$(echo "$json_data" | jq -r '.analysis.score')
  local signal=$(echo "$json_data" | jq -r '.analysis.signal')
  local signals=$(echo "$json_data" | jq -r '.analysis.signals[]')

  echo "当前价格: \$${current_price}"
  echo "24h 涨跌: ${price_change}%"
  echo "RSI(14): $rsi"
  echo "ATH: \$${ath} (距离 ${ath_change}%)"
  echo "MVRV: $mvrv"
  echo "恐慌贪婪指数: $fg_value ($fg_class)"
  echo ""
  echo "📊 评分: $score/100 | 信号: $signal"
  echo "🚨 信号:"
  echo "   • 极度恐慌: $fg_class"
  echo ""

  # 输出 JSON
  echo "$json_data" | jq '.'
}

# 函数：生成多资产摘要
function generate_multi_asset_summary() {
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

    # 获取 JSON 数据（只用 stdout）
    local report_json=$(generate_asset_report_json "$coin_id" "$symbol" 2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$report_json" ]; then
      # 显示到屏幕
      display_asset_report "$coin_id" "$symbol" 2>&1 | grep -v '^{' | head -20

      assets_array+=("$report_json")
      asset_count=$((asset_count + 1))
      local score=$(echo "$report_json" | jq -r '.analysis.score')
      total_score=$((total_score + score))
    else
      echo "⚠️ 跳过 $symbol (数据获取失败)"
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
  local all_assets_json=$(printf '%s\n' "${assets_array[@]}" | jq -s .)

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
  echo "✅ 报告已保存: $output_file"

  # 同时保存最新版本
  echo "$final_json" | jq '.' > "$OUTPUT_DIR/crypto-monitor-latest.json"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━"
  echo "📈 综合评分: $avg_score/100"
  echo "🎯 综合信号: $overall_signal"
  echo "━━━━━━━━━━━━━━━━━━"

  # 输出最终 JSON
  echo "$final_json" | jq '.'
}

# 主函数
function main() {
  case "${1:-all}" in
    "all")
      generate_multi_asset_summary
      ;;
    "single")
      if [ -z "$2" ]; then
        echo "用法: $0 single <coin_id> <symbol>"
        exit 1
      fi
      display_asset_report "$2" "$3"
      ;;
    *)
      echo "用法: $0 [all|single] [coin_id] [symbol]"
      exit 1
      ;;
  esac
}

# 执行
main "$@"
