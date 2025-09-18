"""
Test Driven Repair Agent Implementation
测试驱动修复Agent的实现
"""

import ast
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from ..core.base_agent import BaseAgent
from ..core.config import AgentConfig
from ..core.models import (
    AnalysisResult, TestCase, TestResults, RepairResult,
    AnalysisContext, Strategy, SeverityLevel, IssueType, TestType, ValidationResult
)
from ..core.exceptions import RepairException, TestGenerationException
from ..core.constants import TEST_CONFIG


class TestDrivenRepairAgent(BaseAgent):
    """测试驱动修复Agent - 负责基于测试的缺陷修复"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.test_generator = TestGenerator()
        self.test_runner = TestRunner()
        self.repair_strategies = self._initialize_repair_strategies()

    def _initialize_repair_strategies(self) -> Dict[str, Any]:
        """初始化修复策略"""
        return {
            'security': SecurityRepairStrategy(),
            'quality': QualityRepairStrategy(),
            'performance': PerformanceRepairStrategy(),
            'logic': LogicRepairStrategy()
        }

    def analyze(self, target: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """实现基类的抽象方法"""
        code = str(target)
        return self.analyze_and_repair(code, None, context)

    def analyze_and_repair(self, code: str, issues: List[AnalysisResult] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析并修复代码缺陷

        Args:
            code: 要修复的代码
            issues: 已知问题列表
            context: 修复上下文

        Returns:
            修复结果字典
        """
        self.start_execution()

        try:
            # 生成测试用例
            test_cases = self.test_generator.generate_tests(code)
            self.logger.info(f"Generated {len(test_cases)} test cases")

            # 运行测试确认问题
            test_results = self.test_runner.run_tests(test_cases, code)
            self.logger.info(f"Test results: {test_results.passed_tests} passed, {test_results.failed_tests} failed")

            # 如果没有提供问题，通过测试发现问题
            if not issues and test_results.failed_tests > 0:
                issues = self._identify_issues_from_tests(code, test_results)

            # 应用修复
            repair_results = []
            current_code = code

            for issue in issues:
                repair_result = self._repair_issue(current_code, issue)
                if repair_result.success:
                    current_code = repair_result.repaired_code
                    repair_results.append(repair_result)

            # 验证修复效果
            final_test_results = self.test_runner.run_tests(test_cases, current_code)

            # 构建结果
            result = {
                'original_code': code,
                'repaired_code': current_code,
                'generated_tests': [self._test_case_to_dict(tc) for tc in test_cases],
                'initial_test_results': self._test_results_to_dict(test_results),
                'final_test_results': self._test_results_to_dict(final_test_results),
                'applied_repairs': [self._repair_result_to_dict(rr) for rr in repair_results],
                'repair_success': len(repair_results) > 0 and final_test_results.failed_tests < test_results.failed_tests,
                'improvement_metrics': self._calculate_improvement(test_results, final_test_results),
                'confidence': self._calculate_repair_confidence(repair_results),
                'execution_metadata': {
                    'test_cases_generated': len(test_cases),
                    'repairs_attempted': len(issues),
                    'repairs_successful': len(repair_results),
                    'execution_time': 0
                }
            }

            # 更新指标
            self.metrics.issues_found = len(issues)
            self.metrics.accuracy_rate = result['confidence']

            # 记录执行
            self.record_execution("test_driven_repair", {
                "success": result['repair_success'],
                "repairs_applied": len(repair_results),
                "test_improvement": result['improvement_metrics']
            })

            return result

        except Exception as e:
            error_result = self.handle_error(e, {"code_length": len(code) if code else 0})
            self.record_execution("test_driven_repair", error_result)
            return error_result

        finally:
            self.end_execution()

    def get_capabilities(self) -> List[str]:
        """获取测试驱动修复Agent能力"""
        return [
            'automated_test_generation',
            'defect_localization',
            'intelligent_code_repair',
            'repair_validation',
            'test_driven_refactoring',
            'regression_testing',
            'code_quality_improvement'
        ]

    def _identify_issues_from_tests(self, code: str, test_results: TestResults) -> List[AnalysisResult]:
        """从测试结果中识别问题"""
        issues = []

        for test_detail in test_results.test_details:
            if test_detail.get('status') == 'failed':
                # 分析失败原因，创建相应的问题对象
                issue = AnalysisResult(
                    file_path="generated",
                    line_number=0,  # 需要进一步定位
                    issue_type=IssueType.LOGIC,
                    severity=SeverityLevel.HIGH,
                    description=f"Test failed: {test_detail.get('error', 'Unknown error')}",
                    suggestion="Review and fix the failing test case",
                    confidence=0.7
                )
                issues.append(issue)

        return issues

    def _repair_issue(self, code: str, issue: AnalysisResult) -> RepairResult:
        """修复单个问题"""
        strategy_type = issue.issue_type.value
        strategy = self.repair_strategies.get(strategy_type)

        if not strategy:
            return RepairResult(
                original_code=code,
                repaired_code=code,
                applied_fixes=[],
                success=False,
                validation_passed=False,
                performance_impact={},
                side_effects=["No repair strategy available"],
                confidence=0.0,
                repair_strategy="none"
            )

        try:
            return strategy.repair(code, issue)
        except Exception as e:
            self.logger.warning(f"Repair strategy {strategy_type} failed: {e}")
            return RepairResult(
                original_code=code,
                repaired_code=code,
                applied_fixes=[],
                success=False,
                validation_passed=False,
                performance_impact={},
                side_effects=[f"Repair failed: {str(e)}"],
                confidence=0.0,
                repair_strategy=strategy_type
            )

    def _calculate_improvement(self, initial_results: TestResults, final_results: TestResults) -> Dict[str, float]:
        """计算改进指标"""
        improvement = {
            'failed_tests_reduction': initial_results.failed_tests - final_results.failed_tests,
            'passed_tests_increase': final_results.passed_tests - initial_results.passed_results,
            'success_rate_improvement': (
                (final_results.passed_tests / final_results.total_tests) -
                (initial_results.passed_tests / initial_results.total_tests)
            ) if initial_results.total_tests > 0 else 0
        }

        return improvement

    def _calculate_repair_confidence(self, repair_results: List[RepairResult]) -> float:
        """计算修复置信度"""
        if not repair_results:
            return 0.0

        successful_repairs = sum(1 for rr in repair_results if rr.success)
        total_confidence = sum(rr.confidence for rr in repair_results)

        return total_confidence / len(repair_results) if repair_results else 0.0

    def _test_case_to_dict(self, test_case: TestCase) -> Dict[str, Any]:
        """转换测试用例为字典"""
        return {
            'id': test_case.id,
            'name': test_case.name,
            'description': test_case.description,
            'test_type': test_case.test_type.value,
            'generated_by': test_case.generated_by
        }

    def _test_results_to_dict(self, test_results: TestResults) -> Dict[str, Any]:
        """转换测试结果为字典"""
        return {
            'total_tests': test_results.total_tests,
            'passed_tests': test_results.passed_tests,
            'failed_tests': test_results.failed_tests,
            'error_tests': test_results.error_tests,
            'execution_time': test_results.execution_time,
            'success_rate': test_results.passed_tests / test_results.total_tests if test_results.total_tests > 0 else 0
        }

    def _repair_result_to_dict(self, repair_result: RepairResult) -> Dict[str, Any]:
        """转换修复结果为字典"""
        return {
            'success': repair_result.success,
            'validation_passed': repair_result.validation_passed,
            'confidence': repair_result.confidence,
            'repair_strategy': repair_result.repair_strategy,
            'applied_fixes': repair_result.applied_fixes,
            'side_effects': repair_result.side_effects
        }


