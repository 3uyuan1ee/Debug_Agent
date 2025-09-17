
"""



Data Models for Debug Agent
定义项目中使用的所有数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class SeverityLevel(Enum):
    """严重程度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueType(Enum):
    """问题类型"""
    SECURITY = "security"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    LOGIC = "logic"
    STYLE = "style"

class Strategy(Enum):
    """执行策略"""
    STATIC_ONLY = "static_only"
    TEST_DRIVEN_ONLY = "test_driven_only"
    HYBRID = "hybrid"
    AUTO = "auto"

class ComplexityLevel(Enum):
    """复杂度级别"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4

class TestType(Enum):
    """测试类型"""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"

@dataclass
class AnalysisResult:
    """分析结果基类"""
    file_path: str = ""
    line_number: int = 0
    issue_type: IssueType = IssueType.QUALITY
    severity: SeverityLevel = SeverityLevel.LOW
    description: str = ""
    suggestion: str = ""
    confidence: float = 0.0
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityIssue(AnalysisResult):
    """安全问题"""
    cwe_id: Optional[str] = None
    vulnerability_type: Optional[str] = None
    attack_vector: Optional[str] = None

@dataclass
class QualityIssue(AnalysisResult):
    """质量问题"""
    quality_metric: str = ""
    threshold_value: float = 0.0
    actual_value: float = 0.0

@dataclass
class PerformanceIssue(AnalysisResult):
    """性能问题"""
    performance_metric: str = ""
    impact_level: SeverityLevel = SeverityLevel.MEDIUM
    optimization_suggestion: str = ""

@dataclass
class TestCase:
    """测试用例"""
    id: str = ""
    name: str = ""
    description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Any = None
    test_type: TestType = TestType.UNIT
    generated_by: str = "ai"  # ai, human, template
    code_template: Optional[str] = None
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None

@dataclass
class TestResults:
    """测试结果"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    execution_time: float = 0.0
    test_details: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RepairResult:
    """修复结果"""
    original_code: str = ""
    repaired_code: str = ""
    applied_fixes: List[str] = field(default_factory=list)
    success: bool = False
    validation_passed: bool = False
    performance_impact: Dict[str, float] = field(default_factory=dict)
    side_effects: List[str] = field(default_factory=list)
    confidence: float = 0.0
    repair_strategy: str = ""

@dataclass
class AnalysisContext:
    """分析上下文"""
    code: str = ""
    file_path: Optional[str] = None
    complexity_level: ComplexityLevel = ComplexityLevel.LOW
    file_type: str = ""
    code_size: int = 0
    dependencies: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentConfig:
    """Agent配置基类"""
    name: str
    version: str
    enabled: bool = True
    log_level: str = "INFO"
    ai_model: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    config_file: Optional[str] = None

@dataclass
class DecisionFactors:
    """决策因子"""
    code_complexity: float = 0.0
    file_importance: float = 0.0
    issue_severity: float = 0.0
    performance_requirements: float = 0.0
    testing_coverage: float = 0.0

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool = False
    confidence: float = 0.0
    issues_found: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    execution_time: float = 0.0

@dataclass
class Metrics:
    """性能指标"""
    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    issues_found: int = 0
    accuracy_rate: float = 0.0
    precision: float = 0.0
    recall: float = 0.0