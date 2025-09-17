"""
Command Line Interface
命令行接口，提供用户友好的交互方式
"""

import click
import json
import sys
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .core.config import get_config, update_config
from .core.models import Strategy
from .agents.coordinator_agent import CoordinatorAgent
from .core.exceptions import DebugAgentException


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Debug Agent - AI驱动的代码缺陷检测与修复工具"""
    pass


@cli.command()
@click.argument('code', type=str)
@click.option('--file', '-f', type=str, help='代码文件路径')
@click.option('--strategy', '-s', type=click.Choice(['static', 'test-driven', 'hybrid', 'auto']),
              default='auto', help='执行策略')
@click.option('--output', '-o', type=str, help='输出文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def analyze(code: str, file: Optional[str], strategy: str, output: Optional[str], verbose: bool):
    """分析代码并检测缺陷"""
    try:
        # 获取配置
        config = get_config()
        if verbose:
            config.verbose_output = True

        # 映射策略
        strategy_map = {
            'static': Strategy.STATIC_ONLY,
            'test-driven': Strategy.TEST_DRIVEN_ONLY,
            'hybrid': Strategy.HYBRID,
            'auto': Strategy.AUTO
        }

        # 创建协调器
        coordinator = CoordinatorAgent(config)

        # 执行分析
        click.echo(f"🔍 正在分析代码... (策略: {strategy})")
        result = coordinator.analyze_and_repair(
            code=code,
            file_path=file,
            strategy=strategy_map[strategy]
        )

        # 显示结果
        if verbose:
            _display_detailed_result(result)
        else:
            _display_summary_result(result)

        # 保存结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"📁 结果已保存到: {output}")

    except Exception as e:
        click.echo(f"❌ 分析失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--strategy', '-s', type=click.Choice(['static', 'test-driven', 'hybrid', 'auto']),
              default='auto', help='执行策略')
@click.option('--repair', '-r', is_flag=True, help='自动修复发现的问题')
@click.option('--output', '-o', type=str, help='输出文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def scan(file_path: str, strategy: str, repair: bool, output: Optional[str], verbose: bool):
    """扫描文件或目录"""
    try:
        config = get_config()
        if verbose:
            config.verbose_output = True

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # 映射策略
        strategy_map = {
            'static': Strategy.STATIC_ONLY,
            'test-driven': Strategy.TEST_DRIVEN_ONLY,
            'hybrid': Strategy.HYBRID,
            'auto': Strategy.AUTO
        }

        # 创建协调器
        coordinator = CoordinatorAgent(config)

        # 执行扫描
        click.echo(f"🔍 正在扫描文件: {file_path}")
        result = coordinator.analyze_and_repair(
            code=code,
            file_path=file_path,
            strategy=strategy_map[strategy]
        )

        # 显示结果
        if verbose:
            _display_detailed_result(result)
        else:
            _display_summary_result(result)

        # 保存结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"📁 结果已保存到: {output}")

    except Exception as e:
        click.echo(f"❌ 扫描失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--enable-repair', is_flag=True, help='启用自动修复')
@click.option('--confidence', type=float, default=0.7, help='修复置信度阈值')
@click.option('--max-attempts', type=int, default=3, help='最大修复尝试次数')
def config(enable_repair: bool, confidence: float, max_attempts: int):
    """配置Debug Agent"""
    try:
        updates = {}

        if enable_repair:
            updates['enable_auto_repair'] = True
            click.echo("✅ 已启用自动修复")

        if confidence != 0.7:
            updates['repair_confidence_threshold'] = confidence
            click.echo(f"✅ 修复置信度阈值设置为: {confidence}")

        if max_attempts != 3:
            updates['max_repair_attempts'] = max_attempts
            click.echo(f"✅ 最大修复尝试次数设置为: {max_attempts}")

        if updates:
            update_config(updates)
            click.echo("📝 配置已更新")
        else:
            # 显示当前配置
            current_config = get_config()
            click.echo("📋 当前配置:")
            click.echo(f"  自动修复: {'启用' if current_config.enable_auto_repair else '禁用'}")
            click.echo(f"  修复置信度阈值: {current_config.repair_confidence_threshold}")
            click.echo(f"  最大修复尝试次数: {current_config.max_repair_attempts}")

    except Exception as e:
        click.echo(f"❌ 配置失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """显示系统状态"""
    try:
        config = get_config()
        coordinator = CoordinatorAgent(config)
        agent_status = coordinator.get_agent_status()

        click.echo("📊 Debug Agent 系统状态")
        click.echo("=" * 50)

        for agent_name, status in agent_status.items():
            click.echo(f"\n🔧 {agent_name.upper()}:")
            click.echo(f"  执行次数: {status['execution_count']}")
            click.echo(f"  成功率: {status['success_rate']:.2%}")
            click.echo(f"  能力数量: {len(status['capabilities'])}")
            if status['capabilities']:
                click.echo("  主要能力:")
                for capability in status['capabilities'][:3]:  # 只显示前3个能力
                    click.echo(f"    • {capability}")
                if len(status['capabilities']) > 3:
                    click.echo(f"    ... 还有 {len(status['capabilities']) - 3} 个能力")

    except Exception as e:
        click.echo(f"❌ 获取状态失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('test_file', type=click.Path(exists=True))
def test(test_file: str):
    """运行测试用例"""
    try:
        import subprocess

        click.echo(f"🧪 运行测试: {test_file}")
        result = subprocess.run(
            ['python', '-m', 'pytest', test_file, '-v'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.echo("✅ 测试通过")
            click.echo(result.stdout)
        else:
            click.echo("❌ 测试失败")
            click.echo(result.stdout)
            click.echo(result.stderr)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ 测试运行失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def init():
    """初始化项目配置"""
    try:
        from .core.config import config_manager

        # 创建示例配置文件
        config_manager.create_sample_config()

        # 创建输出目录
        os.makedirs("output", exist_ok=True)

        click.echo("✅ 项目初始化完成")
        click.echo("📝 配置文件: config.sample.json")
        click.echo("📁 输出目录: output/")
        click.echo("💡 请复制 config.sample.json 为 config.json 并根据需要修改")

    except Exception as e:
        click.echo(f"❌ 初始化失败: {e}", err=True)
        sys.exit(1)


def _display_summary_result(result: Dict[str, Any]):
    """显示结果摘要"""
    total_issues = result.get('total_issues', 0)
    overall_success = result.get('overall_success', False)
    strategy = result.get('strategy', 'unknown')

    if overall_success:
        click.echo(f"✅ 分析完成 (策略: {strategy})")
    else:
        click.echo(f"⚠️  分析完成，但发现问题 (策略: {strategy})")

    click.echo(f"📊 发现问题: {total_issues} 个")

    applied_repairs = result.get('applied_repairs', [])
    if applied_repairs:
        click.echo(f"🔧 应用修复: {len(applied_repairs)} 个")

    quality_improvement = result.get('quality_improvement', {})
    if quality_improvement:
        score = quality_improvement.get('quality_score', 0)
        click.echo(f"📈 质量评分: {score:.2f}")


def _display_detailed_result(result: Dict[str, Any]):
    """显示详细结果"""
    _display_summary_result(result)

    # 显示协调信息
    coordination_info = result.get('coordination_info', {})
    if coordination_info:
        click.echo("\n🔗 协调信息:")
        click.echo(f"  策略: {coordination_info.get('strategy_used', 'unknown')}")

        context_analysis = coordination_info.get('context_analysis', {})
        if context_analysis:
            click.echo(f"  复杂度级别: {context_analysis.get('complexity_level', 'unknown')}")
            click.echo(f"  文件类型: {context_analysis.get('file_type', 'unknown')}")
            click.echo(f"  代码大小: {context_analysis.get('code_size', 0)} 字符")

    # 显示静态分析结果
    static_results = result.get('static_analysis_results')
    if static_results:
        click.echo("\n📋 静态分析结果:")
        if isinstance(static_results, dict):
            security_issues = static_results.get('security_issues', [])
            quality_issues = static_results.get('quality_issues', [])
            performance_issues = static_results.get('performance_issues', [])

            if security_issues:
                click.echo(f"  🔴 安全问题: {len(security_issues)} 个")
            if quality_issues:
                click.echo(f"  🟡 质量问题: {len(quality_issues)} 个")
            if performance_issues:
                click.echo(f"  🟠 性能问题: {len(performance_issues)} 个")

    # 显示修复结果
    repair_results = result.get('repair_results')
    if repair_results:
        click.echo("\n🔧 修复结果:")
        repair_success = repair_results.get('repair_success', False)
        click.echo(f"  修复成功: {'是' if repair_success else '否'}")

        if 'confidence' in repair_results:
            click.echo(f"  置信度: {repair_results['confidence']:.2f}")


if __name__ == '__main__':
    cli()