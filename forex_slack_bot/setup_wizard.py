#!/usr/bin/env python3
"""
Slack Bot 設定支援スクリプト
対話形式で.envファイルを作成します
"""

import os
import re
from pathlib import Path

def print_header():
    """ヘッダーを表示"""
    print("=" * 60)
    print("🤖 Forex Trading Slack Bot 設定ウィザード")
    print("=" * 60)
    print()
    print("このスクリプトでは、Slack Botの設定を対話形式で行います。")
    print("事前にSlack APIサイトでアプリを作成し、必要なトークンを取得してください。")
    print()
    print("📖 詳細な手順は SLACK_SETUP_GUIDE.md を参照してください。")
    print()

def validate_token(token, expected_prefix):
    """トークンの形式を検証"""
    if not token or not token.startswith(expected_prefix):
        return False
    return True

def get_user_input(prompt, validator=None, required=True, default=None):
    """ユーザー入力を取得"""
    while True:
        if default:
            user_input = input(f"{prompt} [デフォルト: {default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not required and not user_input:
            return ""
        
        if not user_input and required:
            print("❌ この項目は必須です。入力してください。")
            continue
            
        if validator and not validator(user_input):
            print("❌ 入力形式が正しくありません。再度入力してください。")
            continue
            
        return user_input

def collect_slack_tokens():
    """Slackトークンを収集"""
    print("🔑 Slackトークンの設定")
    print("-" * 30)
    
    tokens = {}
    
    # Bot Token
    print("\n1. Bot User OAuth Token (OAuth & Permissions から取得)")
    print("   形式: xoxb-で始まる長いトークン")
    tokens['SLACK_BOT_TOKEN'] = get_user_input(
        "Bot Token",
        validator=lambda x: validate_token(x, 'xoxb-')
    )
    
    # Signing Secret
    print("\n2. Signing Secret (Basic Information から取得)")
    print("   形式: 32文字の英数字")
    tokens['SLACK_SIGNING_SECRET'] = get_user_input(
        "Signing Secret",
        validator=lambda x: len(x) >= 30
    )
    
    # App Token
    print("\n3. App-Level Token (Socket Mode から取得)")
    print("   形式: xapp-で始まる長いトークン")
    tokens['SLACK_APP_TOKEN'] = get_user_input(
        "App Token",
        validator=lambda x: validate_token(x, 'xapp-')
    )
    
    return tokens

def collect_channel_settings():
    """チャンネル設定を収集"""
    print("\n📢 チャンネル設定")
    print("-" * 20)
    
    channels = {}
    
    channels['DEFAULT_CHANNEL'] = get_user_input(
        "メイン通知チャンネル（推論結果が投稿される）",
        validator=lambda x: x.startswith('#'),
        default="#forex-trading"
    )
    
    channels['ADMIN_CHANNEL'] = get_user_input(
        "管理者通知チャンネル（エラーが投稿される）",
        validator=lambda x: x.startswith('#'),
        default="#admin"
    )
    
    return channels

def collect_admin_settings():
    """管理者設定を収集"""
    print("\n👑 管理者設定")
    print("-" * 15)
    
    print("管理者のユーザーIDを入力してください（複数の場合はカンマ区切り）")
    print("ユーザーIDの確認方法: Slackでプロフィール → その他 → メンバーIDをコピー")
    
    admin_ids = get_user_input(
        "管理者ユーザーID (例: U1234567890,U0987654321)",
        validator=lambda x: all(uid.strip().startswith('U') for uid in x.split(',')),
        required=False,
        default="U1234567890"
    )
    
    return {'ADMIN_USER_IDS': admin_ids}

def collect_system_settings():
    """システム設定を収集"""
    print("\n⚙️ システム設定")
    print("-" * 15)
    
    settings = {}
    
    # 定期推論設定
    periodic_enabled = get_user_input(
        "定期推論を有効にしますか？ (y/n)",
        validator=lambda x: x.lower() in ['y', 'n', 'yes', 'no'],
        default="y"
    )
    
    settings['PERIODIC_INFERENCE_ENABLED'] = 'true' if periodic_enabled.lower() in ['y', 'yes'] else 'false'
    
    if settings['PERIODIC_INFERENCE_ENABLED'] == 'true':
        settings['PERIODIC_INFERENCE_INTERVAL_HOURS'] = get_user_input(
            "実行間隔（時間）",
            validator=lambda x: x.isdigit() and int(x) > 0,
            default="1"
        )
    else:
        settings['PERIODIC_INFERENCE_INTERVAL_HOURS'] = "1"
    
    # 初期残高設定
    settings['INITIAL_BALANCE_JPY'] = get_user_input(
        "初期残高（円）",
        validator=lambda x: x.replace('.', '').isdigit(),
        default="1000000.0"
    )
    
    return settings

def generate_env_file(tokens, channels, admin_settings, system_settings):
    """環境ファイルを生成"""
    env_content = f"""# Slack Bot Configuration - 自動生成ファイル
# Generated by Slack Bot Setup Wizard

# ==========================================
# Slack API トークン（必須）
# ==========================================
SLACK_BOT_TOKEN={tokens['SLACK_BOT_TOKEN']}
SLACK_SIGNING_SECRET={tokens['SLACK_SIGNING_SECRET']}
SLACK_APP_TOKEN={tokens['SLACK_APP_TOKEN']}

# ==========================================
# チャンネル設定
# ==========================================
DEFAULT_CHANNEL={channels['DEFAULT_CHANNEL']}
ADMIN_CHANNEL={channels['ADMIN_CHANNEL']}

# ==========================================
# データファイル設定
# ==========================================
DATA_DIR=./data

# ==========================================
# 推論モデル設定
# ==========================================
MODEL_PATH=./models
GPU_MEMORY_LIMIT_GB=8
INFERENCE_TIMEOUT_SECONDS=300

# ==========================================
# 定期推論設定
# ==========================================
PERIODIC_INFERENCE_ENABLED={system_settings['PERIODIC_INFERENCE_ENABLED']}
PERIODIC_INFERENCE_INTERVAL_HOURS={system_settings['PERIODIC_INFERENCE_INTERVAL_HOURS']}

# ==========================================
# レートAPI設定（オプション）
# ==========================================
RATE_API_URL=https://api.example.com/forex
RATE_API_KEY=your-rate-api-key-here

# ==========================================
# 取引設定
# ==========================================
INITIAL_BALANCE_JPY={system_settings['INITIAL_BALANCE_JPY']}

# ==========================================
# セキュリティ設定
# ==========================================
ADMIN_USER_IDS={admin_settings['ADMIN_USER_IDS']}

# ==========================================
# LLM Forex Simulator設定
# ==========================================
LLM_SIMULATOR_PATH=/llm_forex_simulator
LLM_SIMULATOR_PATH_HOST=/mnt/bigdata/00_students/mattsun_ucl/workspace/forex/llm_forex_simulator

# ==========================================
# Docker設定
# ==========================================
DOCKER_DATA_DIR=./data
DOCKER_LOGS_DIR=./logs
"""
    
    return env_content

def backup_existing_env():
    """既存の.envファイルをバックアップ"""
    env_file = Path('.env')
    if env_file.exists():
        backup_file = Path('.env.backup')
        counter = 1
        while backup_file.exists():
            backup_file = Path(f'.env.backup.{counter}')
            counter += 1
        
        env_file.rename(backup_file)
        print(f"✅ 既存の.envファイルを {backup_file} にバックアップしました")

def main():
    """メイン処理"""
    print_header()
    
    # 既存ファイルのバックアップ確認
    if Path('.env').exists():
        overwrite = get_user_input(
            "既存の.envファイルが存在します。上書きしますか？ (y/n)",
            validator=lambda x: x.lower() in ['y', 'n', 'yes', 'no']
        )
        
        if overwrite.lower() in ['n', 'no']:
            print("設定を中止しました。")
            return
        
        backup_existing_env()
    
    try:
        # 設定情報を収集
        tokens = collect_slack_tokens()
        channels = collect_channel_settings()
        admin_settings = collect_admin_settings()
        system_settings = collect_system_settings()
        
        # 環境ファイル生成
        env_content = generate_env_file(tokens, channels, admin_settings, system_settings)
        
        # ファイルに保存
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n" + "=" * 60)
        print("🎉 設定が完了しました！")
        print("=" * 60)
        print()
        print("✅ .envファイルが作成されました")
        print("✅ 次のステップ:")
        print("   1. 必要なSlackチャンネルを作成")
        print("   2. ボットをチャンネルに招待 (/invite @botname)")
        print("   3. ボットをテスト実行")
        print()
        print("🚀 テスト実行コマンド:")
        print("   python app.py                    # 直接実行")
        print("   ./docker-manage.sh up-dev       # Docker開発環境")
        print()
        print("📖 詳細なガイドは SLACK_SETUP_GUIDE.md を参照してください")
        
    except KeyboardInterrupt:
        print("\n\n❌ 設定が中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
