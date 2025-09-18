"""
Analysis Chains Implementation
分析链的实现
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chains import LLMChain, SequentialChain, TransformChain
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from json import loads, dumps

from ..core.models import AnalysisResult, SecurityIssue, QualityIssue, PerformanceIssue, SeverityLevel, IssueType


class SecurityAnalysisResult(BaseModel):
    """安全分析结果"""
    vulnerabilities: List[Dict[str, Any]] = Field(description="安全漏洞列表")
    risk_level: str = Field(description="风险级别")
    recommendations: List[str] = Field(description="建议措施")


class QualityAnalysisResult(BaseModel):
    """质量分析结果"""
    issues: List[Dict[str, Any]] = Field(description="质量问题列表")
    quality_score: float = Field(description="质量分数")
    style_violations: List[Dict[str, Any]] = Field(description="风格违规")


class PerformanceAnalysisResult(BaseModel):
    """性能分析结果"""
    bottlenecks: List[Dict[str, Any]] = Field(description="性能瓶颈")
    complexity_score: float = Field(description="复杂度分数")
    optimization_suggestions: List[str] = Field(description="优化建议")


class SecurityAnalysisChain(LLMChain):
    """安全分析链"""

    def __init__(self, llm):
        parser = PydanticOutputParser(pydantic_object=SecurityAnalysisResult)

        prompt = PromptTemplate(
            input_variables=["code", "language", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            template=self._get_security_prompt()
        )

        super().__init__(llm=llm, prompt=prompt)

    def _get_security_prompt(self) -> str:
        return """
你是一个专业的代码安全专家。请仔细分析以下{language}代码中的安全问题：

```{language}
{code}
```

分析上下文：
- 文件路径：{context.get('file_path', 'unknown')}
- 项目类型：{context.get('project_type', 'unknown')}

请重点检查以下安全问题：

1. **输入验证漏洞**
   - SQL注入
   - XSS跨站脚本
   - 命令注入
   - 路径遍历

2. **认证和授权**
   - 硬编码密码或密钥
   - 弱密码策略
   - 会话管理问题

3. **数据安全**
   - 敏感信息泄露
   - 不安全的数据存储
   - 加密问题

4. **其他安全问题**
   - 缓冲区溢出
   - 整数溢出
   - 竞态条件

{format_instructions}

请提供详细的分析结果，包括每个漏洞的位置、严重性和修复建议。
"""

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """执行安全分析"""
        result = super().invoke(input_dict)

        # 解析结果
        try:
            parsed_result = SecurityAnalysisResult.parse_raw(result['text'])
            return {
                'security_analysis': parsed_result.dict(),
                'raw_output': result['text']
            }
        except Exception as e:
            return {
                'security_analysis': {
                    'vulnerabilities': [],
                    'risk_level': 'unknown',
                    'recommendations': []
                },
                'raw_output': result['text'],
                'parse_error': str(e)
            }


class QualityAnalysisChain(LLMChain):
    """质量分析链"""

    def __init__(self, llm):
        parser = PydanticOutputParser(pydantic_object=QualityAnalysisResult)

        prompt = PromptTemplate(
            input_variables=["code", "language", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            template=self._get_quality_prompt()
        )

        super().__init__(llm=llm, prompt=prompt)

    def _get_quality_prompt(self) -> str:
        return """
你是一个专业的代码质量专家。请分析以下{language}代码的质量问题：

```{language}
{code}
```

分析上下文：
- 文件路径：{context.get('file_path', 'unknown')}
- 编码规范：{context.get('coding_standard', 'PEP8')}

请检查以下质量问题：

1. **代码风格**
   - 命名规范
   - 缩进和格式
   - 注释质量
   - 文档字符串

2. **代码结构**
   - 函数长度
   - 类的职责
   - 模块化程度
   - 耦合度

3. **最佳实践**
   - 代码复用
   - 错误处理
   - 日志记录
   - 单元测试

4. **维护性**
   - 可读性
   - 可扩展性
   - 技术债务
   - TODO和FIXME

{format_instructions}

请提供详细的质量分析结果。
"""

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """执行质量分析"""
        result = super().invoke(input_dict)

        try:
            parsed_result = QualityAnalysisResult.parse_raw(result['text'])
            return {
                'quality_analysis': parsed_result.dict(),
                'raw_output': result['text']
            }
        except Exception as e:
            return {
                'quality_analysis': {
                    'issues': [],
                    'quality_score': 0.0,
                    'style_violations': []
                },
                'raw_output': result['text'],
                'parse_error': str(e)
            }


class PerformanceAnalysisChain(LLMChain):
    """性能分析链"""

    def __init__(self, llm):
        parser = PydanticOutputParser(pydantic_object=PerformanceAnalysisResult)

        prompt = PromptTemplate(
            input_variables=["code", "language", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            template=self._get_performance_prompt()
        )

        super().__init__(llm=llm, prompt=prompt)

    def _get_performance_prompt(self) -> str:
        return """
你是一个专业的性能优化专家。请分析以下{language}代码的性能问题：

```{language}
{code}
```

分析上下文：
- 文件路径：{context.get('file_path', 'unknown')}
- 性能要求：{context.get('performance_requirements', 'general')}

请检查以下性能问题：

1. **算法复杂度**
   - 时间复杂度分析
   - 空间复杂度分析
   - 循环优化

2. **资源使用**
   - 内存使用
   - CPU使用
   - I/O操作

