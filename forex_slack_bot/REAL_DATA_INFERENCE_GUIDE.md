# 実データ推論機能実装概要

## 概要

Slack Botの実際の取引データを使用してAI推論を行い、結果をシミュレーション推論と分離して保存する機能を実装しました。

## 実装した機能

### 1. 実データ推論サービス (`services/inference_service.py`)

**新しいメソッド**:
- `run_inference_with_real_data()`: 実データを使用した推論の実行
- `_execute_inference_with_real_data()`: 実データ推論の具体的処理
- `_analyze_real_trading_performance()`: 実取引データの分析
- `_parse_simulation_result()` (拡張): 実データ対応版の結果解析
- `_read_simulation_logs()` (拡張): 実データ対応版のログ読み取り

**主な特徴**:
- `run_with_slack_data.py`との連携でSlackボットの実際の残高・取引データを使用
- 結果保存先を `slack_real_data_inference_*` ディレクトリに分離
- 実データ使用時は信頼度を自動的に高く設定（0.9）
- 詳細な取引履歴分析を含む

### 2. 推論ハンドラ (`handlers/inference_handler.py`)

**拡張機能**:
- `/inference real` または `/inference 実データ` コマンドで実データ推論を実行
- 結果ファイル名に `real_data` または `simulation` サフィックスを追加
- 実データ使用時は結果表示に詳細情報を追加

### 3. 定期推論スケジューラ (`schedulers/periodic_inference.py`)

**拡張機能**:
- `PERIODIC_INFERENCE_USE_REAL_DATA` 環境変数で実データ使用を制御
- 定期推論での実データ分析対応
- 実データ使用時の結果表示に詳細分析を追加

### 4. LLM Simulator連携 (`llm_forex_simulator/forex_simulator/run_with_slack_data.py`)

**新しい関数**:
- `run_simulation_with_slack_data()`: Slackボットデータを使用したシミュレーション実行
- Slackボットの `data/balance/balance.json` と `data/transactions/transaction_log.json` を自動読み込み
- 結果保存先を `slack_real_trades_simulation_*` に設定

### 5. 設定管理 (`config.py`)

**新しい設定項目**:
```python
REAL_DATA_INFERENCE_ENABLED: bool  # 実データ推論機能の有効化
REAL_DATA_OUTPUT_DIR: str          # 実データ結果の出力ディレクトリ  
PERIODIC_INFERENCE_USE_REAL_DATA: bool  # 定期推論での実データ使用
```

## 使用方法

### 手動実行

**シミュレーション推論**:
```
/inference
```

**実データ推論**:
```
/inference real
/inference 実データ
```

### 定期実行

環境変数で制御:
```env
# 定期推論で実データを使用
PERIODIC_INFERENCE_USE_REAL_DATA=true

# 実データ推論機能の有効化  
REAL_DATA_INFERENCE_ENABLED=true

# 出力ディレクトリ指定
REAL_DATA_OUTPUT_DIR=../llm_forex_simulator/real_data_output
```

## 出力ファイル構成

### シミュレーション推論
```
temp/
├── slack_inference_20250720_143000/
│   ├── simulation_log.txt
│   └── results.json
```

### 実データ推論
```
llm_forex_simulator/real_data_output/
├── slack_real_data_inference_20250720_143000/
│   ├── simulation_log.txt
│   ├── results.json
│   └── real_data_analysis.txt
└── slack_real_trades_simulation_20250720_143000/
    ├── detailed_log.txt
    └── results.json
```

## 結果の違い

| 項目 | シミュレーション | 実データ |
|------|------------------|----------|
| データソース | 仮想データ | 実際の取引履歴 |
| 信頼度 | 0.8 | 0.9 |
| 保存場所 | temp/ | real_data_output/ |
| 分析詳細度 | 基本 | 詳細 |
| ファイル名プレフィックス | `slack_inference_` | `slack_real_data_inference_` |

## テスト

実装された機能をテストするには:

```bash
cd /mnt/bigdata/00_students/mattsun_ucl/workspace/forex/forex_slack_bot
python test_real_data_inference.py
```

## セキュリティ考慮事項

- 実データ推論は実際の取引データを使用するため、適切なアクセス制御が必要
- 結果ファイルには実際の残高情報が含まれるため、出力ディレクトリの権限設定に注意
- 定期推論での実データ使用は慎重に設定（デフォルト: false）

## 今後の拡張予定

1. **データ暗号化**: 実データファイルの暗号化保存
2. **権限管理**: 実データ推論への管理者権限要求
3. **履歴管理**: 実データ推論結果の履歴管理機能
4. **比較分析**: シミュレーションと実データ結果の自動比較
5. **アラート機能**: 実データ推論での異常値検出とアラート

## 注意事項

- 実データ推論は実際の取引データに依存するため、取引履歴がない場合はフォールバック処理が実行されます
- LLM Simulator との連携が必要なため、simulator が利用できない環境では一部機能が制限されます
- 実データ推論の結果は高い信頼度を持ちますが、実際の投資判断は慎重に行ってください
