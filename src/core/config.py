"""
Configuration Settings
系统配置文件，包含所有可配置参数
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .models import Strategy, SeverityLevel


class LogType(Enum):
    """日志类型"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    log_level: str = "INFO"
    timeout: int = 300  # 秒
    max_memory: int = 1024 * 1024 * 1024  # 1GB
    max_cpu_usage: float = 0.8  # 80%
    max_file_size: int = 10 * 1024 * 1024  # 10MB
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

    # AI配置
    ai_provider: str = "openai"
    ai_model: str = "gpt-3.5-turbo"
    ai_api_key: Optional[str] = None
    ai_temperature: float = 0.7
    ai_max_tokens: int = 2000

    # 输出配置
    output_format: str = "json"
    output_directory: str = "output"
    create_report: bool = True
    verbose_output: bool = False

    def __post_init__(self):
        """后处理，设置默认值"""
        if not self.working_directory:
            self.working_directory = os.getcwd()

        # 确保日志级别有效
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            self.log_level = "INFO"

        # 确保超时时间合理
        if self.timeout <= 0:
            self.timeout = 300

        # 确保置信度阈值在合理范围内
        if not 0.0 <= self.repair_confidence_threshold <= 1.0:
            self.repair_confidence_threshold = 0.7


@dataclass
class StaticAnalysisConfig:
    """静态分析配置"""
    # 安全分析配置
    security_enabled: bool = True
    security_severity_threshold: SeverityLevel = SeverityLevel.MEDIUM

    # 质量分析配置
    quality_enabled: bool = True
    max_line_length: int = 100
    check_todo_comments: bool = True
    check_hardcoded_credentials: bool = True

    # 性能分析配置
    performance_enabled: bool = True
    check_string_concatenation: bool = True
    check_database_queries: bool = True

    # 复杂度分析配置
    complexity_enabled: bool = True
    max_function_length: int = 50
    max_class_length: int = 200
    max_cyclomatic_complexity: int = 10

    # 依赖分析配置
    dependency_analysis_enabled: bool = True
    check_vulnerabilities: bool = True
    check_outdated_packages: bool = True


@dataclass
class TestDrivenRepairConfig:
    """测试驱动修复配置"""
    # 测试生成配置
    test_generation_enabled: bool = True
    test_framework: str = "pytest"
    test_coverage_target: float = 0.8
    max_test_cases_per_function: int = 5

    # 修复策略配置
    repair_strategies: List[str] = field(default_factory=lambda: [
        "security_repair",
        "quality_repair",
        "performance_repair",
        "logic_repair"
    ])

    # 修复限制配置
    max_repair_attempts: int = 3
    repair_confidence_threshold: float = 0.7
    allow_risky_repairs: bool = False

    # 验证配置
    run_tests_after_repair: bool = True
    require_all_tests_pass: bool = True
    test_timeout: int = 60


@dataclass
class CoordinatorConfig:
    """协调器配置"""
    # 策略选择配置
    default_strategy: str = "auto"
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        "static_only": 0.3,
        "test_driven_only": 0.3,
        "hybrid": 0.4
    })

    # 决策配置
    complexity_weight: float = 0.4
    severity_weight: float = 0.3
    file_importance_weight: float = 0.3

    # 工作流配置
    parallel_execution: bool = True
    max_workers: int = 4
    workflow_timeout: int = 600

    # 报告配置
    generate_detailed_report: bool = True
    include_execution_metrics: bool = True
    include_quality_metrics: bool = True


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.json"
        self._config_cache: Optional[AgentConfig] = None

    def load_config(self) -> AgentConfig:
        """加载配置"""
        if self._config_cache:
            return self._config_cache

        # 如果配置文件存在，从文件加载
        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                self._config_cache = AgentConfig(**config_data)
                return self._config_cache
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")

        # 否则使用默认配置
        self._config_cache = AgentConfig(
            name="DebugAgent",
            version="1.0.0",
            enabled=True,
            log_level="INFO"
        )

        return self._config_cache

    def save_config(self, config: AgentConfig) -> None:
        """保存配置到文件"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.__dict__, f, indent=2, ensure_ascii=False)

            self._config_cache = config
            print(f"配置已保存到: {self.config_file}")

        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def get_env_config(self) -> Dict[str, Any]:
        """从环境变量获取配置"""
        env_config = {}

        # API密钥
        if api_key := os.getenv("OPENAI_API_KEY"):
            env_config["ai_api_key"] = api_key

        # 日志级别
        if log_level := os.getenv("LOG_LEVEL"):
            env_config["log_level"] = log_level

        # 工作目录
        if work_dir := os.getenv("WORKING_DIRECTORY"):
            env_config["working_directory"] = work_dir

        # 超时时间
        if timeout := os.getenv("TIMEOUT"):
            try:
                env_config["timeout"] = int(timeout)
            except ValueError:
                pass

        # 输出目录
        if output_dir := os.getenv("OUTPUT_DIRECTORY"):
            env_config["output_directory"] = output_dir

        return env_config

    def create_sample_config(self, file_path: str = "config.sample.json") -> None:
        """创建示例配置文件"""
        sample_config = AgentConfig(
            name="DebugAgent",
            version="1.0.0",
            enabled=True,
            log_level="INFO",
            timeout=300,
            working_directory=os.getcwd(),
            enable_security_analysis=True,
            enable_quality_analysis=True,
            enable_performance_analysis=True,
            enable_auto_repair=False,
            repair_confidence_threshold=0.7,
            ai_provider="openai",
            ai_model="gpt-3.5-turbo",
            ai_temperature=0.7,
            output_format="json",
            output_directory="output",
            create_report=True
        )

        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config.__dict__, f, indent=2, ensure_ascii=False)

            print(f"示例配置文件已创建: {file_path}")

        except Exception as e:
            print(f"创建示例配置文件失败: {e}")


# 全局配置实例
config_manager = ConfigManager()
default_config = config_manager.load_config()


def get_config() -> AgentConfig:
    """获取全局配置"""
    return config_manager.load_config()


def update_config(updates: Dict[str, Any]) -> None:
    """更新配置"""
    config = config_manager.load_config()

    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)

    config_manager.save_config(config)


def reset_config() -> None:
    """重置为默认配置"""
    config_manager._config_cache = None
    config = config_manager.load_config()
    config_manager.save_config(config)