#!/bin/bash
# Agent Browser 封装脚本 - OpenClaw Skill
# 用途：简化浏览器自动化操作

set -e

CMD="agent-browser"

function show_help() {
  cat << _EOF
Agent Browser 封装脚本

用法: $0 <action> [options]

操作:
  open <url>                 - 打开网页
  snapshot                   - 获取可访问性树快照
  click <selector>           - 点击元素
  fill <selector> <text>     - 填充表单
  type <selector> <text>     - 输入文本
  screenshot [path]          - 截图
  pdf <path>                 - 导出 PDF
  find <role> <action>       - 语义定位
  wait <condition>           - 等待条件
  eval <js>                  - 执行 JavaScript
  close                      - 关闭浏览器

示例:
  $0 open https://example.com
  $0 fill "#email" "user@example.com"
  $0 click "#submit"
  $0 screenshot page.png
  $0 close

更多信息见: SKILL.md
_EOF
}

function check_installed() {
  if ! command -v agent-browser &> /dev/null; then
    echo "❌ agent-browser 未安装"
    echo "运行: npm install -g agent-browser"
    echo "然后: agent-browser install"
    exit 1
  fi
}

# 主逻辑
if [ $# -eq 0 ]; then
  show_help
  exit 0
fi

ACTION="$1"
shift || true

check_installed

case "$ACTION" in
  open)
    if [ -z "$1" ]; then
      echo "❌ 需要指定 URL"
      exit 1
    fi
    $CMD open "$1"
    ;;

  snapshot)
    $CMD snapshot
    ;;

  click)
    if [ -z "$1" ]; then
      echo "❌ 需要指定选择器"
      exit 1
    fi
    $CMD click "$1"
    ;;

  fill)
    if [ -z "$1" ] || [ -z "$2" ]; then
      echo "❌ 需要指定选择器和文本"
      exit 1
    fi
    $CMD fill "$1" "$2"
    ;;

  type)
    if [ -z "$1" ] || [ -z "$2" ]; then
      echo "❌ 需要指定选择器和文本"
      exit 1
    fi
    $CMD type "$1" "$2"
    ;;

  screenshot)
    $CMD screenshot "$1"
    ;;

  pdf)
    if [ -z "$1" ]; then
      echo "❌ 需要指定输出路径"
      exit 1
    fi
    $CMD pdf "$1"
    ;;

  find)
    if [ -z "$1" ] || [ -z "$2" ]; then
      echo "❌ 需要指定定位器和操作"
      exit 1
    fi
    $CMD find "$@"
    ;;

  wait)
    if [ -z "$1" ]; then
      echo "❌ 需要指定等待条件"
      exit 1
    fi
    $CMD wait "$@"
    ;;

  eval)
    if [ -z "$1" ]; then
      echo "❌ 需要指定 JavaScript 代码"
      exit 1
    fi
    $CMD eval "$1"
    ;;

  close)
    $CMD close
    ;;

  install)
    echo "📦 安装 agent-browser..."
    npm install -g agent-browser
    echo "📥 下载 Chromium..."
    agent-browser install
    echo "✅ 安装完成！"
    ;;

  *)
    echo "❌ 未知操作: $ACTION"
    show_help
    exit 1
    ;;
esac
