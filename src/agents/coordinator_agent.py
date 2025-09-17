"""
Coordinator Agent Implementation
协调Agent的实现 - 负责整体协调和决策
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from ..core.base_agent import BaseAgent
from ..core.models import (
    AgentConfig, AnalysisResult, AnalysisContext, Strategy,
    SeverityLevel, IssueType, ComplexityLevel, Metrics, ValidationResult
)
from ..core.exceptions import DebugAgentException, AnalysisException
from ..core.constants import DEFAULT_CONFIG
from .static_analysis_agent import StaticAnalysisAgent
from .test_driven_repair_agent import TestDrivenRepairAgent


class CoordinatorAgent(BaseAgent):
    """协调Agent - 负责整体协调和决策"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.static_agent = StaticAnalysisAgent(config)
        self.repair_agent = TestDrivenRepairAgent(config)
        self.decision_engine = DecisionEngine()
        self.workflow_orchestrator = WorkflowOrchestrator()

    def analyze(self, target: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """实现基类的抽象方法"""
        code = str(target)
        return self.analyze_and_repair(code, None, context)

    def analyze_and_repair(self,
                          code: str,
                          file_path: str = None,
                          strategy: Strategy = Strategy.AUTO,
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        协调执行分析和修复

        Args:
            code: 要分析和修复的代码
            file_path: 文件路径（可选）
            strategy: 执行策略
            context: 额外上下文信息

        Returns:
            协调执行结果
        """
        self.start_execution()

        try:
            # 创建分析上下文
            analysis_context = self._create_analysis_context(code, file_path, context)

            # 决定执行策略
            if strategy == Strategy.AUTO:
                strategy = self.decision_engine.make_strategy_decision(analysis_context)

            self.logger.info(f"Selected strategy: {strategy.value}")

            # 执行相应的工作流
            if strategy == Strategy.STATIC_ONLY:
                result = self._execute_static_only_workflow(analysis_context)
            elif strategy == Strategy.TEST_DRIVEN_ONLY:
                result = self._execute_test_driven_workflow(analysis_context)
            else:  # HYBRID
                result = self._execute_hybrid_workflow(analysis_context)

            # 添加协调信息
            result['coordination_info'] = {
                'strategy_used': strategy.value,
                'context_analysis': {
                    'complexity_level': analysis_context.complexity_level.value,
                    'file_type': analysis_context.file_type,
                    'code_size': analysis_context.code_size,
                    'dependencies_count': len(analysis_context.dependencies)
                },
                'decision_factors': self.decision_engine.get_last_decision_factors(),
                'execution_summary': self._generate_execution_summary(result)
            }

            # 更新指标
            self._update_metrics(result)

            # 记录执行
            self.record_execution("coordination", {
                "success": result.get('overall_success', False),
                "strategy": strategy.value,
                "issues_found": result.get('total_issues', 0),
                "repairs_applied": len(result.get('applied_repairs', []))
            })

            return result

        except Exception as e:
            error_result = self.handle_error(e, {
                "code_length": len(code) if code else 0,
                "strategy": strategy.value if strategy else "unknown"
            })
            self.record_execution("coordination", error_result)
            return error_result

        finally:
            self.end_execution()

    def get_capabilities(self) -> List[str]:
        """获取协调Agent能力"""
        return [
            'strategy_decision',
            'workflow_orchestration',
            'result_integration',
            'quality_assessment',
            'multi_agent_coordination',
            'context_analysis',
            'performance_optimization'
        ]

    def _create_analysis_context(self, code: str, file_path: str, context: Optional[Dict[str, Any]] = None) -> AnalysisContext:
        """创建分析上下文"""
        complexity_level = self._assess_complexity(code)
        file_type = self._determine_file_type(file_path)
        dependencies = self._extract_dependencies(code)

        return AnalysisContext(
            code=code,
            file_path=file_path,
            complexity_level=complexity_level,
            file_type=file_type,
            code_size=len(code),
            dependencies=dependencies,
            metadata=context or {}
        )

    def _assess_complexity(self, code: str) -> ComplexityLevel:
        """评估代码复杂度"""
        import ast

        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])

            # 统计语法元素
            functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            loops = len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))])
            conditionals = len([node for node in ast.walk(tree) if isinstance(node, ast.If)])

            # 计算复杂度分数
            complexity_score = (
                (total_lines * 0.1) +
                (functions * 2) +
                (classes * 3) +
                (loops * 1.5) +
                (conditionals * 1)
            )

            # 根据分数确定复杂度级别
            if complexity_score < 20:
                return ComplexityLevel.LOW
            elif complexity_score < 50:
                return ComplexityLevel.MEDIUM
            elif complexity_score < 100:
                return ComplexityLevel.HIGH
            else:
                return ComplexityLevel.VERY_HIGH

        except Exception:
            return ComplexityLevel.MEDIUM

    def _determine_file_type(self, file_path: str) -> str:
        """确定文件类型"""
        if not file_path:
            return 'unknown'

        import os
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        file_type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }

        return file_type_map.get(ext, 'unknown')

    def _extract_dependencies(self, code: str) -> List[str]:
        """提取依赖关系"""
        import ast
        dependencies = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)

        except Exception:
            pass

        return dependencies

    def _execute_static_only_workflow(self, context: AnalysisContext) -> Dict[str, Any]:
        """执行纯静态分析工作流"""
        self.logger.info("Executing static-only workflow")

        # 执行静态分析
        static_result = self.static_agent.analyze(context.code, {'file_path': context.file_path})

        # 整理结果
        all_issues = (
            static_result.get('security_issues', []) +
            static_result.get('quality_issues', []) +
            static_result.get('performance_issues', [])
        )

        result = {
            'strategy': 'STATIC_ONLY',
            'static_analysis_results': static_result,
            'repair_results': None,
            'final_code': context.code,
            'total_issues': len(all_issues),
            'overall_success': True,
            'applied_repairs': [],
            'quality_improvement': {
                'issues_identified': len(all_issues),
                'critical_issues': len([i for i in all_issues if i.severity == SeverityLevel.CRITICAL]),
                'quality_score': static_result.get('overall_score', 0)
            }
        }

        return result

    def _execute_test_driven_workflow(self, context: AnalysisContext) -> Dict[str, Any]:
        """执行纯测试驱动工作流"""
        self.logger.info("Executing test-driven workflow")

        # 执行测试驱动修复
        repair_result = self.repair_agent.analyze_and_repair(context.code, context={'file_path': context.file_path})

        # 统计问题
        total_issues = len(repair_result.get('applied_repairs', []))

        result = {
            'strategy': 'TEST_DRIVEN_ONLY',
            'static_analysis_results': None,
            'repair_results': repair_result,
            'final_code': repair_result.get('repaired_code', context.code),
            'total_issues': total_issues,
            'overall_success': repair_result.get('repair_success', False),
            'applied_repairs': repair_result.get('applied_repairs', []),
            'quality_improvement': {
                'repairs_applied': total_issues,
                'test_improvement': repair_result.get('improvement_metrics', {}),
                'repair_confidence': repair_result.get('confidence', 0)
            }
        }

        return result

    def _execute_hybrid_workflow(self, context: AnalysisContext) -> Dict[str, Any]:
        """执行混合工作流"""
        self.logger.info("Executing hybrid workflow")

        # 步骤1: 执行静态分析
        static_result = self.static_agent.analyze(context.code, {'file_path': context.file_path})

        # 提取问题
        all_issues = (
            static_result.get('security_issues', []) +
            static_result.get('quality_issues', []) +
            static_result.get('performance_issues', [])
        )

        # 步骤2: 如果发现问题，执行修复
        repair_result = None
        final_code = context.code

        if all_issues:
            repair_result = self.repair_agent.analyze_and_repair(
                context.code, all_issues, {'file_path': context.file_path}
            )
            final_code = repair_result.get('repaired_code', context.code)

        # 步骤3: 如果修复了代码，重新进行静态分析
        final_static_result = None
        if final_code != context.code:
            final_static_result = self.static_agent.analyze(final_code, {'file_path': context.file_path})

        result = {
            'strategy': 'HYBRID',
            'static_analysis_results': {
                'initial': static_result,
                'final': final_static_result
            },
            'repair_results': repair_result,
            'final_code': final_code,
            'total_issues': len(all_issues),
            'overall_success': len(all_issues) > 0 and (repair_result.get('repair_success', False) if repair_result else True),
            'applied_repairs': repair_result.get('applied_repairs', []) if repair_result else [],
            'quality_improvement': {
                'issues_identified': len(all_issues),
                'initial_quality_score': static_result.get('overall_score', 0),
                'final_quality_score': final_static_result.get('overall_score', 0) if final_static_result else static_result.get('overall_score', 0),
                'quality_improvement': (final_static_result.get('overall_score', 0) if final_static_result else static_result.get('overall_score', 0)) - static_result.get('overall_score', 0),
                'repairs_applied': len(repair_result.get('applied_repairs', [])) if repair_result else 0
            }
        }

        return result

    def _generate_execution_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行摘要"""
        return {
            'execution_successful': result.get('overall_success', False),
            'issues_found': result.get('total_issues', 0),
            'repairs_applied': len(result.get('applied_repairs', [])),
            'quality_improvement': result.get('quality_improvement', {}),
            'strategy_effectiveness': self._assess_strategy_effectiveness(result)
        }

    def _assess_strategy_effectiveness(self, result: Dict[str, Any]) -> float:
        """评估策略效果"""
        strategy = result.get('strategy', 'UNKNOWN')
        quality_improvement = result.get('quality_improvement', {})

        if strategy == 'STATIC_ONLY':
            # 基于问题识别效果
            return min(1.0, quality_improvement.get('issues_identified', 0) / 10.0)
        elif strategy == 'TEST_DRIVEN_ONLY':
            # 基于修复效果
            return quality_improvement.get('repair_confidence', 0)
        elif strategy == 'HYBRID':
            # 基于综合效果
            initial_score = quality_improvement.get('initial_quality_score', 0)
            final_score = quality_improvement.get('final_quality_score', 0)
            score_improvement = final_score - initial_score
            return min(1.0, max(0.0, score_improvement / 50.0))

        return 0.0

    def _update_metrics(self, result: Dict[str, Any]):
        """更新性能指标"""
        self.metrics.issues_found = result.get('total_issues', 0)
        self.metrics.accuracy_rate = result.get('coordination_info', {}).get('execution_summary', {}).get('strategy_effectiveness', 0)

    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有Agent的状态"""
        return {
            'coordinator': {
                'execution_count': len(self.execution_history),
                'success_rate': self._calculate_success_rate(),
                'capabilities': self.get_capabilities()
            },
            'static_agent': {
                'execution_count': len(self.static_agent.execution_history),
                'success_rate': self.static_agent._calculate_success_rate(),
                'capabilities': self.static_agent.get_capabilities()
            },
            'repair_agent': {
                'execution_count': len(self.repair_agent.execution_history),
                'success_rate': self.repair_agent._calculate_success_rate(),
                'capabilities': self.repair_agent.get_capabilities()
            }
        }


class DecisionEngine:
    """决策引擎 - 负责策略决策"""

    def __init__(self):
        self.last_decision_factors = None

    def make_strategy_decision(self, context: AnalysisContext) -> Strategy:
        """基于上下文做出策略决策"""
        factors = self._extract_decision_factors(context)
        self.last_decision_factors = factors

        # 计算各个策略的得分
        static_score = self._calculate_static_score(factors)
        test_driven_score = self._calculate_test_driven_score(factors)
        hybrid_score = self._calculate_hybrid_score(factors)

        # 选择最优策略
        scores = {
            Strategy.STATIC_ONLY: static_score,
            Strategy.TEST_DRIVEN_ONLY: test_driven_score,
            Strategy.HYBRID: hybrid_score
        }

        selected_strategy = max(scores, key=scores.get)
        return selected_strategy

    def get_last_decision_factors(self) -> Optional[Dict[str, float]]:
        """获取上一次决策的因子"""
        return self.last_decision_factors

    def _extract_decision_factors(self, context: AnalysisContext) -> Dict[str, float]:
        """提取决策因子"""
        return {
            'code_complexity': context.complexity_level.value / 4.0,  # 归一化到0-1
            'file_importance': self._assess_file_importance(context.file_path),
            'issue_severity': self._assess_potential_issue_severity(context.code),
            'performance_requirements': self._assess_performance_requirements(context),
            'testing_coverage': self._assess_testing_coverage(context)
        }

    def _assess_file_importance(self, file_path: str) -> float:
        """评估文件重要性"""
        if not file_path:
            return 0.5

        important_keywords = ['main', 'app', 'core', 'api', 'service', 'controller']
        filename = file_path.lower()

        importance = 0.5  # 基础重要性
        for keyword in important_keywords:
            if keyword in filename:
                importance += 0.1

        return min(1.0, importance)

    def _assess_potential_issue_severity(self, code: str) -> float:
        """评估潜在问题严重性"""
        # 简单的关键词匹配
        high_severity_keywords = ['password', 'secret', 'key', 'token', 'sql']
        medium_severity_keywords = ['todo', 'fixme', 'hack', 'temp']

        severity_score = 0.0
        code_lower = code.lower()

        for keyword in high_severity_keywords:
            if keyword in code_lower:
                severity_score += 0.2

        for keyword in medium_severity_keywords:
            if keyword in code_lower:
                severity_score += 0.1

        return min(1.0, severity_score)

    def _assess_performance_requirements(self, context: AnalysisContext) -> float:
        """评估性能需求"""
        # 根据文件类型和复杂度评估性能需求
        if context.file_type in ['python', 'javascript', 'java']:
            return min(1.0, context.complexity_level.value / 4.0)
        return 0.3

    def _assess_testing_coverage(self, context: AnalysisContext) -> float:
        """评估测试覆盖需求"""
        # 根据代码复杂度评估测试需求
        return min(1.0, context.complexity_level.value / 4.0)

    def _calculate_static_score(self, factors: Dict[str, float]) -> float:
        """计算静态分析策略得分"""
        # 静态分析在低复杂度、低严重性问题时效果更好
        complexity_factor = 1.0 - factors['code_complexity']
        severity_factor = 1.0 - factors['issue_severity']

        return (complexity_factor * 0.6 + severity_factor * 0.4)

    def _calculate_test_driven_score(self, factors: Dict[str, float]) -> float:
        """计算测试驱动策略得分"""
        # 测试驱动在高复杂度、高测试需求时效果更好
        complexity_factor = factors['code_complexity']
        testing_factor = factors['testing_coverage']

        return (complexity_factor * 0.5 + testing_factor * 0.5)

    def _calculate_hybrid_score(self, factors: Dict[str, float]) -> float:
        """计算混合策略得分"""
        # 混合策略在中等复杂度时效果最好
        complexity_factor = 1.0 - abs(factors['code_complexity'] - 0.5)
        overall_risk = (factors['code_complexity'] + factors['issue_severity']) / 2.0
        risk_factor = min(1.0, overall_risk)

        return (complexity_factor * 0.4 + risk_factor * 0.6)


class WorkflowOrchestrator:
    """工作流编排器"""

    def __init__(self):
        self.active_workflows = {}

    def execute_workflow(self, workflow_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定工作流"""
        workflow_id = f"{workflow_type}_{time.time()}"
        self.active_workflows[workflow_id] = {
            'type': workflow_type,
            'context': context,
            'start_time': time.time(),
            'status': 'running'
        }

        try:
            # 这里简化了工作流执行逻辑
            # 在实际实现中，会有更复杂的工作流管理
            result = {
                'workflow_id': workflow_id,
                'workflow_type': workflow_type,
                'success': True,
                'execution_time': time.time() - self.active_workflows[workflow_id]['start_time']
            }

            self.active_workflows[workflow_id]['status'] = 'completed'
            return result

        except Exception as e:
            self.active_workflows[workflow_id]['status'] = 'failed'
            raise e