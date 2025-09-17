"""
Framework Tests
框架测试，验证核心功能是否正常工作
"""

import pytest
import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)
os.chdir(src_path)  # 更改工作目录到src

from src.core.config import get_config, AgentConfig
from src.core.models import Strategy, SeverityLevel, ComplexityLevel
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.static_analysis_agent import StaticAnalysisAgent
from src.agents.test_driven_repair_agent import TestDrivenRepairAgent


class TestAgentFramework:
    """Agent框架测试"""

    def test_config_loading(self):
        """测试配置加载"""
        config = get_config()
        assert isinstance(config, AgentConfig)
        assert config.name == "DebugAgent"
        assert config.version == "1.0.0"
        assert config.enabled is True

    def test_agent_creation(self):
        """测试Agent创建"""
        config = get_config()

        # 测试静态分析Agent
        static_agent = StaticAnalysisAgent(config)
        assert static_agent.config == config
        assert len(static_agent.get_capabilities()) > 0

        # 测试测试驱动修复Agent
        repair_agent = TestDrivenRepairAgent(config)
        assert repair_agent.config == config
        assert len(repair_agent.get_capabilities()) > 0

        # 测试协调器Agent
        coordinator = CoordinatorAgent(config)
        assert coordinator.config == config
        assert len(coordinator.get_capabilities()) > 0

    def test_coordinator_capabilities(self):
        """测试协调器能力"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        capabilities = coordinator.get_capabilities()
        expected_capabilities = [
            'strategy_decision',
            'workflow_orchestration',
            'result_integration',
            'quality_assessment',
            'multi_agent_coordination',
            'context_analysis',
            'performance_optimization'
        ]

        for capability in expected_capabilities:
            assert capability in capabilities

    def test_static_analysis_capabilities(self):
        """测试静态分析能力"""
        config = get_config()
        agent = StaticAnalysisAgent(config)

        capabilities = agent.get_capabilities()
        expected_capabilities = [
            'security_vulnerability_detection',
            'code_quality_analysis',
            'performance_issue_detection',
            'complexity_analysis',
            'dependency_analysis',
            'code_style_checking',
            'dead_code_detection',
            'best_practices_violation'
        ]

        for capability in expected_capabilities:
            assert capability in capabilities

    def test_code_analysis(self):
        """测试代码分析功能"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        # 测试简单代码分析
        test_code = '''
def add(a, b):
    return a + b

# TODO: 实现减法
def subtract(a, b):
    pass
'''

        result = coordinator.analyze_and_repair(
            code=test_code,
            strategy=Strategy.STATIC_ONLY
        )

        # 验证结果结构
        assert 'strategy' in result
        assert 'static_analysis_results' in result
        assert 'total_issues' in result
        assert 'overall_success' in result
        assert result['strategy'] == 'STATIC_ONLY'

    def test_security_detection(self):
        """测试安全漏洞检测"""
        config = get_config()
        agent = StaticAnalysisAgent(config)

        # 测试包含安全问题的代码
        malicious_code = '''
def login_user(username, password):
    # 硬编码密码
    if password == "admin123":
        return True
    return False

def query_user(user_id):
    import sqlite3
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # SQL注入风险
    cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
    return cursor.fetchone()
'''

        result = agent.analyze(malicious_code, {'file_path': 'test.py'})

        # 验证安全检测结果
        assert 'security_issues' in result
        assert len(result['security_issues']) > 0

        # 检查是否检测到硬编码密码
        security_issues = result['security_issues']
        hardcoded_password_found = any(
            'password' in issue.description.lower() or
            'hardcoded' in issue.description.lower()
            for issue in security_issues
        )
        assert hardcoded_password_found

    def test_quality_analysis(self):
        """测试代码质量分析"""
        config = get_config()
        agent = StaticAnalysisAgent(config)

        # 测试包含质量问题的代码
        poor_quality_code = '''
def very_long_function_name_that_should_be_shorter(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p):
    # TODO: 重构这个函数
    # FIXME: 这个函数太长了
    if a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p:
        return True
    return False
'''

        result = agent.analyze(poor_quality_code, {'file_path': 'test.py'})

        # 验证质量分析结果
        assert 'quality_issues' in result
        assert len(result['quality_issues']) > 0

        # 检查是否检测到TODO注释
        quality_issues = result['quality_issues']
        todo_found = any(
            'todo' in issue.description.lower() or
            'fixme' in issue.description.lower()
            for issue in quality_issues
        )
        assert todo_found

    def test_context_assessment(self):
        """测试上下文评估"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        # 测试复杂度评估
        simple_code = 'def simple(): pass'
        complex_code = '''
def complex_function(data):
    result = []
    for i in range(len(data)):
        if i % 2 == 0:
            for j in range(len(data[i])):
                if data[i][j] > 0:
                    result.append(data[i][j] * 2)
                else:
                    result.append(data[i][j] * 3)
        else:
            while i > 0:
                if i % 3 == 0:
                    result.append(i * 4)
                elif i % 2 == 0:
                    result.append(i * 5)
                else:
                    result.append(i * 6)
                i -= 1
    return result

class ComplexClass:
    def method1(self, items):
        filtered_items = []
        for item in items:
            if item is not None:
                if hasattr(item, 'value'):
                    if item.value > 0:
                        filtered_items.append(item)
                    elif item.value < 0:
                        filtered_items.append(item)
                    else:
                        continue
                else:
                    filtered_items.append(item)
        return filtered_items

    def method2(self, data):
        try:
            result = []
            for i in range(len(data)):
                if i % 2 == 0:
                    result.append(data[i] * 2)
                else:
                    result.append(data[i] * 3)
            return result
        except Exception as e:
            return []

    def method3(self, condition1, condition2, condition3):
        if condition1:
            if condition2:
                if condition3:
                    return True
                else:
                    return False
            else:
                if condition3:
                    return True
                else:
                    return False
        else:
            return False
'''

        # 测试简单代码
        simple_context = coordinator._create_analysis_context(simple_code, 'simple.py')
        assert simple_context.complexity_level in [ComplexityLevel.LOW, ComplexityLevel.MEDIUM]

        # 测试复杂代码
        complex_context = coordinator._create_analysis_context(complex_code, 'complex.py')
        assert complex_context.complexity_level in [ComplexityLevel.MEDIUM, ComplexityLevel.HIGH, ComplexityLevel.VERY_HIGH]

    def test_strategy_decision(self):
        """测试策略决策"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        # 测试低复杂度代码决策
        simple_code = 'def hello(): return "world"'
        context = coordinator._create_analysis_context(simple_code, 'simple.py')

        strategy = coordinator.decision_engine.make_strategy_decision(context)
        assert strategy in [Strategy.STATIC_ONLY, Strategy.AUTO]

    def test_agent_status(self):
        """测试Agent状态获取"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        status = coordinator.get_agent_status()

        # 验证状态结构
        assert 'coordinator' in status
        assert 'static_agent' in status
        assert 'repair_agent' in status

        # 验证每个Agent的状态信息
        for agent_status in status.values():
            assert 'execution_count' in agent_status
            assert 'success_rate' in agent_status
            assert 'capabilities' in agent_status
            assert isinstance(agent_status['execution_count'], int)
            assert isinstance(agent_status['success_rate'], float)
            assert isinstance(agent_status['capabilities'], list)

    def test_error_handling(self):
        """测试错误处理"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        # 测试无效代码输入
        invalid_code = "def invalid_syntax(\n    return None"

        result = coordinator.analyze_and_repair(
            code=invalid_code,
            strategy=Strategy.STATIC_ONLY
        )

        # 验证错误处理
        assert 'error' in result or result.get('overall_success', False) is False

    def test_file_type_detection(self):
        """测试文件类型检测"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        # 测试不同文件类型
        test_cases = [
            ('test.py', 'python'),
            ('test.js', 'javascript'),
            ('test.ts', 'typescript'),
            ('test.java', 'java'),
            ('unknown.xyz', 'unknown')
        ]

        for file_path, expected_type in test_cases:
            detected_type = coordinator._determine_file_type(file_path)
            assert detected_type == expected_type

    def test_dependency_extraction(self):
        """测试依赖提取"""
        config = get_config()
        coordinator = CoordinatorAgent(config)

        # 测试包含导入的代码
        code_with_imports = '''
import os
import sys
from typing import List, Dict
from datetime import datetime
import numpy as np

def main():
    pass
'''

        dependencies = coordinator._extract_dependencies(code_with_imports)

        # 验证提取的依赖
        expected_deps = ['os', 'sys', 'typing', 'datetime', 'numpy']
        for dep in expected_deps:
            assert dep in dependencies


if __name__ == '__main__':
    pytest.main([__file__, '-v'])