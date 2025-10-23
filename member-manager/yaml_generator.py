#!/usr/bin/env python3
"""
YAMLファイル生成モジュール
新規レコード作成フォームからYAMLファイルを生成する機能を提供
"""

import logging
from datetime import datetime
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class YAMLGenerator:
    """YAMLファイル生成クラス

    フォームデータから適切なYAMLファイルを生成し、
    ストレージサービスにアップロードするための準備を行います。
    """

    @staticmethod
    def generate_human_member_yaml(form_data: dict[str, Any]) -> str:
        """人間メンバー用のYAMLファイルを生成

        Args:
            form_data (Dict[str, Any]): フォームから送信されたデータ

        Returns:
            str: 生成されたYAML文字列

        Raises:
            ValueError: 必須フィールドが不足している場合
        """
        # 必須フィールドの検証
        if not form_data.get("member_name"):
            raise ValueError("member_name is required for human member")

        # YAMLデータの構築
        # member_nameをnameフィールドに統一
        yaml_data = {
            "name": form_data["member_name"].strip(),
            "created_at": datetime.now().isoformat(),
            "source": "member-manager",
        }

        # オプションフィールドの追加
        if form_data.get("bio"):
            yaml_data["bio"] = form_data["bio"].strip()

        # その他のフィールドがあれば追加
        for key, value in form_data.items():
            if key not in ["member_name", "bio"] and value and value.strip():
                yaml_data[key] = value.strip()

        # YAML文字列に変換
        yaml_content = yaml.dump(
            yaml_data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

        logger.info(f"Generated human member YAML for: {yaml_data['name']}")
        return yaml_content

    @staticmethod
    def generate_virtual_member_yaml(form_data: dict[str, Any]) -> str:
        """仮想メンバー用のYAMLファイルを生成

        Args:
            form_data (Dict[str, Any]): フォームから送信されたデータ

        Returns:
            str: 生成されたYAML文字列

        Raises:
            ValueError: 必須フィールドが不足している場合
        """
        # 必須フィールドの検証
        if not form_data.get("member_name"):
            raise ValueError("member_name is required for virtual member")
        if not form_data.get("llm_model"):
            raise ValueError("llm_model is required for virtual member")

        # YAMLデータの構築
        # member_nameをnameフィールドに統一
        yaml_data = {
            "name": form_data["member_name"].strip(),
            "llm_model": form_data["llm_model"].strip(),
            "created_at": datetime.now().isoformat(),
            "source": "member-manager",
        }

        # オプションフィールドの追加
        if form_data.get("custom_prompt"):
            yaml_data["custom_prompt"] = form_data["custom_prompt"].strip()

        # その他のフィールドがあれば追加
        for key, value in form_data.items():
            if (
                key not in ["member_name", "llm_model", "custom_prompt"]
                and value
                and value.strip()
            ):
                yaml_data[key] = value.strip()

        # YAML文字列に変換
        yaml_content = yaml.dump(
            yaml_data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

        logger.info(f"Generated virtual member YAML for: {yaml_data['name']}")
        return yaml_content

    @staticmethod
    def generate_yaml_filename(member_name: str, member_type: str) -> str:
        """メンバー名からYAMLファイル名を生成

        Args:
            member_name (str): メンバー名
            member_type (str): メンバータイプ ('human' または 'virtual')

        Returns:
            str: 生成されたファイル名
        """
        # ファイル名に使用できない文字を置換
        safe_name = member_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in "_-")

        return f"{safe_name}.yml"

    @staticmethod
    def generate_storage_path(member_name: str, member_type: str) -> str:
        """ストレージ内のパスを生成

        Args:
            member_name (str): メンバー名
            member_type (str): メンバータイプ ('human' または 'virtual')

        Returns:
            str: ストレージ内のパス
        """
        filename = YAMLGenerator.generate_yaml_filename(member_name, member_type)
        return f"data/{member_type}_members/{filename}"

    @staticmethod
    def validate_form_data(
        form_data: dict[str, Any], member_type: str
    ) -> dict[str, str]:
        """フォームデータのバリデーション

        Args:
            form_data (Dict[str, Any]): フォームデータ
            member_type (str): メンバータイプ ('human' または 'virtual')

        Returns:
            Dict[str, str]: エラーメッセージの辞書（空の場合はバリデーション成功）
        """
        errors = {}

        # 共通の必須フィールドチェック
        if not form_data.get("member_name") or not form_data["member_name"].strip():
            errors["member_name"] = "メンバー名は必須です"

        # 仮想メンバーの追加チェック
        if member_type == "virtual":
            if not form_data.get("llm_model") or not form_data["llm_model"].strip():
                errors["llm_model"] = "LLMモデルは必須です"

        # 文字数制限チェック
        if form_data.get("member_name") and len(form_data["member_name"].strip()) > 50:
            errors["member_name"] = "メンバー名は50文字以内で入力してください"

        if form_data.get("bio") and len(form_data["bio"].strip()) > 1000:
            errors["bio"] = "自己紹介は1000文字以内で入力してください"

        if form_data.get("llm_model") and len(form_data["llm_model"].strip()) > 50:
            errors["llm_model"] = "LLMモデル名は50文字以内で入力してください"

        if (
            form_data.get("custom_prompt")
            and len(form_data["custom_prompt"].strip()) > 5000
        ):
            errors["custom_prompt"] = (
                "カスタムプロンプトは5000文字以内で入力してください"
            )

        return errors
