"""
シミュレータ連携ハンドラ - llm_forex_slack_simulatorとの連携コマンド処理
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from services.slack_simulator_integration import SlackSimulatorIntegrationService
from utils.slack_utils import SlackUtils

logger = logging.getLogger(__name__)

class SimulatorIntegrationHandler:
    """シミュレータ連携コマンドのハンドラクラス"""
    
    def __init__(self):
        self.integration_service = SlackSimulatorIntegrationService()
        self.slack_utils = SlackUtils()
        
    def handle_simulator_status(self, respond, command):
        """
        !simulator_status コマンドの処理
        シミュレータの接続状態を確認
        """
        try:
            respond("🔍 シミュレータの状態を確認中...")
            
            status = self.integration_service.get_simulator_status()
            
            if "error" in status:
                respond(f"❌ エラーが発生しました: {status['error']}")
                return
            
            # ステータスメッセージを作成
            status_message = "📊 **LLM Forex Slack Simulator 状態**\n\n"
            status_message += f"📁 パス: `{status['simulator_path']}`\n"
            status_message += f"🔧 シミュレータ存在: {'✅' if status['simulator_exists'] else '❌'}\n"
            status_message += f"🐍 main.py存在: {'✅' if status['main_py_exists'] else '❌'}\n"
            status_message += f"⚙️ 設定ファイル存在: {'✅' if status['config_exists'] else '❌'}\n"
            status_message += f"🔗 接続テスト: {'✅ 成功' if status['connection_valid'] else '❌ 失敗'}\n"
            
            if status['connection_valid']:
                status_message += "\n✅ シミュレータとの連携準備完了です！"
            else:
                status_message += "\n⚠️ シミュレータとの接続に問題があります。設定を確認してください。"
            
            respond(status_message)
            
        except Exception as e:
            logger.error(f"Error handling simulator status: {e}")
            respond(f"❌ シミュレータ状態確認中にエラーが発生しました: {str(e)}")
    
    def handle_run_analysis(self, respond, command):
        """
        !run_analysis コマンドの処理
        シミュレータに分析実行を依頼
        """
        try:
            # コマンドパラメータの解析
            text = command.get("text", "").strip()
            params = text.split() if text else []
            
            start_date = None
            end_date = None
            
            # 日付パラメータの解析
            if len(params) >= 2:
                try:
                    start_date = params[0]
                    end_date = params[1]
                    datetime.strptime(start_date, "%Y-%m-%d")  # 形式確認
                    datetime.strptime(end_date, "%Y-%m-%d")    # 形式確認
                except ValueError:
                    respond("❌ 日付形式が正しくありません。YYYY-MM-DD形式で指定してください。\n例: `!run_analysis 2025-07-15 2025-07-20`")
                    return
            
            respond("🔄 取引データの分析を開始します...")
            
            # 分析実行
            results = self.integration_service.trigger_analysis(start_date, end_date)
            
            if "error" in results:
                respond(f"❌ 分析実行中にエラーが発生しました: {results['error']}")
                return
            
            # 結果の整形と表示
            analysis_message = self._format_analysis_results(results)
            respond(analysis_message)
            
        except Exception as e:
            logger.error(f"Error handling run analysis: {e}")
            respond(f"❌ 分析実行中にエラーが発生しました: {str(e)}")
    
    def handle_run_inference(self, respond, command):
        """
        !run_inference コマンドの処理
        シミュレータにAI推論実行を依頼
        """
        try:
            respond("🤖 AI推論を開始します（数分かかる場合があります）...")
            
            # 推論実行
            results = self.integration_service.trigger_inference(is_now=True)
            
            if "error" in results:
                respond(f"❌ 推論実行中にエラーが発生しました: {results['error']}")
                return
            
            # 結果の整形と表示
            inference_message = self._format_inference_results(results)
            respond(inference_message)
            
        except Exception as e:
            logger.error(f"Error handling run inference: {e}")
            respond(f"❌ 推論実行中にエラーが発生しました: {str(e)}")
    
    def _format_analysis_results(self, results: Dict[str, Any]) -> str:
        """分析結果をフォーマット"""
        try:
            message = "📊 **取引データ分析結果**\n\n"
            
            # 基本情報
            if "analysis_info" in results:
                info = results["analysis_info"]
                message += f"📅 分析時刻: {info.get('timestamp', 'N/A')}\n"
                message += f"📈 取引件数: {info.get('transaction_count', 0)}件\n\n"
            
            # ポートフォリオ状態
            if "portfolio_state" in results:
                portfolio = results["portfolio_state"]
                balances = portfolio.get("current_balances", {})
                message += "💰 **現在の残高**\n"
                for currency, amount in balances.items():
                    message += f"  {currency}: {amount:,.2f}\n"
                message += "\n"
            
            # ポートフォリオサマリー（取引履歴情報を含む）
            if "portfolio_summary" in results:
                message += "📈 **ポートフォリオ詳細**\n"
                # HTMLタグを除去してSlack用にフォーマット
                summary = results["portfolio_summary"].replace("**", "*").replace("📊", "📊")
                message += summary + "\n"
            
            # パフォーマンス指標
            if "performance_metrics" in results:
                perf = results["performance_metrics"]
                message += "📈 **パフォーマンス指標**\n"
                message += f"初期価値: ¥{perf.get('initial_value_jpy', 0):,.2f}\n"
                message += f"現在価値: ¥{perf.get('current_value_jpy', 0):,.2f}\n"
                message += f"損益: ¥{perf.get('profit_loss_jpy', 0):+,.2f}\n"
                message += f"利回り: {perf.get('return_rate_percent', 0):+.2f}%\n"
                message += f"運用時間: {perf.get('duration_hours', 0):.1f}時間\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting analysis results: {e}")
            return f"✅ 分析が完了しましたが、結果の表示中にエラーが発生しました: {str(e)}"
    
    def _format_inference_results(self, results: Dict[str, Any]) -> str:
        """推論結果をフォーマット"""
        try:
            message = "🤖 **AI推論結果**\n\n"
            
            # 推論情報
            if "inference_info" in results:
                info = results["inference_info"]
                message += f"🕐 推論時刻: {info.get('timestamp', 'N/A')}\n\n"
            
            # 現在のレート
            if "current_rates" in results:
                rates = results["current_rates"]
                message += "💱 **現在のレート**\n"
                for pair, rate in rates.items():
                    message += f"  {pair}: {rate:.4f}\n"
                message += "\n"
            
            # 抽出された取引判断
            if "extracted_decisions" in results:
                decisions = results["extracted_decisions"]
                if decisions:
                    message += "💡 **AI推論による取引判断**\n"
                    if isinstance(decisions, list):
                        for i, decision in enumerate(decisions, 1):
                            message += f"{i}. {decision}\n"
                    else:
                        message += f"{decisions}\n"
                else:
                    message += "💡 **AI推論結果**: 取引推奨なし\n"
                message += "\n"
            
            # パフォーマンス
            if "performance_metrics" in results:
                perf = results["performance_metrics"]
                message += "📊 **現在のポートフォリオ**\n"
                message += f"総資産価値: ¥{perf.get('current_value_jpy', 0):,.2f}\n"
                message += f"損益: ¥{perf.get('profit_loss_jpy', 0):+,.2f}\n"
                message += f"利回り: {perf.get('return_rate_percent', 0):+.2f}%\n"
                
                # 取引回数も表示
                if perf.get('transaction_count', 0) > 0:
                    message += f"取引回数: {perf['transaction_count']}回\n"
            
            # LLMレスポンスの一部表示
            if "llm_response" in results and results["llm_response"]:
                response_preview = results["llm_response"][:200] + "..." if len(results["llm_response"]) > 200 else results["llm_response"]
                message += f"\n📝 **AIレスポンス（抜粋）**\n```\n{response_preview}\n```"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting inference results: {e}")
            return f"✅ 推論が完了しましたが、結果の表示中にエラーが発生しました: {str(e)}"


def setup_simulator_integration_handlers(app, error_handler=None):
    """シミュレータ連携ハンドラの登録"""
    
    handler = SimulatorIntegrationHandler()
    
    @app.command("/simulator_status")
    def handle_simulator_status_command(ack, respond, command):
        ack()
        try:
            handler.handle_simulator_status(respond, command)
        except Exception as e:
            logger.error(f"Error in simulator status command: {e}")
            if error_handler:
                error_handler.handle_error(e, "simulator_status", command)
            respond(f"❌ エラーが発生しました: {str(e)}")
    
    @app.command("/run_analysis")
    def handle_run_analysis_command(ack, respond, command):
        ack()
        try:
            handler.handle_run_analysis(respond, command)
        except Exception as e:
            logger.error(f"Error in run analysis command: {e}")
            if error_handler:
                error_handler.handle_error(e, "run_analysis", command)
            respond(f"❌ エラーが発生しました: {str(e)}")
    
    @app.command("/run_inference")
    def handle_run_inference_command(ack, respond, command):
        ack()
        try:
            handler.handle_run_inference(respond, command)
        except Exception as e:
            logger.error(f"Error in run inference command: {e}")
            if error_handler:
                error_handler.handle_error(e, "run_inference", command)
            respond(f"❌ エラーが発生しました: {str(e)}")
    
    logger.info("Simulator integration handlers registered successfully")
