"""
LLM Forex Slack Simulator連携サービス
外部のllm_forex_slack_simulatorとの連携を管理
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SlackSimulatorIntegrationService:
    """LLM Forex Slack Simulatorとの連携サービス"""
    
    def __init__(self, simulator_path: str = "../llm_forex_slack_simulator"):
        """
        Args:
            simulator_path: llm_forex_slack_simulatorのパス
        """
        self.simulator_path = Path(simulator_path).resolve()
        self.logger = logger
        
        # パス存在確認
        if not self.simulator_path.exists():
            self.logger.warning(f"Simulator path not found: {self.simulator_path}")
        else:
            self.logger.info(f"Simulator path found: {self.simulator_path}")
    
    def validate_simulator_connection(self) -> bool:
        """
        シミュレータとの接続を確認
        
        Returns:
            接続成功フラグ
        """
        try:
            # main.pyの存在確認
            main_py = self.simulator_path / "main.py"
            if not main_py.exists():
                self.logger.error(f"Simulator main.py not found: {main_py}")
                return False
            
            # 検証コマンドの実行
            cmd = [
                sys.executable, "main.py", 
                "--mode", "validate", 
                "--quick"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.simulator_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("Simulator connection validated successfully")
                return True
            else:
                self.logger.error(f"Simulator validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating simulator connection: {e}")
            return False
    
    def trigger_analysis(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        シミュレータに分析を実行させる
        
        Args:
            start_date: 分析開始日（YYYY-MM-DD形式）
            end_date: 分析終了日（YYYY-MM-DD形式）
            
        Returns:
            分析結果の辞書
        """
        try:
            cmd = [sys.executable, "main.py", "--mode", "analysis"]
            
            if start_date:
                cmd.extend(["--start_date", start_date])
            if end_date:
                cmd.extend(["--end_date", end_date])
            
            self.logger.info(f"Running analysis command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.simulator_path),
                capture_output=True,
                text=True,
                timeout=300  # 5分のタイムアウト
            )
            
            if result.returncode == 0:
                # 結果ファイルから分析結果を読み込み
                return self._load_latest_analysis_results()
            else:
                self.logger.error(f"Analysis failed: {result.stderr}")
                return {
                    "error": "Analysis execution failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Analysis timed out")
            return {"error": "Analysis timed out"}
        except Exception as e:
            self.logger.error(f"Error triggering analysis: {e}")
            return {"error": str(e)}
    
    def trigger_inference(self, is_now: bool = True) -> Dict[str, Any]:
        """
        シミュレータに推論を実行させる
        
        Args:
            is_now: 現在時刻で推論するかどうか
            
        Returns:
            推論結果の辞書
        """
        try:
            cmd = [sys.executable, "main.py", "--mode", "inference"]
            
            if is_now:
                cmd.append("--is_now")
            
            self.logger.info(f"Running inference command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.simulator_path),
                capture_output=True,
                text=True,
                timeout=600  # 10分のタイムアウト（LLM推論時間を考慮）
            )
            
            if result.returncode == 0:
                # 結果ファイルから推論結果を読み込み
                return self._load_latest_inference_results()
            else:
                self.logger.error(f"Inference failed: {result.stderr}")
                return {
                    "error": "Inference execution failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Inference timed out")
            return {"error": "Inference timed out"}
        except Exception as e:
            self.logger.error(f"Error triggering inference: {e}")
            return {"error": str(e)}
    
    def get_simulator_status(self) -> Dict[str, Any]:
        """
        シミュレータの状態を取得
        
        Returns:
            状態情報の辞書
        """
        try:
            status = {
                "simulator_path": str(self.simulator_path),
                "simulator_exists": self.simulator_path.exists(),
                "main_py_exists": (self.simulator_path / "main.py").exists(),
                "config_exists": (self.simulator_path / "config" / "config.json").exists(),
                "connection_valid": False
            }
            
            if status["main_py_exists"]:
                status["connection_valid"] = self.validate_simulator_connection()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting simulator status: {e}")
            return {"error": str(e)}
    
    def _load_latest_analysis_results(self) -> Dict[str, Any]:
        """最新の分析結果を読み込み"""
        try:
            output_dir = self.simulator_path / "output"
            if not output_dir.exists():
                return {"error": "Output directory not found"}
            
            # 最新の分析ディレクトリを探す
            analysis_dirs = [d for d in output_dir.iterdir() 
                           if d.is_dir() and d.name.startswith("analysis_")]
            
            if not analysis_dirs:
                return {"error": "No analysis results found"}
            
            latest_dir = max(analysis_dirs, key=lambda d: d.stat().st_mtime)
            results_file = latest_dir / "analysis_results.json"
            
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"error": "Analysis results file not found"}
                
        except Exception as e:
            self.logger.error(f"Error loading analysis results: {e}")
            return {"error": str(e)}
    
    def _load_latest_inference_results(self) -> Dict[str, Any]:
        """最新の推論結果を読み込み（新: results/ ディレクトリ対応）"""
        try:
            results_dir = self.simulator_path / "../results"
            results_dir = results_dir.resolve()
            if not results_dir.exists():
                return {"error": "Results directory not found"}
            # 日付順で最新のresultsサブディレクトリを探す
            result_subdirs = [d for d in results_dir.iterdir() if d.is_dir()]
            if not result_subdirs:
                return {"error": "No results found"}
            latest_dir = max(result_subdirs, key=lambda d: d.stat().st_mtime)
            results_file = latest_dir / "inference_results.json"
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"error": "Inference results file not found in latest results directory"}
        except Exception as e:
            self.logger.error(f"Error loading inference results: {e}")
            return {"error": str(e)}
    
    def send_notification_to_simulator(self, message: str, notification_type: str = "info") -> bool:
        """
        シミュレータに通知を送信（将来の拡張用）
        
        Args:
            message: 通知メッセージ
            notification_type: 通知タイプ（info, warning, error）
            
        Returns:
            送信成功フラグ
        """
        try:
            # 現在は仮実装（ファイル通知）
            notifications_file = self.simulator_path / "notifications.json"
            
            notification = {
                "timestamp": datetime.now().isoformat(),
                "type": notification_type,
                "message": message,
                "from": "forex_slack_bot"
            }
            
            # 既存の通知を読み込み
            notifications = []
            if notifications_file.exists():
                with open(notifications_file, 'r', encoding='utf-8') as f:
                    notifications = json.load(f)
            
            # 新しい通知を追加
            notifications.append(notification)
            
            # 最新10件のみ保持
            notifications = notifications[-10:]
            
            # 保存
            with open(notifications_file, 'w', encoding='utf-8') as f:
                json.dump(notifications, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Notification sent to simulator: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
