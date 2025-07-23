#!/usr/bin/env python3
"""
Forex Slack Bot の動作確認スクリプト
"""

import sys
import os
import importlib.util

def check_python_version():
    """Pythonバージョンの確認"""
    print("=== Python バージョン確認 ===")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 9:
        print("❌ Python 3.9以上が必要です")
        return False
    else:
        print("✅ Pythonバージョン OK")
        return True

def check_dependencies():
    """依存関係の確認"""
    print("\n=== 依存関係確認 ===")
    
    required_packages = [
        "slack_bolt",
        "slack_sdk", 
        "aiohttp",
        "apscheduler",
        "pandas",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                print(f"❌ {package} が見つかりません")
                missing_packages.append(package)
            else:
                print(f"✅ {package} OK")
        except ImportError:
            print(f"❌ {package} のインポートに失敗")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n以下のパッケージをインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✅ 全ての依存関係 OK")
        return True

def check_file_structure():
    """ファイル構成の確認"""
    print("\n=== ファイル構成確認 ===")
    
    required_files = [
        "app.py",
        "config.py",
        "requirements.txt",
        "handlers/__init__.py",
        "handlers/inference_handler.py",
        "handlers/deal_handler.py",
        "handlers/balance_handler.py",
        "handlers/common_handlers.py",
        "services/__init__.py",
        "services/inference_service.py",
        "services/trading_service.py",
        "services/rate_service.py",
        "models/__init__.py",
        "models/balance_manager.py",
        "models/transaction_log.py",
        "schedulers/__init__.py",
        "schedulers/periodic_inference.py",
        "utils/__init__.py",
        "utils/slack_utils.py",
        "utils/error_handler.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} が見つかりません")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n以下のファイルが不足しています:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("\n✅ 全てのファイル OK")
        return True

def check_data_directory():
    """データディレクトリの確認"""
    print("\n=== データディレクトリ確認 ===")
    
    data_dir = "./data"
    
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            print(f"✅ {data_dir} ディレクトリを作成しました")
        except Exception as e:
            print(f"❌ {data_dir} ディレクトリの作成に失敗: {e}")
            return False
    else:
        print(f"✅ {data_dir} ディレクトリ OK")
    
    # 書き込み権限の確認
    test_file = os.path.join(data_dir, "test_write.tmp")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ データディレクトリの書き込み権限 OK")
        return True
    except Exception as e:
        print(f"❌ データディレクトリの書き込み権限なし: {e}")
        return False

def check_config():
    """設定の確認"""
    print("\n=== 設定確認 ===")
    
    try:
        from config import Config
        
        # 必須設定の確認
        required_settings = [
            ("SLACK_BOT_TOKEN", Config.SLACK_BOT_TOKEN),
            ("SLACK_SIGNING_SECRET", Config.SLACK_SIGNING_SECRET),
            ("SLACK_APP_TOKEN", Config.SLACK_APP_TOKEN)
        ]
        
        missing_config = []
        
        for setting_name, setting_value in required_settings:
            if not setting_value:
                print(f"❌ {setting_name} が設定されていません")
                missing_config.append(setting_name)
            else:
                print(f"✅ {setting_name} OK")
        
        if missing_config:
            print(f"\n.envファイルで以下の設定を行ってください:")
            for setting in missing_config:
                print(f"  {setting}=your-value-here")
            return False
        else:
            print("\n✅ 基本設定 OK")
            return True
            
    except ImportError as e:
        print(f"❌ config.py のインポートに失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 設定確認中にエラー: {e}")
        return False

def test_basic_imports():
    """基本的なインポートテスト"""
    print("\n=== インポートテスト ===")
    
    modules_to_test = [
        "handlers.inference_handler",
        "handlers.deal_handler", 
        "handlers.balance_handler",
        "handlers.common_handlers",
        "services.inference_service",
        "services.trading_service",
        "services.rate_service",
        "models.balance_manager",
        "models.transaction_log",
        "schedulers.periodic_inference",
        "utils.slack_utils",
        "utils.error_handler"
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n以下のモジュールのインポートに失敗しました:")
        for module in failed_imports:
            print(f"  - {module}")
        return False
    else:
        print("\n✅ 全てのインポート OK")
        return True

def check_llm_simulator_integration():
    """LLM為替シミュレーター連携の確認"""
    print("\n=== LLM為替シミュレーター連携確認 ===")
    
    # シミュレーターのパスを確認
    simulator_paths = [
        "../llm_forex_simulator",
        "../../llm_forex_simulator", 
        "/mnt/bigdata/00_students/mattsun_ucl/workspace/forex/llm_forex_simulator"
    ]
    
    simulator_found = False
    working_path = None
    
    for path in simulator_paths:
        simulator_file = os.path.join(path, "forex_simulator/simulator.py")
        if os.path.exists(simulator_file):
            print(f"✅ LLM為替シミュレーター発見: {path}")
            simulator_found = True
            working_path = path
            break
        else:
            print(f"❌ {path} にシミュレーターが見つかりません")
    
    if not simulator_found:
        print("⚠️  LLM為替シミュレーターが見つかりません")
        print("   推論機能はフォールバックモードで動作します")
        return True  # 必須ではないので True を返す
    
    # シミュレーターモジュールのインポートテスト
    try:
        import sys
        sys.path.insert(0, os.path.abspath(working_path))
        
        # 基本モジュールの確認
        from forex_simulator import simulator
        from forex_simulator.script import portfolio
        print("✅ シミュレーターモジュールのインポート OK")
        
        # 基本的な設定の確認
        portfolio_test = portfolio.Portfolio(balances={"JPY": 10000, "USD": 0, "EUR": 0})
        print("✅ ポートフォリオクラスの動作 OK")
        
        print("✅ LLM為替シミュレーター連携 OK")
        return True
        
    except ImportError as e:
        print(f"⚠️  シミュレーターモジュールのインポートに失敗: {e}")
        print("   推論機能はフォールバックモードで動作します")
        return True
    except Exception as e:
        print(f"⚠️  シミュレーター連携テスト中にエラー: {e}")
        print("   推論機能はフォールバックモードで動作します")
        return True

def main():
    """メイン実行関数"""
    print("Forex Slack Bot 動作確認スクリプト")
    print("=" * 50)
    
    all_checks = [
        check_python_version(),
        check_dependencies(),
        check_file_structure(),
        check_data_directory(),
        check_config(),
        test_basic_imports(),
        check_llm_simulator_integration()
    ]
    
    print("\n" + "=" * 50)
    print("=== 最終結果 ===")
    
    if all(all_checks):
        print("🎉 全てのチェックが完了しました！")
        print("以下のコマンドでBotを起動できます:")
        print("python app.py")
        return 0
    else:
        print("❌ いくつかの問題が見つかりました。")
        print("上記のメッセージを確認し、問題を解決してください。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
