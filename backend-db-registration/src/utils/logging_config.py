#!/usr/bin/env python3
"""
共通ロギング設定モジュール

このモジュールは、サービス全体で統一されたロギング設定を提供します。
各モジュールでこの関数を呼び出すことで、一貫したロギング設定を実現します。
"""

import logging
import os
from pathlib import Path


def setup_logging(
    module_name: str = None, log_level: str = None, log_format: str = None, log_file: str = None
) -> logging.Logger:
    """
    統一されたロギング設定を行う

    Args:
        module_name: ロガー名（Noneの場合は__name__が使用される）
        log_level: ログレベル（環境変数LOG_LEVELから取得、デフォルトはINFO）
        log_format: ログフォーマット（デフォルトは統一されたフォーマット）
        log_file: ログファイルパス（環境変数LOG_FILEから取得）

    Returns:
        logging.Logger: 設定されたロガーインスタンス
    """

    # デフォルト値の設定
    if module_name is None:
        module_name = __name__

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if log_file is None:
        log_file = os.getenv("LOG_FILE")

    # ログレベルの検証
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        log_level = "INFO"
        print(f"Warning: Invalid log level '{log_level}', using 'INFO' instead")

    # ログレベルの設定
    numeric_level = getattr(logging, log_level)

    # ルートロガーの設定（既に設定されている場合はスキップ）
    if not logging.getLogger().handlers:
        logging.basicConfig(level=numeric_level, format=log_format, handlers=[])

    # モジュール固有のロガーを取得
    logger = logging.getLogger(module_name)
    logger.setLevel(numeric_level)

    # ハンドラーが既に設定されている場合はスキップ
    if logger.handlers:
        return logger

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラーの設定（LOG_FILEが指定されている場合）
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(numeric_level)
            file_formatter = logging.Formatter(log_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            print(f"Warning: Failed to setup file logging to {log_file}: {e}")

    # ログの重複を防ぐ
    logger.propagate = False

    return logger


def get_logger(module_name: str = None) -> logging.Logger:
    """
    既存のロガーを取得する（setup_loggingが既に呼ばれている場合）

    Args:
        module_name: ロガー名（Noneの場合は__name__が使用される）

    Returns:
        logging.Logger: ロガーインスタンス
    """
    if module_name is None:
        module_name = __name__

    return logging.getLogger(module_name)
