"""
Debug Agent - AI驱动的代码缺陷检测与修复工具
"""

__version__ = "1.0.0"
__author__ = "Debug Agent Team"
__email__ = "team@debugagent.com"
__description__ = "AI驱动的代码缺陷检测与修复工具"

# 导入核心组件
from .core.config import get_config, AgentConfig
from .core.models import Strategy, SeverityLevel, ComplexityLevel
from .agents.coordinator_agent import CoordinatorAgent

# 导入主要功能
from .cli import cli

__all__ = [
    'get_config',
    'AgentConfig',
    'Strategy',
    'SeverityLevel',
    'ComplexityLevel',
    'CoordinatorAgent',
    'cli',
    '__version__',
]