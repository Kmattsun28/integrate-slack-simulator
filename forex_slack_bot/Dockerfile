# Dockerfile for Forex Slack Bot
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新とタイムゾーン設定
RUN apt-get update && apt-get install -y \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# タイムゾーンをJSTに設定
ENV TZ=Asia/Tokyo

# Python依存関係ファイルをコピー
COPY requirements.txt .

# Python依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# データディレクトリを作成
RUN mkdir -p /app/data /app/logs

# 環境変数の設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ヘルスチェック用のスクリプト
COPY healthcheck.py /app/healthcheck.py
RUN chmod +x /app/healthcheck.py

# ヘルスチェックの設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python /app/healthcheck.py

# デフォルトポートを公開（必要に応じて）
EXPOSE 3000

# デフォルトコマンド（docker-compose.ymlでオーバーライド）
CMD ["python", "app.py"]
