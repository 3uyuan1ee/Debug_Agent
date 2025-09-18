"""
Mock configuration for testing LangChain Agent without API keys
测试用的模拟配置，无需API密钥
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

@dataclass
class MockAgentConfig:
    """模拟Agent配置，用于测试"""
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    log_level: str = "INFO"
    timeout: int = 300
    max_memory: int = 1024 * 1024 * 1024
    max_cpu_usage: float = 0.8
    max_file_size: int = 10 * 1024 * 1024
    supported_languages: List[str] = field(default_factory=lambda: ["python", "javascript", "java"])
    working_directory: str = field(default_factory=lambda: os.getcwd())

    # 分析配置
    enable_security_analysis: bool = True
    enable_quality_analysis: bool = True
    enable_performance_analysis: bool = True
    enable_complexity_analysis: bool = True

    # 修复配置
    enable_auto_repair: bool = False
    repair_confidence_threshold: float = 0.7
    max_repair_attempts: int = 3

    # 测试配置
    enable_test_generation: bool = True
    test_framework: str = "pytest"
    test_timeout: int = 60
    max_test_cases: int = 100

    # AI配置 - 使用模拟模型
    ai_provider: str = "mock"
    ai_model: str = "mock-model"
    ai_api_key: Optional[str] = "mock-api-key"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 2000

    # 输出配置
    output_format: str = "json"
    output_directory: str = "output"
    create_report: bool = True
    verbose_output: bool = False