"""
Performance Comparison Tests
性能对比测试 - 传统版本 vs LangChain版本
"""

import time
import statistics
import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass
import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)
os.chdir(src_path)  # 更改工作目录到src

from src.core.config import get_config, AgentConfig
from src.core.models import Strategy
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.langchain_debug_agent import LangChainDebugAgent
from src.agents.intelligent_coordinator import IntelligentCoordinator


@dataclass
class TestResult:
    """测试结果"""
    agent_name: str
    execution_time: float
    success: bool
    issues_found: int
    memory_usage_mb: float
    accuracy_score: float
    error_message: str = ""


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    agent_name: str
    average_time: float
    median_time: float
    min_time: float
    max_time: float
    success_rate: float
    average_issues: float
    average_memory: float
    average_accuracy: float


class PerformanceComparator:
    """性能比较器"""

    def __init__(self):
        self.config = get_config()
        self.config.ai_model = "gpt-4"  # 使用可用的模型进行测试

        # 初始化Agent
        self.traditional_agent = CoordinatorAgent(self.config)
        self.langchain_agent = LangChainDebugAgent(self.config)
        self.intelligent_agent = IntelligentCoordinator(self.config)

        # 测试用例
        self.test_cases = self._create_test_cases()

    def _create_test_cases(self) -> List[Dict[str, Any]]:
        """创建测试用例"""
        return [
            {
                'name': '简单函数',
                'code': '''
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
''',
                'expected_issues': 0,
                'complexity': 'low'
            },
            {
                'name': '中等复杂度',
                'code': '''
def process_data(data):
    results = []
    for i in range(len(data)):
        if data[i] > 0:
            results.append(data[i] * 2)
        else:
            results.append(data[i] * 3)
    return results

def validate_input(input_str):
    # TODO: 输入验证
    if len(input_str) > 100:
        return False
    return True
''',
                'expected_issues': 1,
                'complexity': 'medium'
            },
            {
                'name': '安全漏洞',
                'code': '''
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
''',
                'expected_issues': 3,
                'complexity': 'high'
            },
            {
                'name': '性能问题',
                'code': '''
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
''',
                'expected_issues': 2,
                'complexity': 'high'
            },
            {
                'name': '复杂类',
                'code': '''
class UserManager:
    def __init__(self):
        self.users = []
        self.logged_in_users = []

    def add_user(self, username, password, email):
        # FIXME: 密码应该加密
        user = {
            'username': username,
            'password': password,
            'email': email
        }
        self.users.append(user)
        return user

    def login(self, username, password):
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                self.logged_in_users.append(user)
                return True
        return False

    def get_user_by_email(self, email):
        # TODO: 优化搜索算法
        for user in self.users:
            if user['email'] == email:
                return user
        return None

    def delete_user(self, username):
        # HACK: 简单实现
        self.users = [u for u in self.users if u['username'] != username]
        self.logged_in_users = [u for u in self.logged_in_users if u['username'] != username]
''',
                'expected_issues': 4,
                'complexity': 'high'
            }
        ]

    def get_memory_usage(self) -> float:
        """获取内存使用量（MB）"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def calculate_accuracy(self, result: Dict[str, Any], test_case: Dict[str, Any]) -> float:
        """计算准确率"""
        expected_issues = test_case['expected_issues']
        actual_issues = result.get('total_issues', 0)

        if expected_issues == 0:
            return 1.0 if actual_issues == 0 else 0.5

        # 计算准确率（基于预期问题的接近程度）
        accuracy = 1.0 - abs(actual_issues - expected_issues) / max(expected_issues, actual_issues)
        return max(0.0, min(1.0, accuracy))

    def test_agent(self, agent, agent_name: str, test_cases: List[Dict[str, Any]]) -> List[TestResult]:
        """测试单个Agent"""
        results = []

        for test_case in test_cases:
            print(f"测试 {agent_name} - {test_case['name']}")

            try:
                # 记录开始时间和内存
                start_time = time.time()
                start_memory = self.get_memory_usage()

                # 执行分析
                if hasattr(agent, 'intelligent_analyze_and_repair'):
                    result = agent.intelligent_analyze_and_repair(
                        code=test_case['code'],
                        strategy=Strategy.AUTO
                    )
                else:
                    result = agent.analyze_and_repair(
                        code=test_case['code'],
                        strategy=Strategy.AUTO
                    )

                # 记录结束时间和内存
                end_time = time.time()
                end_memory = self.get_memory_usage()

                # 计算指标
                execution_time = end_time - start_time
                memory_usage = end_memory - start_memory
                accuracy = self.calculate_accuracy(result, test_case)

                test_result = TestResult(
                    agent_name=agent_name,
                    execution_time=execution_time,
                    success=result.get('overall_success', False),
                    issues_found=result.get('total_issues', 0),
                    memory_usage_mb=memory_usage,
                    accuracy_score=accuracy
                )

                results.append(test_result)

                print(f"  结果: {execution_time:.2f}s, 问题: {test_result.issues_found}, 准确率: {accuracy:.2f}")

            except Exception as e:
                print(f"  错误: {str(e)}")
                test_result = TestResult(
                    agent_name=agent_name,
                    execution_time=0.0,
                    success=False,
                    issues_found=0,
                    memory_usage_mb=0.0,
                    accuracy_score=0.0,
                    error_message=str(e)
                )
                results.append(test_result)

        return results

    def run_benchmark(self) -> Dict[str, BenchmarkResult]:
        """运行基准测试"""
        print("开始性能对比测试...")
        print("=" * 50)

        benchmark_results = {}

        # 测试传统Agent
        print("测试传统协调器Agent...")
        traditional_results = self.test_agent(
            self.traditional_agent,
            "传统协调器",
            self.test_cases
        )
        benchmark_results['traditional'] = self._calculate_benchmark(traditional_results)

        # 测试LangChain Agent
        print("测试LangChain Agent...")
        langchain_results = self.test_agent(
            self.langchain_agent,
            "LangChain Agent",
            self.test_cases
        )
        benchmark_results['langchain'] = self._calculate_benchmark(langchain_results)

        # 测试智能协调器
        print("测试智能协调器...")
        intelligent_results = self.test_agent(
            self.intelligent_agent,
            "智能协调器",
            self.test_cases
        )
        benchmark_results['intelligent'] = self._calculate_benchmark(intelligent_results)

        return benchmark_results

    def _calculate_benchmark(self, results: List[TestResult]) -> BenchmarkResult:
        """计算基准测试结果"""
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return BenchmarkResult(
                agent_name=results[0].agent_name,
                average_time=0.0,
                median_time=0.0,
                min_time=0.0,
                max_time=0.0,
                success_rate=0.0,
                average_issues=0.0,
                average_memory=0.0,
                average_accuracy=0.0
            )

        execution_times = [r.execution_time for r in successful_results]
        issues_found = [r.issues_found for r in successful_results]
        memory_usage = [r.memory_usage_mb for r in successful_results]
        accuracy_scores = [r.accuracy_score for r in successful_results]

        return BenchmarkResult(
            agent_name=results[0].agent_name,
            average_time=statistics.mean(execution_times),
            median_time=statistics.median(execution_times),
            min_time=min(execution_times),
            max_time=max(execution_times),
            success_rate=len(successful_results) / len(results),
            average_issues=statistics.mean(issues_found),
            average_memory=statistics.mean(memory_usage),
            average_accuracy=statistics.mean(accuracy_scores)
        )

    def print_comparison_report(self, benchmark_results: Dict[str, BenchmarkResult]):
        """打印对比报告"""
        print("\n" + "=" * 60)
        print("性能对比测试报告")
        print("=" * 60)

        agents = list(benchmark_results.keys())
        if not agents:
            print("没有可用的测试结果")
            return

        # 打印详细结果
        print(f"\n{'Agent':<15} {'平均时间':<10} {'成功率':<8} {'准确率':<8} {'内存使用':<10} {'问题数':<8}")
        print("-" * 70)

        for agent_name in agents:
            result = benchmark_results[agent_name]
            print(f"{result.agent_name:<15} {result.average_time:<10.2f} {result.success_rate:<8.2%} {result.average_accuracy:<8.2f} {result.average_memory:<10.2f} {result.average_issues:<8.1f}")

        # 性能对比分析
        print("\n" + "=" * 60)
        print("性能分析")
        print("=" * 60)

        if 'traditional' in benchmark_results and 'langchain' in benchmark_results:
            traditional = benchmark_results['traditional']
            langchain = benchmark_results['langchain']

            print(f"\n传统协调器 vs LangChain Agent:")
            print(f"时间差异: {langchain.average_time - traditional.average_time:+.2f}s ({((langchain.average_time / traditional.average_time - 1) * 100):+.1f}%)")
            print(f"准确率提升: {((langchain.average_accuracy / traditional.average_accuracy - 1) * 100):+.1f}%")
            print(f"内存增加: {langchain.average_memory - traditional.average_memory:+.2f}MB")

        if 'traditional' in benchmark_results and 'intelligent' in benchmark_results:
            traditional = benchmark_results['traditional']
            intelligent = benchmark_results['intelligent']

            print(f"\n传统协调器 vs 智能协调器:")
            print(f"时间差异: {intelligent.average_time - traditional.average_time:+.2f}s ({((intelligent.average_time / traditional.average_time - 1) * 100):+.1f}%)")
            print(f"准确率提升: {((intelligent.average_accuracy / traditional.average_accuracy - 1) * 100):+.1f}%")
            print(f"内存增加: {intelligent.average_memory - traditional.average_memory:+.2f}MB")

        # 综合评分
        print("\n" + "=" * 60)
        print("综合评分 (1-10分)")
        print("=" * 60)

        for agent_name in agents:
            result = benchmark_results[agent_name]
            # 综合评分计算：准确率40%，速度30%，成功率20%，内存使用10%
            speed_score = max(0, 10 - (result.average_time / 10))  # 越快越好
            accuracy_score = result.average_accuracy * 10
            success_score = result.success_rate * 10
            memory_score = max(0, 10 - (result.average_memory / 10))  # 内存使用越少越好

            overall_score = (accuracy_score * 0.4 + speed_score * 0.3 +
                           success_score * 0.2 + memory_score * 0.1)

            print(f"{result.agent_name}: {overall_score:.1f}/10")
            print(f"  - 准确率: {accuracy_score:.1f}")
            print(f"  - 速度: {speed_score:.1f}")
            print(f"  - 成功率: {success_score:.1f}")
            print(f"  - 内存: {memory_score:.1f}")

    def run_specific_test(self, test_case_name: str) -> Dict[str, TestResult]:
        """运行特定测试用例"""
        test_case = next((tc for tc in self.test_cases if tc['name'] == test_case_name), None)
        if not test_case:
            raise ValueError(f"测试用例 '{test_case_name}' 不存在")

        results = {}

        # 测试所有Agent
        agents = [
            (self.traditional_agent, "传统协调器"),
            (self.langchain_agent, "LangChain Agent"),
            (self.intelligent_agent, "智能协调器")
        ]

        for agent, name in agents:
            test_results = self.test_agent(agent, name, [test_case])
            results[name] = test_results[0]

        return results


def main():
    """主函数"""
    print("Debug Agent 性能对比测试")
    print("=" * 50)

    comparator = PerformanceComparator()

    # 运行完整基准测试
    benchmark_results = comparator.run_benchmark()

    # 打印对比报告
    comparator.print_comparison_report(benchmark_results)

    # 保存结果
    import json
    with open('performance_results.json', 'w', encoding='utf-8') as f:
        results_dict = {}
        for key, result in benchmark_results.items():
            results_dict[key] = result.__dict__
        json.dump(results_dict, f, indent=2, ensure_ascii=False)

    print(f"\n详细结果已保存到 performance_results.json")


if __name__ == '__main__':
    main()