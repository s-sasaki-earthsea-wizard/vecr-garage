import logging
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """YAMLファイルのバリデーション時に発生するカスタム例外クラス

    必須フィールドの欠落や不正な形式を検出した際に使用されます。

    Attributes:
        message (str): エラーメッセージ
        missing_fields (List[str]): 欠落している必須フィールドのリスト
    """

    def __init__(self, message: str, missing_fields: list[str] = None):
        self.message = message
        self.missing_fields = missing_fields or []
        super().__init__(self.message)


class YAMLValidator:
    """YAMLファイルの構造と内容を検証するクラス

    メンバー登録用のYAMLファイルが正しい形式で必要な情報を含んでいるかを
    チェックし、問題がある場合はValidationErrorを発生させます。

    主な機能:
    - 人間メンバーYAMLの必須フィールド検証
    - 仮想メンバーYAMLの必須フィールド検証
    - YAML構造の基本的な検証
    """

    @staticmethod
    def validate_human_member_yaml(yaml_data: dict[str, Any]) -> None:
        """人間メンバーのYAMLデータを検証する

        人間メンバーに必要な必須フィールドが存在し、空でないことを確認します。

        Args:
            yaml_data (Dict[str, Any]): 検証対象のYAMLデータ（辞書形式）

        Raises:
            ValidationError: 必須フィールドが欠落している場合、または空の場合

        Example:
            >>> data = {"name": "田中太郎"}
            >>> YAMLValidator.validate_human_member_yaml(data)  # 成功
            >>> data = {"age": 30}
            >>> YAMLValidator.validate_human_member_yaml(data)  # ValidationError発生
        """
        required_fields = ["name"]
        missing_fields = []

        for field in required_fields:
            if (
                field not in yaml_data
                or yaml_data[field] is None
                or yaml_data[field] == ""
            ):
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Required fields missing in human member YAML: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValidationError(error_msg, missing_fields)

        logger.info(f"Human member YAML validation passed for: {yaml_data['name']}")

    @staticmethod
    def validate_virtual_member_yaml(yaml_data: dict[str, Any]) -> None:
        """仮想メンバーのYAMLデータを検証する

        仮想メンバーに必要な必須フィールド（name, llm_model）が存在し、
        空でないことを確認します。

        Args:
            yaml_data (Dict[str, Any]): 検証対象のYAMLデータ（辞書形式）

        Raises:
            ValidationError: 必須フィールドが欠落している場合、または空の場合

        Example:
            >>> data = {"name": "AI助手", "llm_model": "gpt-4"}
            >>> YAMLValidator.validate_virtual_member_yaml(data)  # 成功
            >>> data = {"name": "AI助手"}
            >>> YAMLValidator.validate_virtual_member_yaml(data)  # ValidationError発生
        """
        required_fields = ["name", "llm_model"]
        missing_fields = []

        for field in required_fields:
            if (
                field not in yaml_data
                or yaml_data[field] is None
                or yaml_data[field] == ""
            ):
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Required fields missing in virtual member YAML: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValidationError(error_msg, missing_fields)

        logger.info(f"Virtual member YAML validation passed for: {yaml_data['name']}")

    @staticmethod
    def validate_yaml_structure(yaml_content: str) -> dict[str, Any]:
        """YAMLの構造を検証し、パースされたデータを返す

        YAML文字列が正しい形式であることを確認し、辞書形式のデータとして
        パースします。不正な形式の場合はValidationErrorを発生させます。

        Args:
            yaml_content (str): 検証対象のYAML文字列

        Returns:
            Dict[str, Any]: パースされたYAMLデータ（辞書形式）

        Raises:
            ValidationError: YAML形式が不正な場合、または辞書形式でない場合

        Example:
            >>> yaml_str = "name: 田中太郎\\nage: 30"
            >>> data = YAMLValidator.validate_yaml_structure(yaml_str)
            >>> print(data)  # {'name': '田中太郎', 'age': 30}
        """
        try:
            yaml_data = yaml.safe_load(yaml_content)
            if not isinstance(yaml_data, dict):
                error_msg = "YAML content must be a dictionary"
                logger.error(error_msg)
                raise ValidationError(error_msg)
            return yaml_data
        except yaml.YAMLError as e:
            error_msg = f"Invalid YAML format: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
