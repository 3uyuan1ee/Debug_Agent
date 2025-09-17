"""
Debug Agent Core Module
包含核心架构、基础类和接口定义
"""

__version__ = "0.1.0"
__author__ = "Debug Agent Team"

from .base_agent import BaseAgent, AgentConfig
from .interfaces import AnalysisInterface, RepairInterface
from .models import (
    AnalysisResult, SecurityIssue, QualityIssue, PerformanceIssue,
    TestCase, RepairResult, AnalysisContext, Strategy, SeverityLevel, IssueType
)
from .exceptions import DebugAgentException, AnalysisException, RepairException

__all__ = [
    'BaseAgent', 'AgentConfig',
    'AnalysisInterface', 'RepairInterface',
    'AnalysisResult', 'SecurityIssue', 'QualityIssue', 'PerformanceIssue',
    'TestCase', 'RepairResult', 'AnalysisContext', 'Strategy', 'SeverityLevel', 'IssueType',
    'DebugAgentException', 'AnalysisException', 'RepairException'
]