3. **并发性**
   - 线程安全
   - 异步处理
   - 并行计算

4. **数据库操作**
   - 查询优化
   - 索引使用
   - 连接池

{format_instructions}

请提供详细的性能分析结果。
"""

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """执行性能分析"""
        result = super().invoke(input_dict)

        try:
            parsed_result = PerformanceAnalysisResult.parse_raw(result['text'])
            return {
                'performance_analysis': parsed_result.dict(),
                'raw_output': result['text']
            }
        except Exception as e:
            return {
                'performance_analysis': {
                    'bottlenecks': [],
                    'complexity_score': 0.0,
                    'optimization_suggestions': []
                },
                'raw_output': result['text'],
                'parse_error': str(e)
            }


class ComprehensiveAnalysisChain(SequentialChain):
    """综合分析链"""

    def __init__(self, llm):
        # 创建子链
        self.security_chain = SecurityAnalysisChain(llm)
        self.quality_chain = QualityAnalysisChain(llm)
        self.performance_chain = PerformanceAnalysisChain(llm)

        # 创建汇总链
        self.summary_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=["security_result", "quality_result", "performance_result", "code"],
                template=self._get_summary_prompt()
            )
        )

        chains = [
            self.security_chain,
            self.quality_chain,
            self.performance_chain,
            self.summary_chain
        ]

        super().__init__(
            chains=chains,
            input_variables=["code", "language", "context"],
            output_variables=["security_result", "quality_result", "performance_result", "summary"]
        )

    def _get_summary_prompt(self) -> str:
        return """
基于以下分析结果，生成一个综合的代码分析报告：

安全分析结果：
{security_result}

质量分析结果：
{quality_result}

性能分析结果：
{performance_result}

原始代码：
{code}

请提供一个综合分析报告，包括：
1. 整体评估分数
2. 主要问题总结
3. 优先级排序
4. 建议的修复策略
5. 预期的改进效果

请以结构化的格式返回报告。
"""


class RepairSuggestionChain(LLMChain):
    """修复建议链"""

    def __init__(self, llm):
        prompt = PromptTemplate(
            input_variables=["code", "issues", "context"],
            template=self._get_repair_prompt()
        )

        super().__init__(llm=llm, prompt=prompt)

    def _get_repair_prompt(self) -> str:
        return """
基于以下代码分析结果，提供修复建议：

原始代码：
```python
{code}
```

发现的问题：
{issues}

修复要求：
- 保持原有功能不变
- 提升代码质量
- 修复安全漏洞
- 优化性能

请提供具体的修复方案：

1. **问题分析**
   详细解释每个问题的根本原因

2. **修复方案**
   提供修复后的代码
   说明修复的关键点

3. **影响评估**
   评估修复的潜在影响
   识别可能的副作用

4. **验证方法**
   提供验证修复有效性的方法
   建议的测试用例

请以清晰的格式返回修复建议。
"""


class CodeOptimizationChain(LLMChain):
    """代码优化链"""

    def __init__(self, llm):
        # 优化示例
        optimization_examples = [
            {
                "original": "def slow_function(data):\n    result = []\n    for i in range(len(data)):\n        if data[i] > 0:\n            result.append(data[i] * 2)\n    return result",
                "optimized": "def fast_function(data):\n    return [x * 2 for x in data if x > 0]",
                "improvement": "使用列表推导式替代循环，提升性能和可读性"
            }
        ]

        prompt = FewShotPromptTemplate(
            examples=optimization_examples,
            suffix="原始代码：\n{code}\n优化后：",
            input_variables=["code"],
            example_prompt=PromptTemplate(
                input_variables=["original", "optimized", "improvement"],
                template="原始代码：\n{original}\n优化后：\n{optimized}\n改进说明：\n{improvement}"
            )
        )

        super().__init__(llm=llm, prompt=prompt)


class TestGenerationChain(LLMChain):
    """测试生成链"""

    def __init__(self, llm):
        prompt = PromptTemplate(
            input_variables=["code", "context"],
            template=self._get_test_prompt()
        )

        super().__init__(llm=llm, prompt=prompt)

    def _get_test_prompt(self) -> str:
        return """
为以下代码生成comprehensive测试用例：

```python
{code}
```

测试要求：
- 单元测试
- 边界条件测试
- 异常情况测试
- 性能测试

请生成完整的测试代码，包括：
1. 测试框架导入
2. 测试类定义
3. 测试方法实现
4. 测试数据准备
5. 断言语句

请使用pytest框架编写测试代码。
"""


def create_analysis_chains(llm_config: Dict[str, Any]) -> Dict[str, LLMChain]:
    """创建分析链集合"""

    # 初始化LLM
    if llm_config.get('model', '').startswith('gpt'):
        llm = ChatOpenAI(model=llm_config.get('model', 'gpt-4'), temperature=0.1)
    elif llm_config.get('model', '').startswith('claude'):
        llm = ChatAnthropic(model=llm_config.get('model', 'claude-3-sonnet-20240229'), temperature=0.1)
    else:
        llm = ChatOpenAI(model="gpt-4", temperature=0.1)

    return {
        'security': SecurityAnalysisChain(llm),
        'quality': QualityAnalysisChain(llm),
        'performance': PerformanceAnalysisChain(llm),
        'comprehensive': ComprehensiveAnalysisChain(llm),
        'repair': RepairSuggestionChain(llm),
        'optimization': CodeOptimizationChain(llm),
        'test_generation': TestGenerationChain(llm)
    }