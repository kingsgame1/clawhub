#!/bin/bash
# Agent Browser Skill 测试脚本

set -e

CMD="agent-browser"
PASS=0
FAIL=0
FAILED_TESTS=()

function log() {
  echo "[INFO] $1"
}

function success() {
  echo "[✅] $1"
  ((PASS++))
}

function error() {
  echo "[❌] $1"
  ((FAIL++))
  FAILED_TESTS+=("$1")
}

log "=== Agent Browser Skill 测试 ==="
echo ""

# 测试 1: 检查安装
log "检查 agent-browser 是否安装..."
if command -v $CMD &> /dev/null; then
  VERSION=$($CMD --version 2>&1 | grep -oP '[\d.]+')
  success "agent-browser 已安装 (v${VERSION})"
else
  error "agent-browser 未安装"
  exit 1
fi

# 测试 2: 检查帮助命令
log "检查帮助命令..."
if $CMD --help &> /dev/null; then
  success "help 命令可用"
else
  error "help 命令失败"
fi

# 测试 3: 检查快照命令（无需浏览器）
log "检查快照命令（无浏览器）..."
OUTPUT=$($CMD snapshot 2>&1)
if echo "$OUTPUT" | grep -q "document"; then
  success "snapshot 命令可用"
else
  error "snapshot 命令异常"
fi

# 测试 4: 测试打开网页（需要 Chromium）
log "测试打开网页..."
if $CMD open https://httpbin.org &> /dev/null; then
  # 等待加载
  sleep 2

  # 测试 5: 获取标题
  log "获取页面标题..."
  TITLE=$($CMD get title 2>&1)
  if [[ -n "$TITLE" ]]; then
    success "get title 工作正常: '$TITLE'"
  else
    error "get title 失败"
  fi

  # 测试 6: 获取 URL
  log "获取页面 URL..."
  URL=$($CMD get url 2>&1)
  if echo "$URL" | grep -q "httpbin"; then
    success "get url 工作正常"
  else
    error "get url 失败"
  fi

  # 测试 7: 等待网络空闲
  log "等待网络空闲..."
  if $CMD wait --load networkidle &> /dev/null; then
    success "wait --load networkidle 工作正常"
  else
    error "wait --load networkidle 失败"
  fi

  # 测试 8: 查找元素（语义定位）
  log "测试语义定位器..."
  if $CMD find role heading text &> /dev/null; then
    success "find role heading 工作正常"
  else
    error "find role heading 失败"
  fi

  # 测试 9: 快照
  log "测试快照..."
  SNAPSHOT=$($CMD snapshot 2>&1)
  if echo "$SNAPSHOT" | grep -q "document\|heading\|link"; then
    success "snapshot 返回了有效数据"
  else
    error "snapshot 数据异常"
  fi

  # 测试 10: 截图
  log "测试截图..."
  TEMP_DIR="/tmp/agent-browser-test"
  mkdir -p "$TEMP_DIR"
  SCREENSHOT="$TEMP_DIR/test.png"
  if $CMD screenshot "$SCREENSHOT" &> /dev/null; then
    if [ -f "$SCREENSHOT" ]; then
      SIZE=$(stat -f%z "$SCREENSHOT" 2>/dev/null || stat -c%s "$SCREENSHOT" 2>/dev/null)
      if [ "$SIZE" -gt 1000 ]; then
        success "截图生成成功 (${SIZE} 字节)"
        rm -f "$SCREENSHOT"
      else
        error "截图文件过小 (${SIZE} 字节)"
      fi
    else
      error "截图文件不存在"
    fi
  else
    error "screenshot 命令失败"
  fi

  # 测试 11: JavaScript 执行
  log "测试 JavaScript 执行..."
  JS_RESULT=$($CMD eval "document.title" 2>&1)
  if [[ -n "$JS_RESULT" ]]; then
    success "eval 命令工作正常"
  else
    error "eval 命令失败"
  fi

  # 测试 12: 关闭浏览器
  log "关闭浏览器..."
  if $CMD close &> /dev/null; then
    success "close 命令工作正常"
  else
    error "close 命令失败"
  fi

else
  error "无法打开网页（可能未下载 Chromium）"
  log "运行 'agent-browser install' 来下载 Chromium"
fi

# 清理
rm -rf "$TEMP_DIR"

# 汇总结果
echo ""
log "=== 测试结果汇总 ==="
echo "✅ 通过: $PASS"
echo "❌ 失败: $FAIL"
echo ""

if [ $FAIL -gt 0 ]; then
  log "失败的测试:"
  for test in "${FAILED_TESTS[@]}"; do
    echo "  - $test"
  done
  exit 1
else
  log "🎉 所有测试通过！"
  exit 0
fi
