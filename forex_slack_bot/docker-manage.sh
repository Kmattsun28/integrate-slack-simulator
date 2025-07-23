#!/bin/bash

# Forex Slack Bot Docker管理スクリプト

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 使用法を表示
show_usage() {
    cat << EOF
Forex Slack Bot Docker管理スクリプト

使用法:
  $0 [COMMAND] [OPTIONS]

コマンド:
  build              イメージをビルド
  up                 サービスを開始（本番環境）
  up-dev             サービスを開始（開発環境）
  down               サービスを停止
  restart            サービスを再起動
  logs               ログを表示
  status             サービス状態を表示
  cleanup            不要なリソースを削除
  backup             データをバックアップ
  restore [FILE]     データを復元

オプション:
  -h, --help         このヘルプを表示

例:
  $0 build           # イメージをビルド
  $0 up              # 本番環境でサービス開始
  $0 up-dev          # 開発環境でサービス開始
  $0 logs slack-bot  # slack-botサービスのログを表示
  $0 backup          # データをバックアップ
EOF
}

# 必要なファイルの存在確認
check_requirements() {
    local required_files=(".env" "docker-compose.yml" "Dockerfile")
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "必要なファイル '$file' が見つかりません"
            return 1
        fi
    done
    
    # .envファイルの設定確認
    if ! grep -q "SLACK_BOT_TOKEN=xoxb-" .env; then
        log_warning ".envファイルでSLACK_BOT_TOKENが設定されていません"
    fi
    
    return 0
}

# イメージをビルド
build_images() {
    log_info "Docker イメージをビルド中..."
    docker-compose build --no-cache
    log_success "イメージのビルドが完了しました"
}

# 本番環境でサービス開始
start_production() {
    log_info "本番環境でサービスを開始中..."
    
    if ! check_requirements; then
        log_error "要件確認に失敗しました"
        exit 1
    fi
    
    # データディレクトリを作成
    mkdir -p data logs
    
    docker-compose up -d
    log_success "サービスが開始されました"
    
    # 健全性チェック
    log_info "サービスの健全性をチェック中..."
    sleep 10
    docker-compose ps
}

# 開発環境でサービス開始
start_development() {
    log_info "開発環境でサービスを開始中..."
    
    if ! check_requirements; then
        log_error "要件確認に失敗しました"
        exit 1
    fi
    
    # データディレクトリを作成
    mkdir -p data logs
    
    docker-compose -f docker-compose.dev.yml up
}

# サービス停止
stop_services() {
    log_info "サービスを停止中..."
    docker-compose down
    log_success "サービスが停止されました"
}

# サービス再起動
restart_services() {
    log_info "サービスを再起動中..."
    docker-compose restart
    log_success "サービスが再起動されました"
}

# ログ表示
show_logs() {
    local service_name="$1"
    
    if [[ -n "$service_name" ]]; then
        log_info "$service_name のログを表示中..."
        docker-compose logs -f "$service_name"
    else
        log_info "全サービスのログを表示中..."
        docker-compose logs -f
    fi
}

# サービス状態表示
show_status() {
    log_info "サービス状態:"
    docker-compose ps
    
    echo
    log_info "リソース使用状況:"
    docker stats --no-stream
}

# リソースクリーンアップ
cleanup_resources() {
    log_warning "不要なDockerリソースを削除します。よろしいですか？ (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "リソースをクリーンアップ中..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        log_success "クリーンアップが完了しました"
    else
        log_info "クリーンアップをキャンセルしました"
    fi
}

# データバックアップ
backup_data() {
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${backup_dir}/forex_bot_backup_${timestamp}.tar.gz"
    
    log_info "データをバックアップ中..."
    
    # バックアップディレクトリを作成
    mkdir -p "$backup_dir"
    
    # データとログをtar.gzでアーカイブ
    tar -czf "$backup_file" data/ logs/ .env
    
    log_success "バックアップが作成されました: $backup_file"
}

# データ復元
restore_data() {
    local backup_file="$1"
    
    if [[ -z "$backup_file" ]]; then
        log_error "復元するバックアップファイルを指定してください"
        log_info "使用法: $0 restore <backup_file>"
        return 1
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "バックアップファイル '$backup_file' が見つかりません"
        return 1
    fi
    
    log_warning "既存のデータを上書きします。よろしいですか？ (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "データを復元中..."
        tar -xzf "$backup_file"
        log_success "データの復元が完了しました"
    else
        log_info "復元をキャンセルしました"
    fi
}

# メイン処理
main() {
    case "${1:-}" in
        "build")
            build_images
            ;;
        "up")
            start_production
            ;;
        "up-dev")
            start_development
            ;;
        "down")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs "$2"
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup_resources
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "-h"|"--help"|"help")
            show_usage
            ;;
        *)
            log_error "不明なコマンド: ${1:-}"
            show_usage
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"
