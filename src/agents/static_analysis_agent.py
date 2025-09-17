"""
Static Analysis Agent Implementation
静态分析Agent的实现
"""

import ast
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..core.base_agent import BaseAgent
from ..core.models import (
    AgentConfig, AnalysisResult, SecurityIssue, QualityIssue, PerformanceIssue,
    AnalysisContext, SeverityLevel, IssueType, ComplexityLevel
)
from ..core.exceptions import AnalysisException
from ..core.constants import ANALYSIS_RULES, SUPPORTED_FILE_TYPES


class StaticAnalysisAgent(BaseAgent):
    """静态分析Agent - 负责代码静态分析"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.analyzers = self._initialize_analyzers()

    def _initialize_analyzers(self) -> Dict[str, Any]:
        """初始化所有分析器"""
        return {
            'security': SecurityAnalyzer(),
            'quality': QualityAnalyzer(),
            'performance': PerformanceAnalyzer(),
            'complexity': ComplexityAnalyzer(),
        }

    def analyze(self, target: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行静态分析

        Args:
            target: 分析目标（代码字符串或文件路径）
            context: 分析上下文

        Returns:
            分析结果字典
        """
        self.start_execution()

        try:
            # 获取代码内容
            if isinstance(target, str) and os.path.exists(target):
                code, file_path = self._read_file(target)
            else:
                code = str(target)
                file_path = context.get('file_path') if context else None

            if not self.validate_input(code):
                return self.handle_error(
                    AnalysisException("Invalid input code"),
                    {"target": str(target)}
                )

            # 创建分析上下文
            analysis_context = self._create_analysis_context(code, file_path, context)

            # 执行分析
            results = {
                'file_path': file_path,
                'code_size': len(code),
                'complexity_level': analysis_context.complexity_level.value,
                'security_issues': [],
                'quality_issues': [],
                'performance_issues': [],
                'complexity_metrics': {},
                'overall_score': 0.0,
                'suggestions': [],
                'execution_metadata': {
                    'analyzers_used': [],
                    'execution_time': 0,
                    'success': True
                }
            }

            # 执行各种分析
            for analyzer_name, analyzer in self.analyzers.items():
                if ANALYSIS_RULES.get(analyzer_name, {}).get('enabled', True):
                    try:
                        analyzer_result = analyzer.analyze(code, file_path)
                        results[f"{analyzer_name}_issues"] = analyzer_result.get('issues', [])
                        results['complexity_metrics'].update(analyzer_result.get('metrics', {}))
                        results['execution_metadata']['analyzers_used'].append(analyzer_name)
                    except Exception as e:
                        self.logger.warning(f"Analyzer {analyzer_name} failed: {e}")

            # 计算总体评分
            results['overall_score'] = self._calculate_overall_score(results)
            results['suggestions'] = self._generate_suggestions(results)

            # 更新指标
            total_issues = (
                len(results['security_issues']) +
                len(results['quality_issues']) +
                len(results['performance_issues'])
            )
            self.metrics.issues_found = total_issues

            # 记录执行
            self.record_execution("static_analysis", {
                "success": True,
                "issues_found": total_issues,
                "overall_score": results['overall_score']
            })

            return results

        except Exception as e:
            error_result = self.handle_error(e, {"target": str(target)})
            self.record_execution("static_analysis", error_result)
            return error_result

        finally:
            self.end_execution()

    def get_capabilities(self) -> List[str]:
        """获取静态分析Agent能力"""
        return [
            'security_vulnerability_detection',
            'code_quality_analysis',
            'performance_issue_detection',
            'complexity_analysis',
            'dependency_analysis',
            'code_style_checking',
            'dead_code_detection',
            'best_practices_violation'
        ]

    def _read_file(self, file_path: str) -> tuple[str, str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), file_path
        except Exception as e:
            raise AnalysisException(f"Failed to read file {file_path}: {e}")

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
        try:
            tree = ast.parse(code)

            # 计算复杂度指标
            lines = code.split('\n')
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])

            # 统计函数和类的数量
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # 简单的复杂度评估
            if total_lines < 50 and len(functions) <= 3 and len(classes) <= 1:
                return ComplexityLevel.LOW
            elif total_lines < 200 and len(functions) <= 10 and len(classes) <= 5:
                return ComplexityLevel.MEDIUM
            elif total_lines < 500 and len(functions) <= 20 and len(classes) <= 10:
                return ComplexityLevel.HIGH
            else:
                return ComplexityLevel.VERY_HIGH

        except Exception:
            return ComplexityLevel.MEDIUM

    def _determine_file_type(self, file_path: str) -> str:
        """确定文件类型"""
        if not file_path:
            return 'unknown'

        _, ext = os.path.splitext(file_path)
        return SUPPORTED_FILE_TYPES.get(ext, 'unknown')

    def _extract_dependencies(self, code: str) -> List[str]:
        """提取依赖关系"""
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

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """计算代码质量总体评分"""
        # 计算各种问题的权重
        security_issues = results['security_issues']
        quality_issues = results['quality_issues']
        performance_issues = results['performance_issues']

        # 严重程度权重
        severity_weights = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 5
        }

        total_penalty = 0
        max_penalty = 100

        # 计算安全问题的惩罚
        for issue in security_issues:
            weight = severity_weights.get(issue.severity, 1)
            total_penalty += weight * 5  # 安全问题权重更高

        # 计算质量问题的惩罚
        for issue in quality_issues:
            weight = severity_weights.get(issue.severity, 1)
            total_penalty += weight * 2

        # 计算性能问题的惩罚
        for issue in performance_issues:
            weight = severity_weights.get(issue.severity, 1)
            total_penalty += weight * 3

        # 计算最终评分
        score = max(0, max_penalty - total_penalty)
        return round(score, 2)

    def _generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 基于安全问题生成建议
        if results['security_issues']:
            suggestions.append("发现安全漏洞，建议立即修复并检查代码安全实践")

        # 基于质量问题生成建议
        if results['quality_issues']:
            suggestions.append("代码质量有待提升，建议重构和优化")

        # 基于性能问题生成建议
        if results['performance_issues']:
            suggestions.append("存在性能问题，建议优化算法和数据结构")

        # 基于复杂度生成建议
        complexity_level = ComplexityLevel(results['complexity_level'])
        if complexity_level in [ComplexityLevel.HIGH, ComplexityLevel.VERY_HIGH]:
            suggestions.append("代码复杂度过高，建议拆分函数和类")

        # 如果没有问题
        if not any([results['security_issues'], results['quality_issues'], results['performance_issues']]):
            suggestions.append("代码质量良好，继续保持")

        return suggestions


