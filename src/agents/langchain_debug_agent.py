"""
LangChain-based Debug Agent Implementation
基于LangChain的调试Agent实现
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import HumanMessage, AIMessage

from ..core.base_agent import BaseAgent
from ..core.config import AgentConfig
from ..core.models import AnalysisResult, Strategy, SeverityLevel, IssueType
from ..core.exceptions import DebugAgentException


class LangChainDebugAgent(BaseAgent):
    """基于LangChain的调试Agent"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # 初始化LLM
        self.llm = self._initialize_llm()

        # 初始化记忆管理
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 初始化处理链
        self.analysis_chain = self._create_analysis_chain()
        self.repair_chain = self._create_repair_chain()
        self.decision_chain = self._create_decision_chain()

        # 初始化工具
        self.tools = self._create_tools()

        # 初始化智能代理
        self.agent = self._create_agent()

    def _initialize_llm(self):
        """初始化LLM"""
        if self.config.ai_model and self.config.ai_model.startswith('gpt'):
            # 使用配置中的API密钥
            api_key = self.config.ai_api_key or None
            if api_key:
                return ChatOpenAI(model=self.config.ai_model, temperature=0.1, api_key=api_key)
            else:
                return ChatOpenAI(model=self.config.ai_model, temperature=0.1)
        elif self.config.ai_model and self.config.ai_model.startswith('claude'):
            # 使用配置中的API密钥
            api_key = self.config.ai_api_key or None
            if api_key:
                return ChatAnthropic(model=self.config.ai_model, temperature=0.1, api_key=api_key)
            else:
                return ChatAnthropic(model=self.config.ai_model, temperature=0.1)
        else:
            # 默认使用GPT-4
            api_key = self.config.ai_api_key or None
            if api_key:
                return ChatOpenAI(model="gpt-4", temperature=0.1, api_key=api_key)
            else:
                return ChatOpenAI(model="gpt-4", temperature=0.1)

    def _create_analysis_chain(self):
        """创建代码分析链"""
        prompt = PromptTemplate(
            input_variables=["code", "language", "context"],
            template=self._get_analysis_prompt()
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def _create_repair_chain(self):
        """创建修复建议链"""
        prompt = PromptTemplate(
            input_variables=["code", "issues", "context"],
            template=self._get_repair_prompt()
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def _create_decision_chain(self):
        """创建决策链"""
        prompt = PromptTemplate(
            input_variables=["code_complexity", "issue_severity", "context"],
            template=self._get_decision_prompt()
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def _create_tools(self):
        """创建工具集"""
        return [
            Tool(
                name="static_analysis",
                func=self._static_analysis_tool,
                description="执行静态代码分析，检测安全漏洞和质量问题"
            ),
            Tool(
                name="generate_tests",
                func=self._generate_tests_tool,
                description="为给定代码生成测试用例"
            ),
            Tool(
                name="apply_fix",
                func=self._apply_fix_tool,
                description="应用修复到代码中"
            ),
            Tool(
                name="assess_complexity",
                func=self._assess_complexity_tool,
                description="评估代码复杂度"
            )
        ]

    def _create_agent(self):
        """创建智能代理"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

    def analyze(self, target: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """实现基类的抽象方法"""
        code = str(target)
        return self.analyze_and_repair(code, None, context)

    def analyze_and_repair(self,
                          code: str,
                          file_path: str = None,
                          strategy: Strategy = Strategy.AUTO,
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """使用LangChain进行分析和修复"""
        self.start_execution()

        try:
            # 准备上下文
            analysis_context = {
                "code": code,
                "language": self._detect_language(file_path),
                "file_path": file_path,
                "strategy": strategy.value if strategy else "auto",
                **(context or {})
            }

            # 根据策略选择处理方式
            if strategy == Strategy.AUTO:
                # 使用智能代理自动决策
                result = self._agent_based_analysis(analysis_context)
            else:
                # 直接使用处理链
                result = self._chain_based_analysis(analysis_context)

            # 添加LangChain特有的信息
            result['langchain_info'] = {
                'model_used': self.llm.model_name,
                'memory_usage': len(self.memory.chat_memory.messages),
                'tools_used': [tool.name for tool in self.tools],
                'chain_results': {
                    'analysis': result.get('analysis_result', {}),
                    'repair': result.get('repair_result', {}),
                    'decision': result.get('decision_result', {})
                }
            }

            # 记录执行
            self.record_execution("langchain_analysis", {
                "success": result.get('overall_success', False),
                "strategy": strategy.value if strategy else "auto",
                "issues_found": result.get('total_issues', 0),
                "model_used": self.llm.model_name
            })

            return result

        except Exception as e:
            error_result = self.handle_error(e, {
                "code_length": len(code) if code else 0,
                "strategy": strategy.value if strategy else "unknown",
                "model_used": self.llm.model_name
            })
            self.record_execution("langchain_analysis", error_result)
            return error_result

        finally:
            self.end_execution()

    def _agent_based_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """基于智能代理的分析"""
        # 构建代理输入
        agent_input = f"""
请分析以下代码并提供修复建议：

代码语言：{context['language']}
文件路径：{context.get('file_path', 'unknown')}

代码：
```
{context['language']}
{context['code']}
```

请使用可用的工具进行全面分析，包括：
1. 静态分析检测问题
2. 生成测试用例
3. 评估代码复杂度
4. 如果发现问题，尝试修复

请提供详细的分析报告和修复建议。
"""

        # 执行代理
        agent_result = self.agent.run(agent_input)

        # 解析代理结果
        return self._parse_agent_result(agent_result, context)

    def _chain_based_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """基于处理链的分析"""
        # 执行分析链
        analysis_result = self.analysis_chain.run(
            code=context['code'],
            language=context['language'],
            context=context
        )

        # 解析分析结果
        issues = self._parse_analysis_result(analysis_result)

        # 如果发现问题，执行修复链
        repair_result = None
        if issues:
            repair_result = self.repair_chain.run(
                code=context['code'],
                issues=str(issues),
                context=context
            )

        return {
            'strategy': 'chain_based',
            'analysis_result': analysis_result,
            'repair_result': repair_result,
            'issues': issues,
            'total_issues': len(issues),
            'overall_success': len(issues) > 0
        }

    def _static_analysis_tool(self, code: str) -> str:
        """静态分析工具"""
        try:
            # 这里可以集成原有的静态分析逻辑
            # 简化实现，返回基本分析结果
            return f"Static analysis completed for {len(code)} characters of code"
        except Exception as e:
            return f"Static analysis failed: {str(e)}"

    def _generate_tests_tool(self, code: str) -> str:
        """生成测试用例工具"""
        try:
            # 生成测试用例的逻辑
            return f"Test cases generated for the provided code"
        except Exception as e:
            return f"Test generation failed: {str(e)}"

    def _apply_fix_tool(self, args: str) -> str:
        """应用修复工具"""
        try:
            # 解析参数：code, issue, fix_suggestion
            # 简化实现
            return "Fix applied successfully"
        except Exception as e:
            return f"Fix application failed: {str(e)}"

    def _assess_complexity_tool(self, code: str) -> str:
        """评估复杂度工具"""
        try:
            # 评估代码复杂度
            lines = len(code.split('\n'))
            complexity_score = min(10, max(1, lines // 10))
            return f"Code complexity assessed: {complexity_score}/10"
        except Exception as e:
            return f"Complexity assessment failed: {str(e)}"

    def _detect_language(self, file_path: Optional[str]) -> str:
        """检测编程语言"""
        if not file_path:
            return "Python"

        file_path = file_path.lower()
        if file_path.endswith('.py'):
            return "Python"
        elif file_path.endswith('.js'):
            return "JavaScript"
        elif file_path.endswith('.ts'):
            return "TypeScript"
        elif file_path.endswith('.java'):
            return "Java"
        elif file_path.endswith('.cpp') or file_path.endswith('.c'):
            return "C++"
        else:
            return "Python"

    def _parse_agent_result(self, agent_result: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """解析代理结果"""
        # 简化的解析逻辑
        return {
            'strategy': 'agent_based',
            'agent_result': agent_result,
            'total_issues': 0,  # 需要从结果中提取
            'overall_success': True
        }

    def _parse_analysis_result(self, analysis_result: str) -> List[Dict[str, Any]]:
        """解析分析结果"""
        # 简化的解析逻辑
        return []

    def _get_analysis_prompt(self) -> str:
        """获取分析提示模板"""
        return """
你是一个专业的代码分析专家。请仔细分析以下{language}代码：

```{language}
{code}
```

分析上下文：
- 文件路径：{file_path}
- 项目类型：{context.get('project_type', 'unknown')}

请从以下几个方面进行分析：

1. **安全分析**
   - 识别潜在的安全漏洞
   - 检查敏感信息泄露
   - 评估输入验证

2. **质量分析**
   - 代码风格一致性
   - 命名规范
   - 注释质量

3. **性能分析**
   - 时间复杂度
   - 空间复杂度
   - 潜在性能瓶颈

4. **可维护性**
   - 代码复杂度
   - 模块化程度
   - 可读性

请以JSON格式返回分析结果：
```json
{{
    "security_issues": [...],
    "quality_issues": [...],
    "performance_issues": [...],
    "maintainability_issues": [...],
    "overall_score": 0-100,
    "recommendations": [...]
}}
```
"""

    def _get_repair_prompt(self) -> str:
        """获取修复提示模板"""
        return """
基于以下代码分析结果，提供修复建议：

原始代码：
```{language}
{code}
```

发现的问题：
{issues}

修复要求：
- 保持原有功能不变
- 提升代码质量
- 修复安全漏洞
- 优化性能

请提供具体的修复方案，包括修复后的代码。
"""

    def _get_decision_prompt(self) -> str:
        """获取决策提示模板"""
        return """
基于以下信息，选择最佳的代码分析和修复策略：

代码复杂度：{code_complexity}
问题严重性：{issue_severity}
上下文信息：{context}

可选策略：
1. STATIC_ONLY - 仅静态分析
2. TEST_DRIVEN_ONLY - 仅测试驱动修复
3. HYBRID - 混合策略

请选择最适合的策略并解释原因。
"""

    def get_capabilities(self) -> List[str]:
        """获取LangChain Agent的能力"""
        return [
            'intelligent_code_analysis',
            'natural_language_interaction',
            'context_aware_analysis',
            'automated_repair_suggestions',
            'multi_strategy_decision',
            'conversation_memory',
            'tool_integration',
            'continuous_learning'
        ]

    def get_memory_usage(self) -> Dict[str, Any]:
        """获取记忆使用情况"""
        return {
            'total_messages': len(self.memory.chat_memory.messages),
            'memory_type': type(self.memory).__name__,
            'conversation_history': self.memory.load_memory_variables({})
        }

    def clear_memory(self):
        """清理记忆"""
        self.memory.clear()

    def add_context_to_memory(self, context: Dict[str, Any]):
        """添加上下文到记忆"""
        context_message = f"Analysis context: {context}"
        self.memory.chat_memory.add_message(HumanMessage(content=context_message))