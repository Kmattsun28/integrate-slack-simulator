# Forex Trading Slack Bot

実際の取引データを使用したAI推論をSlackで提供するBotです（シミュレーション機能削除版）。

## 概要

このBotは以下の機能を提供します：

- **🔥 実取引データ専用AI推論**: 実際の取引履歴と残高データを使用したAI推論
- **📊 リアルタイム分析**: 現在の市場データと取引実績を統合した分析
- **💰 残高管理**: 実際の通貨残高の追跡と分析
- **🤖 定期分析**: 設定間隔での自動実取引データ推論実行
- **📈 取引ログ**: 全実取引の履歴管理と分析
- **🆕 LLM Simulator連携**: llm_forex_slack_simulatorとの完全統合
- **⚠️ シミュレーション機能削除**: 実取引データのみに特化したシステム

## 重要な変更点

### v2.0 - 実取引データ専用化
- ✅ シミュレーション機能を完全削除
- ✅ 実際の取引データのみを使用するように全機能を修正
- ✅ llm_forex_slack_simulatorとの完全統合
- ✅ より保守的なリスク管理（実取引対応）
- ✅ 実取引データに基づく高精度な分析

## 技術スタック

- **言語**: Python 3.9+
- **フレームワーク**: Slack Bolt for Python
- **非同期処理**: asyncio
- **データ永続化**: JSON ファイル（初期段階）
- **スケジューリング**: APScheduler

## ファイル構成

