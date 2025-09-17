"""
Interface Definitions for Debug Agent
定义项目中使用的主要接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import (
    AnalysisResult, TestCase, RepairResult, TestResults,
    AnalysisContext, ValidationResult, Metrics
)

class AnalysisInterface(ABC):
    """分析接口 - 所有分析器必须实现"""

    @abstractmethod
    def analyze(self, target: Any, context: Optional[AnalysisContext] = None) -> List[AnalysisResult]:
        """执行分析并返回结果"""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """获取支持的分析类型"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """获取分析器能力描述"""
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """验证输入数据"""
        pass

class RepairInterface(ABC):
    """修复接口 - 所有修复器必须实现"""

    @abstractmethod
    def repair(self, code: str, issues: List[AnalysisResult]) -> RepairResult:
        """修复代码问题"""
        pass

    @abstractmethod
    def get_repair_strategies(self) -> List[str]:
        """获取支持的修复策略"""
        pass

    @abstractmethod
    def validate_repair(self, original_code: str, repaired_code: str) -> ValidationResult:
        """验证修复结果"""
        pass

    @abstractmethod
    def estimate_repair_confidence(self, issues: List[AnalysisResult]) -> float:
        """估计修复置信度"""
        pass

class TestInterface(ABC):
    """测试接口 - 所有测试相关组件必须实现"""

    @abstractmethod
    def generate_tests(self, code: str) -> List[TestCase]:
        """生成测试用例"""
        pass

    @abstractmethod
    def run_tests(self, tests: List[TestCase], code: str) -> TestResults:
        """运行测试用例"""
        pass

    @abstractmethod
    def validate_test_results(self, results: TestResults) -> ValidationResult:
        """验证测试结果"""
        pass

class ReportInterface(ABC):
    """报告接口 - 所有报告生成器必须实现"""

    @abstractmethod
    def generate_report(self, data: Dict[str, Any], format_type: str) -> str:
        """生成报告"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """获取支持的报告格式"""
        pass

class WorkflowInterface(ABC):
    """工作流接口 - 所有问题处理流程必须实现"""

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        pass

    @abstractmethod
    def get_workflow_info(self) -> Dict[str, Any]:
        """获取工作流信息"""
        pass

    @abstractmethod
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """验证上下文"""
        pass

class MetricsInterface(ABC):
    """指标接口 - 所有指标收集器必须实现"""

    @abstractmethod
    def collect_metrics(self, operation: str, data: Dict[str, Any]) -> Metrics:
        """收集性能指标"""
        pass

    @abstractmethod
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        pass

    @abstractmethod
    def reset_metrics(self) -> None:
        """重置指标"""
        pass