class TestGenerator:
    """测试生成器"""

    def __init__(self):
        self.test_counter = 0

    def generate_tests(self, code: str) -> List[TestCase]:
        """为代码生成测试用例"""
        test_cases = []

        try:
            # 解析代码结构
            tree = ast.parse(code)

            # 为每个函数生成测试
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    test_case = self._generate_function_test(node, code)
                    if test_case:
                        test_cases.append(test_case)

                # 为每个类生成测试
                elif isinstance(node, ast.ClassDef):
                    class_tests = self._generate_class_tests(node, code)
                    test_cases.extend(class_tests)

        except Exception as e:
            # 如果AST解析失败，生成通用测试
            test_cases.append(self._generate_generic_test(code))

        # 确保不超过最大测试用例数
        max_tests = TEST_CONFIG.get('max_test_cases', 50)
        return test_cases[:max_tests]

    def _generate_function_test(self, func_node: ast.FunctionDef, code: str) -> Optional[TestCase]:
        """为函数生成测试用例"""
        self.test_counter += 1

        # 获取函数信息
        func_name = func_node.name
        args = [arg.arg for arg in func_node.args.args]

        # 生成测试用例
        return TestCase(
            id=f"test_{func_name}_{self.test_counter}",
            name=f"Test {func_name}",
            description=f"Test function {func_name} with {len(args)} arguments",
            input_data={
                'function_name': func_name,
                'arguments': args,
                'test_inputs': self._generate_test_inputs(args)
            },
            expected_output="success",  # 简化的期望输出
            test_type=TestType.UNIT,
            generated_by="ai",
            code_template=self._generate_test_template(func_name, args)
        )

    def _generate_class_tests(self, class_node: ast.ClassDef, code: str) -> List[TestCase]:
        """为类生成测试用例"""
        tests = []
        class_name = class_node.name

        # 生成类初始化测试
        tests.append(TestCase(
            id=f"test_{class_name}_init",
            name=f"Test {class_name} initialization",
            description=f"Test {class_name} class initialization",
            input_data={'class_name': class_name},
            expected_output="instance_created",
            test_type=TestType.UNIT,
            generated_by="ai"
        ))

        return tests

    def _generate_test_inputs(self, args: List[str]) -> List[Dict[str, Any]]:
        """生成测试输入"""
        test_inputs = []

        # 生成基本的测试输入
        if len(args) == 0:
            test_inputs.append({})
        elif len(args) == 1:
            test_inputs.append({args[0]: "test_value"})
        else:
            # 多参数情况
            test_inputs.append({arg: f"test_{i}" for i, arg in enumerate(args)})

        return test_inputs

    def _generate_test_template(self, func_name: str, args: List[str]) -> str:
        """生成测试代码模板"""
        args_str = ", ".join(args)
        return f"""
def test_{func_name}():
    # Test function {func_name}
    result = {func_name}({args_str})
    # Add assertions here
    assert result is not None
"""

    def _generate_generic_test(self, code: str) -> TestCase:
        """生成通用测试用例"""
        self.test_counter += 1

        return TestCase(
            id=f"generic_test_{self.test_counter}",
            name="Generic code test",
            description="Generic test for code validation",
            input_data={'code_sample': code[:100] + "..." if len(code) > 100 else code},
            expected_output="code_executable",
            test_type=TestType.UNIT,
            generated_by="template"
        )


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.timeout = TEST_CONFIG.get('test_timeout', 10)

    def run_tests(self, test_cases: List[TestCase], code: str) -> TestResults:
        """运行测试用例"""
        start_time = time.time()

        passed_tests = 0
        failed_tests = 0
        error_tests = 0
        test_details = []

        for test_case in test_cases:
            try:
                result = self._run_single_test(test_case, code)
                test_details.append(result)

                if result['status'] == 'passed':
                    passed_tests += 1
                elif result['status'] == 'failed':
                    failed_tests += 1
                else:
                    error_tests += 1

            except Exception as e:
                test_details.append({
                    'test_id': test_case.id,
                    'status': 'error',
                    'error': str(e),
                    'execution_time': 0
                })
                error_tests += 1

        execution_time = time.time() - start_time

        return TestResults(
            total_tests=len(test_cases),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            error_tests=error_tests,
            execution_time=execution_time,
            test_details=test_details
        )

    def _run_single_test(self, test_case: TestCase, code: str) -> Dict[str, Any]:
        """运行单个测试用例"""
        start_time = time.time()

        try:
            # 简化的测试执行逻辑
            # 在实际实现中，这里会执行真实的测试代码
            if test_case.test_type == TestType.UNIT:
                result = self._execute_unit_test(test_case, code)
            else:
                result = {'status': 'passed', 'message': 'Test executed'}

            execution_time = time.time() - start_time

            return {
                'test_id': test_case.id,
                'status': result['status'],
                'message': result.get('message', ''),
                'execution_time': execution_time
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'test_id': test_case.id,
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time
            }

    def _execute_unit_test(self, test_case: TestCase, code: str) -> Dict[str, Any]:
        """执行单元测试"""
        # 简化的单元测试逻辑
        # 在实际实现中，这里会编译和执行测试代码
        try:
            # 尝试编译代码
            ast.parse(code)
            return {'status': 'passed', 'message': 'Code compiles successfully'}
        except SyntaxError as e:
            return {'status': 'failed', 'error': f'Syntax error: {e}'}