```
forex_slack_bot/
├── app.py                    # メインアプリケーション
├── config.py                 # 設定管理
├── requirements.txt          # 依存関係
├── .env.example             # 環境変数サンプル
├── README.md                # このファイル
├── data/                    # データファイル
├── handlers/                # Slackイベントハンドラ
│   ├── inference_handler.py # 推論コマンド処理
│   ├── deal_handler.py      # 取引コマンド処理
│   ├── balance_handler.py   # 残高コマンド処理
│   └── common_handlers.py   # 共通ハンドラ
├── services/                # ビジネスロジック
│   ├── inference_service.py # 推論サービス
│   ├── trading_service.py   # 取引サービス
│   └── rate_service.py      # レート取得サービス
├── models/                  # データ永続化
│   ├── balance_manager.py   # 残高管理
│   └── transaction_log.py   # 取引ログ管理
├── schedulers/              # 定期実行
│   └── periodic_inference.py # 定期推論
└── utils/                   # ユーティリティ
    ├── slack_utils.py       # Slack API連携
    └── error_handler.py     # エラーハンドリング
```

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`を`.env`にコピーし、必要な値を設定してください：

```bash
cp .env.example .env
```

必須設定項目：
- `SLACK_BOT_TOKEN`: SlackボットのOAuthトークン
- `SLACK_SIGNING_SECRET`: Slackアプリの署名シークレット
- `SLACK_APP_TOKEN`: ソケットモード用のアプリトークン

### 3. Slackアプリの設定

1. [Slack API](https://api.slack.com/apps)でアプリを作成
2. Socket Modeを有効化
3. 必要なスコープを設定：
   - `chat:write`
   - `files:write`
   - `users:read`
   - `channels:read`
   - `im:read`
   - `commands`

### 4. Bot の起動

```bash
python app.py
```

## 利用可能なコマンド

### 推論・分析系
- `/inference` - AI推論を実行（非同期処理、結果はファイル添付）
- `/inference real` - 実際の取引データを使用したAI推論（別途保存）
  - 実データまたは`real`を含むテキストでコマンドを実行

### 取引系
- `/deal {通貨ペア} {±金額} {レート}` - 取引実行
  - 例: `/deal USDJPY +300 172.4`
- `/deal-undo` - 最新の取引を取り消し
- `/deal-redo` - 取り消した取引をやり直し
- `/deal-log` - 取引ログ表示（DMのみ）

### 残高系
- `/balance` - 現在の残高表示（DMのみ）
- `/balance-override {通貨} {金額}` - 残高上書き（管理者のみ）

### その他
- `/help` - ヘルプ表示

### 🆕 LLM Simulator連携系
- `/simulator_status` - llm_forex_slack_simulatorの状態確認
- `/run_analysis [開始日] [終了日]` - 実取引データの分析実行
  - 例: `/run_analysis 2025-07-15 2025-07-20`
- `/run_inference` - AI推論実行（シミュレータ経由）

## 機能詳細

### 1. 推論機能
- **非同期実行**: 推論は時間がかかるため、バックグラウンドで実行
- **ロック機構**: 同時実行を防止
- **エラーハンドリング**: GPUメモリ不足などの具体的なエラー対応
- **結果ファイル**: 推論結果はテキストファイルとして添付

### 2. 取引機能
- **残高チェック**: 十分な残高があるかを事前確認
- **取引ログ**: 全ての取引を自動記録
- **取り消し/やり直し**: 最新取引の取り消しと復元が可能

### 3. セキュリティ
- **DM制限**: 残高確認と取引ログはDMでのみ表示
- **管理者権限**: 残高上書きには管理者権限が必要
- **確認機能**: 破壊的操作は事前確認

### 4. 定期実行
- **自動推論**: 設定間隔で自動的に推論を実行
- **レート時刻表示**: レート取得時刻を明確に表示
- **衝突回避**: 手動推論との競合を防止

### 5. 実データ分析（新機能）
- **実取引データ使用**: Slackボットの実際の取引履歴を使用したAI推論
- **結果分離**: シミュレーションと実データの結果を別々に保存
- **高い信頼度**: 実際のデータに基づくため高い推論精度
- **詳細分析**: 取引パフォーマンスと履歴の詳細分析
- **柔軟な出力**: 専用ディレクトリに結果を保存（`slack_real_data_inference_*`）

### 🆕 6. LLM Simulator連携機能
- **統合分析**: llm_forex_slack_simulatorと連携した高度な分析
- **自動実行**: Slack経由でシミュレータの機能を直接実行
- **リアルタイム連携**: 取引データをリアルタイムでシミュレータに送信
- **状態監視**: シミュレータの動作状態をSlackから確認可能
- **結果統合**: 分析・推論結果を自動的にSlackに通知

#### 連携機能の詳細
- **データ同期**: data/balance/balance.json、data/transactions/transaction_log.jsonを自動同期
- **コマンド実行**: シミュレータのmain.pyを直接呼び出し
- **エラーハンドリング**: タイムアウト・エラー時の適切な通知
- **結果フォーマット**: 分析結果を分かりやすく表示

## 設定

主要な設定は `config.py` で管理されています：

- **サポート通貨**: JPY, USD, EUR
- **初期残高**: JPY 1,000,000円
- **定期推論間隔**: 1時間（デフォルト）
- **推論タイムアウト**: 5分

## 開発・拡張

### 推論モデルの実装

`services/inference_service.py` の `_execute_inference_model` メソッドで実際の推論モデルを実装してください：

```python
# TODO: 実際の推論モデルをここに実装
# 例:
# model = load_model(Config.MODEL_PATH)
# result = model.predict(features)
```

### レートAPI の実装

`services/rate_service.py` で外部レートAPIとの連携を実装してください。

### データベース対応

将来的にはJSONファイルからデータベースへの移行を想定しています。

## ログ

- アプリケーションログは標準出力とログファイルに出力
- エラーは詳細なスタックトレースと共に記録
- 重要なエラーは管理者チャンネルに自動通知

## トラブルシューティング

### よくある問題

1. **推論が開始されない**
   - GPUメモリを確認
   - 他の推論プロセスが実行中でないか確認

2. **Slack API エラー**
   - トークンの有効性を確認
   - スコープ設定を確認

3. **ファイル権限エラー**
   - データディレクトリの書き込み権限を確認

### ログの確認

```bash
tail -f forex_bot.log
```

## ライセンス

このプロジェクトは MIT ライセンスの下で提供されています。

## 貢献

バグ報告や機能リクエストは Issue にてお願いします。
# forex_slack_bot
