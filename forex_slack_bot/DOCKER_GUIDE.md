# Docker Compose による運用ガイド

## 概要

このForex Slack BotはDocker Composeを使用してマルチコンテナ構成で動作します。

### アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐
│   Slack Bot     │    │   Scheduler     │
│   Container     │    │   Container     │
│                 │    │                 │
│ • Slackイベント  │    │ • 定期推論実行   │
│ • コマンド処理   │    │ • 結果通知      │
│ • リアルタイム   │    │ • エラー処理    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 │
    ┌─────────────────────────────┐
    │      共有ボリューム          │
    │ • データファイル             │
    │ • ログファイル               │
    │ • LLMシミュレーター          │
    └─────────────────────────────┘
```

## クイックスタート

### 1. 環境設定

```bash
# .envファイルを編集してSlackトークンを設定
cp .env.example .env
vim .env
```

### 2. サービスの開始

```bash
# 本番環境
./docker-manage.sh up

# 開発環境（ソースコードの変更がリアルタイムに反映）
./docker-manage.sh up-dev
```

### 3. 状態確認

```bash
./docker-manage.sh status
```

## 管理コマンド

### 基本操作

```bash
# イメージビルド
./docker-manage.sh build

# サービス開始（本番）
./docker-manage.sh up

# サービス開始（開発）
./docker-manage.sh up-dev

# サービス停止
./docker-manage.sh down

# サービス再起動
./docker-manage.sh restart
```

### ログ確認

```bash
# 全ログを表示
./docker-manage.sh logs

# 特定サービスのログ
./docker-manage.sh logs slack-bot
./docker-manage.sh logs scheduler
```

### メンテナンス

```bash
# バックアップ作成
./docker-manage.sh backup

# データ復元
./docker-manage.sh restore backup_file.tar.gz

# リソースクリーンアップ
./docker-manage.sh cleanup
```

## 設定

### 環境変数（.env）

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `SLACK_BOT_TOKEN` | Slackボットトークン | ✅ |
| `SLACK_SIGNING_SECRET` | Slack署名シークレット | ✅ |
| `SLACK_APP_TOKEN` | Slackアプリトークン | ✅ |
| `PERIODIC_INFERENCE_ENABLED` | 定期推論の有効/無効 | - |
| `PERIODIC_INFERENCE_INTERVAL_HOURS` | 実行間隔（時間） | - |
| `LLM_SIMULATOR_PATH` | コンテナ内のシミュレーターパス | - |

### ボリュームマウント

| ホストパス | コンテナパス | 説明 |
|-----------|-------------|------|
| `./data` | `/app/data` | データ永続化 |
| `./logs` | `/app/logs` | ログファイル |
| `[LLM_SIMULATOR_HOST_PATH]` | `/llm_forex_simulator` | シミュレーター（読み取り専用） |

## トラブルシューティング

### 1. サービスが開始できない

```bash
# ログを確認
./docker-manage.sh logs

# 設定ファイルを確認
cat .env

# ネットワーク状態を確認
docker network ls
```

### 2. 定期実行が動作しない

```bash
# スケジューラーのログを確認
./docker-manage.sh logs scheduler

# コンテナの状態を確認
docker-compose ps
```

### 3. LLMシミュレーターにアクセスできない

```bash
# マウント状態を確認
docker-compose exec slack-bot ls -la /llm_forex_simulator

# パスの確認
docker-compose exec slack-bot env | grep LLM_SIMULATOR
```

## 開発・デバッグ

### 開発環境での実行

```bash
# 開発環境で起動（ソースコード変更がリアルタイム反映）
./docker-manage.sh up-dev

# コンテナ内でシェル実行
docker-compose exec slack-bot bash
```

### デバッグ用コマンド

```bash
# 手動で推論実行テスト
docker-compose exec scheduler python -c "
import asyncio
from scheduler import SchedulerService
s = SchedulerService()
asyncio.run(s.run_periodic_inference())
"

# 設定確認
docker-compose exec slack-bot python -c "
from config import Config
print(f'Simulator path: {Config.LLM_SIMULATOR_PATH}')
print(f'Periodic enabled: {Config.PERIODIC_INFERENCE_ENABLED}')
"
```

## 監視とメトリクス

### ヘルスチェック

各コンテナには自動ヘルスチェックが設定されています：

```bash
# ヘルスチェック状態確認
docker-compose ps
```

### ログローテーション

ログファイルが大きくなりすぎないよう、定期的にローテーションしてください：

```bash
# ログサイズ確認
du -sh logs/

# 古いログの削除（7日以上前）
find logs/ -name "*.log" -mtime +7 -delete
```

## セキュリティ

### 設定ファイルの保護

```bash
# .envファイルの権限設定
chmod 600 .env

# 不要なファイルをgitから除外
echo ".env" >> .gitignore
echo "logs/" >> .gitignore
echo "data/" >> .gitignore
```

### ネットワークセキュリティ

- コンテナ間通信は内部ネットワークで暗号化
- 外部との通信はHTTPS/WSS only
- 不要なポートは公開しない

## バックアップ・復旧

### 自動バックアップ

cronで定期バックアップを設定：

```bash
# crontabに追加
0 2 * * * cd /path/to/forex_slack_bot && ./docker-manage.sh backup
```

### 災害復旧

```bash
# 1. サービス停止
./docker-manage.sh down

# 2. データ復元
./docker-manage.sh restore backup_file.tar.gz

# 3. サービス再開
./docker-manage.sh up
```
