import yaml
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """バリデーションエラーのカスタム例外"""
    def __init__(self, message: str, missing_fields: List[str] = None):
        self.message = message
        self.missing_fields = missing_fields or []
        super().__init__(self.message)

class YAMLValidator:
    """YAMLファイルのバリデーションを行うクラス"""
    
    @staticmethod
    def validate_human_member_yaml(yaml_data: Dict[str, Any]) -> None:
        """人間メンバーのYAMLデータを検証する"""
        required_fields = ['name']
        missing_fields = []
        
        for field in required_fields:
            if field not in yaml_data or yaml_data[field] is None or yaml_data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Required fields missing in human member YAML: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValidationError(error_msg, missing_fields)
        
        logger.info(f"Human member YAML validation passed for: {yaml_data['name']}")
    
    @staticmethod
    def validate_virtual_member_yaml(yaml_data: Dict[str, Any]) -> None:
        """仮想メンバーのYAMLデータを検証する"""
        required_fields = ['name', 'llm_model']
        missing_fields = []
        
        for field in required_fields:
            if field not in yaml_data or yaml_data[field] is None or yaml_data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Required fields missing in virtual member YAML: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValidationError(error_msg, missing_fields)
        
        logger.info(f"Virtual member YAML validation passed for: {yaml_data['name']}")
    
    @staticmethod
    def validate_yaml_structure(yaml_content: str) -> Dict[str, Any]:
        """YAMLの構造を検証し、パースされたデータを返す"""
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