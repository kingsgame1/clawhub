#!/bin/bash
# Jina Reader 封装脚本
# 用法: ./fetch.sh <URL>

URL="$1"

if [ -z "$URL" ]; then
    echo "Usage: $0 <URL>" >&2
    echo "Example: $0 https://example.com" >&2
    exit 1
fi

# 移除 URL 中可能的空格
URL=$(echo "$URL" | tr -d ' ')

# 调用 Jina Reader API
curl -s -L "https://r.jina.ai/$URL"
