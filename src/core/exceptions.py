"""
Custom Exceptions for Debug Agent
定义项目中使用的自定义异常类
"""

class DebugAgentException(Exception):
    """Debug Agent基础异常类"""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AnalysisException(DebugAgentException):
    """分析过程异常"""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message, "ANALYSIS_ERROR")

class RepairException(DebugAgentException):
    """修复过程异常"""

    def __init__(self, message: str, repair_strategy: str = None):
        self.repair_strategy = repair_strategy
        super().__init__(message, "REPAIR_ERROR")

class ConfigurationException(DebugAgentException):
    """配置异常"""

    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message, "CONFIG_ERROR")

class TestGenerationException(DebugAgentException):
    """测试生成异常"""

    def __init__(self, message: str, test_case_id: str = None):
        self.test_case_id = test_case_id
        super().__init__(message, "TEST_GENERATION_ERROR")

class ValidationException(DebugAgentException):
    """验证异常"""

    def __init__(self, message: str, validation_type: str = None):
        self.validation_type = validation_type
        super().__init__(message, "VALIDATION_ERROR")

class TimeoutException(DebugAgentException):
    """超时异常"""

    def __init__(self, message: str, operation: str = None, timeout_seconds: int = None):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(message, "TIMEOUT_ERROR")

class ResourceLimitException(DebugAgentException):
    """资源限制异常"""

    def __init__(self, message: str, resource_type: str = None, limit_value: int = None):
        self.resource_type = resource_type
        self.limit_value = limit_value
        super().__init__(message, "RESOURCE_LIMIT_ERROR")