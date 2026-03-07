#!/usr/bin/env python3
import json
from pathlib import Path
import sys

accounts_file = Path("accounts.json")
if not accounts_file.exists():
    print("无账户配置")
    sys.exit(0)

with open(accounts_file) as f:
    accounts = json.load(f)

print("\n账户列表:")
print("-" * 50)
for name, info in accounts.items():
    print(f"  {name:15s} | {info['type']:10s} | 添加于: {info.get('added_at', 'N/A')[:10]}")