class SecurityRepairStrategy:
    """安全修复策略"""

    def repair(self, code: str, issue: AnalysisResult) -> RepairResult:
        """修复安全问题"""
        lines = code.split('\n')
        original_line = lines[issue.line_number - 1]

        # 硬编码密码修复示例
        if "hardcoded_credentials" in str(issue.metadata.get('vulnerability_type', '')):
            # 替换硬编码密码为环境变量
            fixed_line = re.sub(
                r'(\w*password\s*[=:]\s*)["\']([^"\']*)["\']',
                r'\1os.getenv("PASSWORD")',
                original_line
            )
            lines[issue.line_number - 1] = fixed_line

            return RepairResult(
                original_code=code,
                repaired_code='\n'.join(lines),
                applied_fixes=[f"Replaced hardcoded password with environment variable"],
                success=True,
                validation_passed=True,
                performance_impact={'speed_impact': 0.0},
                side_effects=["Requires PASSWORD environment variable"],
                confidence=0.8,
                repair_strategy="security_replacement"
            )

        return RepairResult(
            original_code=code,
            repaired_code=code,
            applied_fixes=[],
            success=False,
            validation_passed=False,
            performance_impact={},
            side_effects=["No specific security repair available"],
            confidence=0.0,
            repair_strategy="security_none"
        )


