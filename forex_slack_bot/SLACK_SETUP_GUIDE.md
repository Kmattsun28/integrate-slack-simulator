# Slack Bot 完全セットアップガイド

## 🎯 概要

このガイドでは、Forex Trading Slack Botを一から設定する方法を詳しく説明します。

## 🔧 必要な準備

- Slackワークスペースの管理者権限
- ボットを動作させるサーバー環境
- インターネット接続

---

## 📱 Step 1: Slack アプリの作成

### 1.1 Slack API サイトにアクセス

1. https://api.slack.com/apps にアクセス
2. Slackアカウントでログイン
3. 「**Create New App**」をクリック

### 1.2 アプリ作成

1. 「**From scratch**」を選択
2. 以下を入力：
   - **App Name**: `Forex Trading Bot` (任意の名前)
   - **Pick a workspace**: ボットを使用するワークスペースを選択
3. 「**Create App**」をクリック

---

## 🤖 Step 2: Bot の設定

### 2.1 OAuth & Permissions の設定

1. 左メニューから「**OAuth & Permissions**」をクリック
2. 「**Scopes**」セクションまでスクロール
3. 「**Bot Token Scopes**」に以下の権限を追加：

```
channels:history    # チャンネル履歴の読み取り
channels:read      # チャンネル情報の読み取り
chat:write         # メッセージの送信
commands           # スラッシュコマンドの処理
files:write        # ファイルのアップロード
im:history         # ダイレクトメッセージ履歴の読み取り
im:read            # DMチャンネル情報の読み取り
im:write           # DMメッセージの送信
users:read         # ユーザー情報の読み取り
```

4. 「**Install App to Workspace**」をクリック
5. 「**Allow**」をクリックして権限を許可
6. 「**Bot User OAuth Token**」をコピー（`xoxb-`で始まる）

### 2.2 Socket Mode の有効化

1. 左メニューから「**Socket Mode**」をクリック
2. 「**Enable Socket Mode**」をオンにする
3. トークン作成ダイアログで：
   - **Token Name**: `socket_token`
   - 「**Generate**」をクリック
4. 「**App-Level Token**」をコピー（`xapp-`で始まる）


### 2.3 Signing Secret の取得
1. 左メニューから「**Basic Information**」をクリック
2. 「**App Credentials**」セクションの「**Signing Secret**」をコピー

---

## ⚡ Step 3: スラッシュコマンドの登録

### 3.1 コマンド作成

1. 左メニューから「**Slash Commands**」をクリック
2. 「**Create New Command**」をクリック
3. 以下のコマンドを順番に作成：

#### `/inference` コマンド
```
Command: /inference
Request URL: (空欄のまま - Socket Mode使用)
Short Description: AI推論を実行して市場分析を行う
Usage Hint: 現在の市場状況に基づいてAI推論を実行
```

#### `/deal` コマンド
```
Command: /deal
Request URL: (空欄のまま)
Short Description: 取引を実行する
Usage Hint: [通貨ペア] [buy/sell] [金額] (例: USDJPY buy 1000)
```

#### `/balance` コマンド
```
Command: /balance
Request URL: (空欄のまま)
Short Description: 残高を確認する
Usage Hint: 現在の残高状況を表示
```

#### `/help` コマンド
```
Command: /help
Request URL: (空欄のまま)
Short Description: ヘルプを表示する
Usage Hint: 利用可能なコマンド一覧を表示
```

4. 各コマンドで「**Save**」をクリック

---

## 🔑 Step 4: 環境変数の設定

### 4.1 設定ファイルの作成

1. プロジェクトディレクトリで`.env`ファイルを編集：

```bash
cd /mnt/bigdata/00_students/mattsun_ucl/workspace/forex/forex_slack_bot
cp env_template.txt .env
vim .env
```

### 4.2 トークンの設定

`.env`ファイルで以下の値を実際のトークンに置き換える：

```bash
# 必須項目（実際の値に置き換えてください）
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here
SLACK_SIGNING_SECRET=your-actual-signing-secret-here
SLACK_APP_TOKEN=xapp-your-actual-app-token-here

# チャンネル設定（実際のチャンネル名に変更）
DEFAULT_CHANNEL=#forex-trading
ADMIN_CHANNEL=#admin
```

### 4.3 管理者ユーザーIDの取得

1. Slackで自分のプロフィールをクリック
2. 「その他」→「メンバーIDをコピー」をクリック
3. `.env`ファイルの`ADMIN_USER_IDS`に設定

---

## 🚀 Step 5: ボットのテスト起動

### 5.1 開発環境でのテスト

```bash
# 依存関係のインストール
pip install -r requirements.txt

# ボットの起動（開発モード）
python app.py
```

### 5.2 Docker での起動

```bash
# Docker環境でのテスト
./docker-manage.sh up-dev
```

### 5.3 動作確認

Slackで以下をテスト：

1. `/help` - ヘルプが表示されるか
2. `/balance` - 残高が表示されるか（DMで実行）
3. `/inference` - 推論が実行されるか

---

## 🔧 Step 6: 本番環境での運用

### 6.1 チャンネルの作成

Slackで必要なチャンネルを作成：
```
#forex-trading  (推論結果投稿用)
#admin          (管理者通知用)
```

### 6.2 本番起動

```bash
./docker-manage.sh up
```

### 6.3 ログ確認

```bash
./docker-manage.sh logs
```

---

## ❓ トラブルシューティング

### よくある問題と解決方法

#### 1. 「Invalid token」エラー
```
原因: トークンが正しく設定されていない
解決: .envファイルでトークンを再確認
```

#### 2. 「Missing scope」エラー
```
原因: 必要な権限が設定されていない
解決: OAuth & Permissionsで権限を再確認
```

#### 3. スラッシュコマンドが反応しない
```
原因: Socket Modeが有効になっていない
解決: Socket Modeの設定を確認
```

#### 4. チャンネルにメッセージが投稿されない
```
原因: ボットがチャンネルに招待されていない
解決: チャンネルでボットを招待（/invite @botname）
```

### デバッグ用コマンド

```bash
# 設定確認
python -c "from config import Config; print(f'Bot Token: {Config.SLACK_BOT_TOKEN[:10]}...')"

# 接続テスト
python check_setup.py

# ログ確認
./docker-manage.sh logs slack-bot
```

---

## 📊 設定確認チェックリスト

- [ ] Slack アプリを作成済み
- [ ] Bot Token Scopes を設定済み
- [ ] Socket Mode を有効化済み
- [ ] スラッシュコマンドを登録済み
- [ ] 必要なトークンを取得済み
- [ ] .envファイルに正しい値を設定済み
- [ ] 必要なチャンネルを作成済み
- [ ] ボットをチャンネルに招待済み
- [ ] 管理者ユーザーIDを設定済み
- [ ] 動作テスト完了

---

## 📞 サポート

設定でお困りの場合は、以下の情報と共にお問い合わせください：

1. エラーメッセージ
2. 実行したコマンド
3. ログファイルの関連部分
4. 設定状況（トークンは除く）

## 🔗 参考リンク

- [Slack API Documentation](https://api.slack.com/)
- [Socket Mode Guide](https://api.slack.com/apis/connections/socket)
- [Slash Commands Guide](https://api.slack.com/interactivity/slash-commands)
