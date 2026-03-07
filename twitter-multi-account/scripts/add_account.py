#!/usr/bin/env python3
"""
添加 Twitter 账户到管理系统
"""

import argparse
import json
from pathlib import Path


def add_account(name, session_file, api_key=None, api_secret=None, account_type="cookie"):
    """添加账户"""
    accounts_file = Path("accounts.json")

    # 加载现有账户
    accounts = {}
    if accounts_file.exists():
        with open(accounts_file) as f:
            accounts = json.load(f)

    # 构建账户配置
    account = {
        "name": name,
        "type": account_type,
        "added_at": "2026-03-07T00:00:00Z"
    }

    if account_type == "cookie":
        account["session_file"] = session_file
    elif account_type == "api":
        account["api_key"] = api_key
        account["api_secret"] = api_secret

    accounts[name] = account

    # 保存
    with open(accounts_file, "w") as f:
        json.dump(accounts, f, indent=2)

    print(f"✓ 账户 '{name}' 已添加")
    print(f"  类型: {account_type}")

    return accounts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="添加 Twitter 账户")
    parser.add_argument("--name", required=True, help="账户名称")
    parser.add_argument("--session-file", help="Session 文件路径（Cookie 方式）")
    parser.add_argument("--api-key", help="API Key（API 方式）")
    parser.add_argument("--api-secret", help="API Secret（API 方式）")
    parser.add_argument("--type", default="cookie", choices=["cookie", "api"], help="账户类型")

    args = parser.parse_args()

    add_account(
        name=args.name,
        session_file=args.session_file,
        api_key=args.api_key,
        api_secret=args.api_secret,
        account_type=args.type
    )