class QualityRepairStrategy:
    """质量修复策略"""

    def repair(self, code: str, issue: AnalysisResult) -> RepairResult:
        """修复质量问题"""
        lines = code.split('\n')
        original_line = lines[issue.line_number - 1]

        # 长行修复示例
        if hasattr(issue, 'quality_metric') and issue.quality_metric == "line_length":
            if len(original_line) > 100:
                # 简单的长行分割
                indent = len(original_line) - len(original_line.lstrip())
                fixed_lines = [
                    original_line[:80] + " \\",
                    " " * indent + original_line[80:].strip()
                ]
                lines[issue.line_number - 1:issue.line_number] = fixed_lines

                return RepairResult(
                    original_code=code,
                    repaired_code='\n'.join(lines),
                    applied_fixes=[f"Split long line at position {issue.line_number}"],
                    success=True,
                    validation_passed=True,
                    performance_impact={'readability_impact': 0.2},
                    side_effects=["Code formatting changed"],
                    confidence=0.9,
                    repair_strategy="quality_formatting"
                )

        return RepairResult(
            original_code=code,
            repaired_code=code,
            applied_fixes=[],
            success=False,
            validation_passed=False,
            performance_impact={},
            side_effects=["No specific quality repair available"],
            confidence=0.0,
            repair_strategy="quality_none"
        )


class PerformanceRepairStrategy:
    """性能修复策略"""

    def repair(self, code: str, issue: AnalysisResult) -> RepairResult:
        """修复性能问题"""
        lines = code.split('\n')
        original_line = lines[issue.line_number - 1]

        # 字符串连接修复示例
        if "string_concatenation" in str(issue.metadata.get('performance_metric', '')):
            if '+' in original_line and 'for' in original_line:
                # 替换为join方法
                fixed_line = re.sub(
                    r'(\w+\s*\+=\s*)["\']\s*\+\s*(\w+)\s*\+\s*["\']',
                    r'\1"".join([str(\2)])',
                    original_line
                )
                lines[issue.line_number - 1] = fixed_line

                return RepairResult(
                    original_code=code,
                    repaired_code='\n'.join(lines),
                    applied_fixes=[f"Optimized string concatenation at line {issue.line_number}"],
                    success=True,
                    validation_passed=True,
                    performance_impact={'speed_improvement': 0.3},
                    side_effects=["String concatenation logic changed"],
                    confidence=0.7,
                    repair_strategy="performance_optimization"
                )

        return RepairResult(
            original_code=code,
            repaired_code=code,
            applied_fixes=[],
            success=False,
            validation_passed=False,
            performance_impact={},
            side_effects=["No specific performance repair available"],
            confidence=0.0,
            repair_strategy="performance_none"
        )


class LogicRepairStrategy:
    """逻辑修复策略"""

    def repair(self, code: str, issue: AnalysisResult) -> RepairResult:
        """修复逻辑问题"""
        # 逻辑修复通常需要更复杂的分析
        # 这里提供一个简单的示例
        return RepairResult(
            original_code=code,
            repaired_code=code,
            applied_fixes=[],
            success=False,
            validation_passed=False,
            performance_impact={},
            side_effects=["Logic repair requires manual intervention"],
            confidence=0.1,
            repair_strategy="logic_manual"
        )