#!/usr/bin/env python3
"""
Docker ヘルスチェック用スクリプト
"""

import os
import sys
import time
import logging
from pathlib import Path

def check_health():
    """アプリケーションの健全性をチェック"""
    try:
        # 1. データディレクトリの存在確認
        data_dir = Path("/app/data")
        if not data_dir.exists():
            print("❌ Data directory does not exist")
            return False
        
        # 2. 設定ファイルの存在確認
        env_file = Path("/app/.env")
        if not env_file.exists():
            print("❌ .env file does not exist")
            return False
        
        # 3. プロセス健全性の簡易チェック
        # アプリケーションログの最終更新時間をチェック
        log_file = Path("/app/logs/app.log")
        if log_file.exists():
            # ログファイルが30分以内に更新されているかチェック
            last_modified = log_file.stat().st_mtime
            current_time = time.time()
            if current_time - last_modified > 1800:  # 30分
                print("⚠️  Log file not updated recently")
                # ただし、これだけでは失敗とはしない
        
        # 4. LLMシミュレーターパスの確認
        simulator_path = Path("/mnt/bigdata/00_students/mattsun_ucl/workspace/forex/llm_forex_simulator")
        if not simulator_path.exists():
            print("⚠️  LLM Simulator path not accessible (may be expected in container)")
        
        print("✅ Health check passed")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
