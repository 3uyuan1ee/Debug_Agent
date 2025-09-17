"""
Base Agent Class
所有Agent的基类，提供通用功能
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

from .models import AgentConfig, Metrics, ValidationResult
from .exceptions import DebugAgentException, TimeoutException
from .constants import DEFAULT_CONFIG


class BaseAgent(ABC):
    """所有Agent的基类"""

    def __init__(self, config: AgentConfig):
        """
        初始化Agent

        Args:
            config: Agent配置
        """
        self.config = config
        self.logger = self._setup_logger()
        self.metrics = Metrics(
            execution_time=0.0,
            memory_usage=0.0,
            cpu_usage=0.0,
            issues_found=0,
            accuracy_rate=0.0,
            precision=0.0,
            recall=0.0
        )
        self.execution_history = []
        self.start_time = None

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        logger.setLevel(getattr(logging, self.config.log_level))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @abstractmethod
    def analyze(self, target: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析目标并返回结果

        Args:
            target: 分析目标
            context: 分析上下文

        Returns:
            分析结果字典
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        获取Agent能力列表

        Returns:
            能力列表
        """
        pass

    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据

        Returns:
            验证结果
        """
        try:
            if input_data is None:
                return False

            # 基本类型检查
            if isinstance(input_data, (str, dict, list)):
                return len(str(input_data)) > 0

            return True
        except Exception as e:
            self.logger.warning(f"Input validation failed: {e}")
            return False

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        统一错误处理

        Args:
            error: 异常对象
            context: 错误上下文

        Returns:
            错误响应字典
        """
        error_info = {
            "error": str(error),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "agent": self.__class__.__name__
        }

        if context:
            error_info["context"] = context

        if isinstance(error, DebugAgentException):
            error_info["error_code"] = error.error_code
            error_info["error_type"] = error.__class__.__name__

        self.logger.error(f"Agent error: {error_info}")
        return error_info

    def execute_with_timeout(self, func, *args, timeout: int = None, **kwargs):
        """
        带超时的执行函数

        Args:
            func: 要执行的函数
            args: 函数参数
            timeout: 超时时间（秒）
            kwargs: 函数关键字参数

        Returns:
            函数执行结果
        """
        import signal
        from functools import wraps

        def timeout_handler(signum, frame):
            raise TimeoutException(f"Operation timed out after {timeout} seconds")

        @wraps(func)
        def wrapper(*args, **kwargs):
            if timeout:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                if timeout:
                    signal.alarm(0)

        return wrapper(*args, **kwargs)

    def start_execution(self):
        """开始执行计时"""
        self.start_time = time.time()
        self.logger.info(f"Starting execution of {self.__class__.__name__}")

    def end_execution(self):
        """结束执行计时"""
        if self.start_time:
            execution_time = time.time() - self.start_time
            self.metrics.execution_time = execution_time
            self.logger.info(f"Execution completed in {execution_time:.2f} seconds")
            self.start_time = None

    def record_execution(self, operation: str, result: Dict[str, Any]):
        """
        记录执行历史

        Args:
            operation: 操作名称
            result: 执行结果
        """
        execution_record = {
            "operation": operation,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "agent": self.__class__.__name__,
            "success": result.get("success", False)
        }
        self.execution_history.append(execution_record)

        # 更新指标
        if "issues_found" in result:
            self.metrics.issues_found += result["issues_found"]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取指标摘要

        Returns:
            指标摘要字典
        """
        return {
            "agent": self.__class__.__name__,
            "execution_count": len(self.execution_history),
            "success_rate": self._calculate_success_rate(),
            "avg_execution_time": self._calculate_avg_execution_time(),
            "total_issues_found": self.metrics.issues_found,
            "metrics": {
                "execution_time": self.metrics.execution_time,
                "memory_usage": self.metrics.memory_usage,
                "cpu_usage": self.metrics.cpu_usage,
                "accuracy_rate": self.metrics.accuracy_rate,
                "precision": self.metrics.precision,
                "recall": self.metrics.recall
            }
        }

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.execution_history:
            return 0.0

        successful_executions = sum(1 for record in self.execution_history if record["success"])
        return successful_executions / len(self.execution_history)

    def _calculate_avg_execution_time(self) -> float:
        """计算平均执行时间"""
        if not self.execution_history:
            return 0.0

        total_time = sum(
            record.get("execution_time", 0)
            for record in self.execution_history
            if "execution_time" in record
        )
        return total_time / len(self.execution_history)

    def validate_config(self) -> ValidationResult:
        """
        验证配置

        Returns:
            验证结果
        """
        issues = []
        suggestions = []

        # 检查必要配置
        if not self.config.name:
            issues.append("Agent name is required")

        if not self.config.version:
            issues.append("Agent version is required")

        # 检查日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.config.log_level not in valid_log_levels:
            issues.append(f"Invalid log level: {self.config.log_level}")
            suggestions.append(f"Valid log levels: {', '.join(valid_log_levels)}")

        # 检查超时设置
        if self.config.timeout <= 0:
            issues.append("Timeout must be positive")

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=1.0 if len(issues) == 0 else 0.0,
            issues_found=issues,
            suggestions=suggestions,
            execution_time=0.0
        )

    def cleanup(self):
        """清理资源"""
        self.logger.info("Cleaning up resources")
        # 子类可以重写此方法进行特定的清理操作

    def __enter__(self):
        """上下文管理器入口"""
        self.start_execution()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.end_execution()
        self.cleanup()

    def __str__(self):
        """字符串表示"""
        return f"{self.__class__.__name__}(name={self.config.name}, version={self.config.version})"

    def __repr__(self):
        """详细字符串表示"""
        return (f"{self.__class__.__name__}("
                f"name='{self.config.name}', "
                f"version='{self.config.version}', "
                f"enabled={self.config.enabled}, "
                f"log_level='{self.config.log_level}')")