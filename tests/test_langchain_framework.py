"""
LangChain Framework Tests
LangChain框架测试，验证基于LangChain的AI Agent功能
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
from src.agents.langchain_debug_agent import LangChainDebugAgent
from src.agents.intelligent_coordinator import IntelligentCoordinator
from src.chains.analysis_chains import create_analysis_chains
from src.memory.memory_manager import MemoryManager


class TestLangChainFramework:
    """LangChain框架测试"""

    def test_langchain_agent_creation(self):
        """测试LangChain Agent创建"""
        config = get_config()
        config.ai_model = "gpt-4"  # 使用可用的模型

        # 测试LangChain Debug Agent
        langchain_agent = LangChainDebugAgent(config)
        assert langchain_agent.config == config
        assert langchain_agent.llm is not None
        assert langchain_agent.memory is not None
        assert len(langchain_agent.tools) > 0
        assert langchain_agent.agent is not None

    def test_intelligent_coordinator_creation(self):
        """测试智能协调器创建"""
        config = get_config()
        config.ai_model = "gpt-4"

        coordinator = IntelligentCoordinator(config)
        assert coordinator.config == config
        assert coordinator.llm is not None
        assert coordinator.master_agent is not None
        assert coordinator.conversation_memory is not None
        assert coordinator.project_memory is not None

    def test_analysis_chains_creation(self):
        """测试分析链创建"""
        llm_config = {'model': 'gpt-4'}
        chains = create_analysis_chains(llm_config)

        # 验证所有链都被创建
        expected_chains = ['security', 'quality', 'performance', 'comprehensive', 'repair', 'optimization', 'test_generation']
        for chain_name in expected_chains:
            assert chain_name in chains
            assert chains[chain_name] is not None

    def test_memory_manager_creation(self):
        """测试记忆管理器创建"""
        config = get_config()
        config.ai_model = "gpt-4"

        memory_manager = MemoryManager(config)
        assert memory_manager.config == config
        assert memory_manager.llm is not None
        assert memory_manager.conversation_memory is not None
        assert memory_manager.summary_memory is not None
        assert memory_manager.kg_memory is not None
        assert memory_manager.project_memory is not None

    def test_memory_conversation_management(self):
        """测试对话记忆管理"""
        config = get_config()
        config.ai_model = "gpt-4"
        memory_manager = MemoryManager(config)

        # 添加对话
        user_input = "请分析这段代码的安全性"
        assistant_response = "代码分析完成，发现2个安全问题"
        memory_manager.add_conversation(user_input, assistant_response)

        # 验证对话记忆
        conversation_vars = memory_manager.conversation_memory.load_memory_variables({})
        assert 'chat_history' in conversation_vars
        assert len(conversation_vars['chat_history']) >= 2

    def test_memory_project_management(self):
        """测试项目记忆管理"""
        config = get_config()
        config.ai_model = "gpt-4"
        memory_manager = MemoryManager(config)

        # 添加分析结果
        file_path = "test.py"
        analysis_result = {
            'issues': [{'type': 'security', 'severity': 'high'}],
            'total_issues': 1,
            'overall_score': 85
        }
        memory_manager.add_analysis_result(file_path, analysis_result)

        # 验证项目记忆
        assert file_path in memory_manager.project_memory.file_analyses
        assert memory_manager.project_memory.file_analyses[file_path]['analysis_count'] == 1

        # 添加修复结果
        issue_id = "security_issue_1"
        repair_result = {
            'success': True,
            'strategy': 'hybrid',
            'repaired_code': 'fixed code'
        }
        memory_manager.add_repair_result(issue_id, repair_result)

        # 验证修复历史
        assert issue_id in memory_manager.project_memory.repair_history

    def test_memory_search_and_context(self):
        """测试记忆搜索和上下文获取"""
        config = get_config()
        config.ai_model = "gpt-4"
        memory_manager = MemoryManager(config)

        # 添加一些测试数据
        memory_manager.add_conversation(
            "代码有问题",
            "发现了3个质量问题",
            {'category': 'quality'}
        )

        memory_manager.add_analysis_result(
            "test.py",
            {'issues': [{'type': 'quality'}], 'total_issues': 1}
        )

        # 测试搜索
        results = memory_manager.search_memory("quality")
        assert len(results) > 0

        # 测试上下文获取
        context = memory_manager.get_relevant_context("质量分析")
        assert 'recent_conversation' in context
        assert 'project_memory' in context

    def test_memory_stats_and_export(self):
        """测试记忆统计和导出"""
        config = get_config()
        config.ai_model = "gpt-4"
        memory_manager = MemoryManager(config)

        # 添加测试数据
        memory_manager.add_conversation("test", "response")
        memory_manager.add_analysis_result("test.py", {'issues': [], 'total_issues': 0})

        # 获取统计信息
        stats = memory_manager.get_memory_stats()
        assert 'conversation_messages' in stats
        assert 'project_memory' in stats
        assert 'long_term_memory' in stats

        # 导出记忆
        exported_data = memory_manager.export_memory()
        assert 'conversation_memory' in exported_data
        assert 'project_memory' in exported_data
        assert 'memory_stats' in exported_data

    def test_langchain_agent_capabilities(self):
        """测试LangChain Agent能力"""
        config = get_config()
        config.ai_model = "gpt-4"
        agent = LangChainDebugAgent(config)

        capabilities = agent.get_capabilities()
        expected_capabilities = [
            'intelligent_code_analysis',
            'natural_language_interaction',
            'context_aware_analysis',
            'automated_repair_suggestions',
            'multi_strategy_decision',
            'conversation_memory',
            'tool_integration',
            'continuous_learning'
        ]

        for capability in expected_capabilities:
            assert capability in capabilities

    def test_intelligent_coordinator_capabilities(self):
        """测试智能协调器能力"""
        config = get_config()
        config.ai_model = "gpt-4"
        coordinator = IntelligentCoordinator(config)

        capabilities = coordinator.get_capabilities()
        expected_capabilities = [
            'intelligent_code_analysis',
            'adaptive_strategy_selection',
            'pattern_recognition',
            'continuous_learning',
            'multi_tool_integration',
            'context_aware_decision',
            'memory_management',
            'quality_optimization',
            'predictive_analysis',
            'automated_repair'
        ]

        for capability in expected_capabilities:
            assert capability in capabilities

    def test_intelligent_coordinator_metrics(self):
        """测试智能协调器指标"""
        config = get_config()
        config.ai_model = "gpt-4"
        coordinator = IntelligentCoordinator(config)

        # 获取智能指标
        metrics = coordinator.get_intelligence_metrics()
        expected_metrics = [
            'learning_capacity',
            'pattern_recognition',
            'decision_accuracy',
            'memory_efficiency',
            'tool_utilization',
            'adaptation_level'
        ]

        for metric in expected_metrics:
            assert metric in metrics

    def test_analysis_chain_invocation(self):
        """测试分析链调用（模拟）"""
        llm_config = {'model': 'gpt-4'}
        chains = create_analysis_chains(llm_config)

        # 模拟安全分析
        test_code = "def test_function(): pass"
        result = chains['security'].invoke({
            'code': test_code,
            'language': 'python',
            'context': {'file_path': 'test.py'}
        })

        assert 'security_analysis' in result
        assert 'raw_output' in result

    def test_memory_optimization(self):
        """测试记忆优化"""
        config = get_config()
        config.ai_model = "gpt-4"
        memory_manager = MemoryManager(config)

        # 添加大量测试数据
        for i in range(150):
            memory_manager.add_conversation(f"test input {i}", f"test response {i}")

        # 执行优化
        memory_manager.optimize_memory()

        # 验证优化效果
        stats = memory_manager.get_memory_stats()
        assert stats['conversation_messages'] <= 1000  # 验证消息数量限制

    def test_agent_memory_usage(self):
        """测试Agent记忆使用"""
        config = get_config()
        config.ai_model = "gpt-4"
        agent = LangChainDebugAgent(config)

        # 获取记忆使用情况
        memory_usage = agent.get_memory_usage()
        assert 'total_messages' in memory_usage
        assert 'memory_type' in memory_usage
        assert 'conversation_history' in memory_usage

    def test_coordinator_memory_export(self):
        """测试协调器记忆导出"""
        config = get_config()
        config.ai_model = "gpt-4"
        coordinator = IntelligentCoordinator(config)

        # 添加一些上下文
        coordinator.add_context_to_memory({'test': 'context'})

        # 导出记忆
        memory_data = coordinator.export_memory()
        assert 'conversation_memory' in memory_data
        assert 'summary_memory' in memory_data
        assert 'project_memory' in memory_data

    def test_code_analysis_with_langchain(self):
        """测试使用LangChain进行代码分析"""
        config = get_config()
        config.ai_model = "gpt-4"
        agent = LangChainDebugAgent(config)

        # 测试代码
        test_code = '''
def login_user(username, password):
    # 硬编码密码检查
    if password == "admin123":
        return True
    return False
'''

        try:
            # 执行分析
            result = agent.analyze_and_repair(
                code=test_code,
                strategy=Strategy.AUTO
            )

            # 验证结果结构
            assert 'langchain_info' in result
            assert 'model_used' in result['langchain_info']
            assert 'tools_used' in result['langchain_info']
            assert result['langchain_info']['model_used'] == 'gpt-4'

        except Exception as e:
            # 如果API调用失败，确保错误被正确处理
            assert 'error' in result or result.get('overall_success', False) is False

    def test_intelligent_coordination_workflow(self):
        """测试智能协调工作流"""
        config = get_config()
        config.ai_model = "gpt-4"
        coordinator = IntelligentCoordinator(config)

        # 测试代码
        test_code = '''
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        if numbers[i] > 0:
            total += numbers[i] * 2
    return total
'''

        try:
            # 执行智能协调
            result = coordinator.intelligent_analyze_and_repair(
                code=test_code,
                strategy=Strategy.AUTO
            )

            # 验证结果
            assert 'intelligent_info' in result
            assert 'model_used' in result['intelligent_info']
            assert 'memory_usage' in result['intelligent_info']
            assert result['intelligent_info']['model_used'] == 'gpt-4'

        except Exception as e:
            # 如果API调用失败，确保错误被正确处理
            assert 'error' in result or result.get('overall_success', False) is False

    def test_memory_persistence_across_sessions(self):
        """测试跨会话的记忆持久性"""
        config = get_config()
        config.ai_model = "gpt-4"
        memory_manager = MemoryManager(config)

        # 第一会话：添加数据
        memory_manager.add_conversation(
            "第一会话的问题",
            "第一会话的回答"
        )
        memory_manager.add_analysis_result(
            "persistent.py",
            {'issues': [{'type': 'persistent'}], 'total_issues': 1}
        )

        # 验证数据存在
        stats_before = memory_manager.get_memory_stats()

        # 清理对话记忆但保留项目记忆
        memory_manager.clear_memory("conversation")

        # 验证项目记忆仍然存在
        assert len(memory_manager.project_memory.file_analyses) > 0
        assert 'persistent.py' in memory_manager.project_memory.file_analyses

    def test_pattern_recognition(self):
        """测试模式识别"""
        config = get_config()
        config.ai_model = "gpt-4"
        coordinator = IntelligentCoordinator(config)

        # 测试代码模式
        test_code = '''
class User:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

def create_user(name):
    return User(name)
'''

        patterns = coordinator._recognize_patterns(test_code)
        assert isinstance(patterns, list)

        # 验证能识别到面向对象模式
        oo_patterns = [p for p in patterns if p.get('type') == 'object_oriented']
        assert len(oo_patterns) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])