class SecurityAnalyzer:
    """安全分析器"""

    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """分析安全漏洞"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # 检查硬编码密码
            if 'password' in line.lower() and ('=' in line or ':' in line):
                if any(secret in line.lower() for secret in ['123', 'admin', 'test', 'password']):
                    issues.append(SecurityIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type=IssueType.SECURITY,
                        severity=SeverityLevel.HIGH,
                        description="Potential hardcoded password detected",
                        suggestion="Use environment variables or secure storage",
                        confidence=0.8,
                        vulnerability_type="hardcoded_credentials"
                    ))

            # 检查SQL注入风险
            if 'execute(' in line.lower() or 'cursor.execute' in line.lower():
                if '+' in line or '%' in line or 'format' in line:
                    issues.append(SecurityIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type=IssueType.SECURITY,
                        severity=SeverityLevel.HIGH,
                        description="Potential SQL injection vulnerability",
                        suggestion="Use parameterized queries",
                        confidence=0.7,
                        vulnerability_type="sql_injection"
                    ))

        return {'issues': issues, 'metrics': {'security_checks': len(lines)}}


class QualityAnalyzer:
    """质量分析器"""

    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """分析代码质量"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # 检查TODO和FIXME
            if any(keyword in line.lower() for keyword in ['todo', 'fixme', 'hack']):
                issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type=IssueType.QUALITY,
                    severity=SeverityLevel.LOW,
                    description=f"TODO/FIXME comment found: {line.strip()}",
                    suggestion="Address the TODO item or create proper issue",
                    confidence=0.9,
                    quality_metric="code_comments",
                    threshold_value=0,
                    actual_value=1
                ))

            # 检查长行
            if len(line) > 100:
                issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type=IssueType.QUALITY,
                    severity=SeverityLevel.LOW,
                    description=f"Line too long ({len(line)} characters)",
                    suggestion="Break long lines into multiple lines",
                    confidence=0.8,
                    quality_metric="line_length",
                    threshold_value=100,
                    actual_value=len(line)
                ))

        return {'issues': issues, 'metrics': {'quality_checks': len(lines)}}


class PerformanceAnalyzer:
    """性能分析器"""

    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """分析性能问题"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # 检查循环中的字符串连接
            if 'for' in line and '+' in line:
                if 'string' in line.lower() or '"' in line or "'" in line:
                    issues.append(PerformanceIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type=IssueType.PERFORMANCE,
                        severity=SeverityLevel.MEDIUM,
                        description="Inefficient string concatenation in loop",
                        suggestion="Use list comprehension or join() method",
                        confidence=0.6,
                        performance_metric="string_concatenation",
                        impact_level=SeverityLevel.MEDIUM,
                        optimization_suggestion="Use str.join() or list comprehension"
                    ))

        return {'issues': issues, 'metrics': {'performance_checks': len(lines)}}


class ComplexityAnalyzer:
    """复杂度分析器"""

    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """分析代码复杂度"""
        try:
            tree = ast.parse(code)

            # 计算圈复杂度
            complexity_metrics = {
                'total_lines': len(code.split('\n')),
                'functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                'loops': len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))]),
                'conditionals': len([node for node in ast.walk(tree) if isinstance(node, ast.If)]),
            }

            return {'issues': [], 'metrics': complexity_metrics}

        except Exception as e:
            return {'issues': [], 'metrics': {'parse_error': str(e)}}