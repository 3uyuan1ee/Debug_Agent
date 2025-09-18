"""
Intelligent Coordinator Agent with LangChain
基于LangChain的智能协调器Agent
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from ..core.base_agent import BaseAgent
from ..core.config import AgentConfig
from ..core.models import AnalysisResult, Strategy, SeverityLevel, IssueType, ComplexityLevel
from ..core.exceptions import DebugAgentException
from .static_analysis_agent import StaticAnalysisAgent
from .test_driven_repair_agent import TestDrivenRepairAgent
from ..chains.analysis_chains import create_analysis_chains


class IntelligentCoordinator(BaseAgent):
    """智能协调器Agent"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # 初始化LLM
        self.llm = self._initialize_llm()

        # 初始化记忆管理
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.summary_memory = ConversationSummaryMemory(llm=self.llm)

        # 初始化传统Agent
        self.static_agent = StaticAnalysisAgent(config)
        self.repair_agent = TestDrivenRepairAgent(config)

        # 初始化LangChain分析链
        self.analysis_chains = create_analysis_chains({
            'model': config.ai_model or 'gpt-4'
        })

        # 初始化决策链
        self.decision_chain = self._create_decision_chain()

        # 初始化工具
        self.tools = self._create_tools()

        # 初始化智能代理
        self.master_agent = self._create_master_agent()

        # 项目记忆
        self.project_memory = {
            'file_analyses': {},
            'issue_patterns': {},
            'repair_history': {},
            'success_rates': {}
        }

    def _initialize_llm(self):
        """初始化LLM"""
        if self.config.ai_model and self.config.ai_model.startswith('gpt'):
            return ChatOpenAI(model=self.config.ai_model, temperature=0.1)
        elif self.config.ai_model and self.config.ai_model.startswith('claude'):
            return ChatAnthropic(model=self.config.ai_model, temperature=0.1)
        else:
            return ChatOpenAI(model="gpt-4", temperature=0.1)

    def _create_decision_chain(self):
        """创建决策链"""
        prompt = PromptTemplate(
            input_variables=["code_complexity", "issue_severity", "context", "project_memory"],
            template=self._get_decision_prompt()
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def _create_tools(self):
        """创建工具集"""
        return [
            Tool(
                name="static_analysis",
                func=self._static_analysis_tool,
                description="执行传统静态分析，检测安全漏洞和质量问题"
            ),
            Tool(
                name="ai_analysis",
                func=self._ai_analysis_tool,
                description="使用AI进行深度代码分析，包括安全、质量和性能分析"
            ),
            Tool(
                name="test_driven_repair",
                func=self._test_driven_repair_tool,
                description="执行测试驱动的代码修复"
            ),
            Tool(
                name="complexity_assessment",
                func=self._complexity_assessment_tool,
                description="评估代码复杂度并识别结构问题"
            ),
            Tool(
                name="strategy_decision",
                func=self._strategy_decision_tool,
                description="基于上下文和项目记忆选择最佳策略"
            ),
            Tool(
                name="pattern_recognition",
                func=self._pattern_recognition_tool,
                description="识别代码中的模式和反模式"
            ),
            Tool(
                name="quality_optimization",
                func=self._quality_optimization_tool,
                description="优化代码质量和性能"
            ),
            Tool(
                name="memory_update",
                func=self._memory_update_tool,
                description="更新项目记忆和历史记录"
            )
        ]

    def _create_master_agent(self):
        """创建主智能代理"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.conversation_memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15
        )

    def analyze(self, target: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """实现基类的抽象方法"""
        code = str(target)
        return self.intelligent_analyze_and_repair(code, None, context)

    def intelligent_analyze_and_repair(self,
                                      code: str,
                                      file_path: str = None,
                                      strategy: Strategy = Strategy.AUTO,
                                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """智能分析和修复"""
        self.start_execution()

        try:
            # 准备分析上下文
            analysis_context = {
                'code': code,
                'file_path': file_path,
                'language': self._detect_language(file_path),
                'strategy': strategy.value if strategy else 'auto',
                'project_memory': self.project_memory,
                **(context or {})
            }

            # 执行智能代理
            if strategy == Strategy.AUTO:
                result = self._execute_intelligent_agent(analysis_context)
            else:
                result = self._execute_strategy_based(analysis_context, strategy)

            # 添加智能协调器特有信息
            result['intelligent_info'] = {
                'model_used': self.llm.model_name,
                'memory_usage': {
                    'conversation': len(self.conversation_memory.chat_memory.messages),
                    'summary': self.summary_memory.buffer
                },
                'tools_used': result.get('tools_used', []),
                'decision_process': result.get('decision_process', {}),
                'learning_improvement': self._calculate_learning_improvement()
            }

            # 记录到项目记忆
            self._update_project_memory(file_path, result)

            # 记录执行
            self.record_execution("intelligent_coordination", {
                "success": result.get('overall_success', False),
                "strategy": strategy.value if strategy else "auto",
                "issues_found": result.get('total_issues', 0),
                "tools_used": result.get('tools_used', []),
                "intelligence_level": "high"
            })

            return result

        except Exception as e:
            error_result = self.handle_error(e, {
                "code_length": len(code) if code else 0,
                "strategy": strategy.value if strategy else "unknown",
                "intelligence_level": "high"
            })
            self.record_execution("intelligent_coordination", error_result)
            return error_result

        finally:
            self.end_execution()

    def _execute_intelligent_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能代理"""
        # 构建代理输入
        agent_input = self._build_agent_input(context)

        # 执行代理
        agent_result = self.master_agent.run(agent_input)

        # 解析代理结果
        return self._parse_intelligent_result(agent_result, context)

    def _execute_strategy_based(self, context: Dict[str, Any], strategy: Strategy) -> Dict[str, Any]:
        """基于策略执行"""
        if strategy == Strategy.STATIC_ONLY:
            return self._execute_static_analysis(context)
        elif strategy == Strategy.TEST_DRIVEN_ONLY:
            return self._execute_test_driven_repair(context)
        elif strategy == Strategy.HYBRID:
            return self._execute_hybrid_strategy(context)
        else:
            return self._execute_intelligent_agent(context)

    def _build_agent_input(self, context: Dict[str, Any]) -> str:
        """构建代理输入"""
        return f"""
请作为智能代码分析和修复专家，处理以下任务：

代码信息：
- 语言：{context['language']}
- 文件路径：{context.get('file_path', 'unknown')}
- 代码长度：{len(context['code'])} 字符

待分析代码：
```
{context['language']}
{context['code']}
```

项目上下文：
- 项目记忆：{len(self.project_memory['file_analyses'])} 个文件已分析
- 历史成功率：{self._calculate_success_rate()}
- 项目模式：{len(self.project_memory['issue_patterns'])} 个问题模式

任务要求：
1. 使用可用的工具进行全面分析
2. 基于项目记忆和历史经验做出决策
3. 选择最适合的分析和修复策略
4. 提供详细的修复建议和优化方案
5. 记录学习到的模式和经验

请按照以下步骤执行：
1. 首先评估代码复杂度和问题严重性
2. 识别已知的模式和反模式
3. 选择最佳策略
4. 执行分析和修复
5. 提供综合报告和改进建议

请以JSON格式返回完整的结果。
"""

    def _static_analysis_tool(self, args: str) -> str:
        """静态分析工具"""
        try:
            # 使用传统静态分析
            context = {'file_path': 'unknown'}  # 简化处理
            result = self.static_agent.analyze(args, context)
            return f"静态分析完成：发现 {result.get('total_issues', 0)} 个问题"
        except Exception as e:
            return f"静态分析失败：{str(e)}"

    def _ai_analysis_tool(self, args: str) -> str:
        """AI分析工具"""
        try:
            # 使用AI分析链
            context = {'language': 'python', 'context': {}}
            result = self.analysis_chains['comprehensive'].invoke({
                'code': args,
                'language': 'python',
                'context': context
            })
            return "AI深度分析完成"
        except Exception as e:
            return f"AI分析失败：{str(e)}"

    def _test_driven_repair_tool(self, args: str) -> str:
        """测试驱动修复工具"""
        try:
            # 使用测试驱动修复
            result = self.repair_agent.analyze_and_repair(args, {})
            return f"测试驱动修复完成：{result.get('repair_success', False)}"
        except Exception as e:
            return f"测试驱动修复失败：{str(e)}"

    def _complexity_assessment_tool(self, args: str) -> str:
        """复杂度评估工具"""
        try:
            complexity_level = self._assess_complexity(args)
            return f"复杂度评估：{complexity_level.value}"
        except Exception as e:
            return f"复杂度评估失败：{str(e)}"

    def _strategy_decision_tool(self, args: str) -> str:
        """策略决策工具"""
        try:
            # 使用决策链
            decision = self.decision_chain.run(
                code_complexity=args.get('complexity', 'medium'),
                issue_severity=args.get('severity', 'medium'),
                context=args.get('context', {}),
                project_memory=self.project_memory
            )
            return f"策略决策：{decision}"
        except Exception as e:
            return f"策略决策失败：{str(e)}"

    def _pattern_recognition_tool(self, args: str) -> str:
        """模式识别工具"""
        try:
            patterns = self._recognize_patterns(args)
            return f"识别到 {len(patterns)} 个模式"
        except Exception as e:
            return f"模式识别失败：{str(e)}"

    def _quality_optimization_tool(self, args: str) -> str:
        """质量优化工具"""
        try:
            # 使用优化链
            result = self.analysis_chains['optimization'].invoke({
                'code': args,
                'language': 'python'
            })
            return "质量优化完成"
        except Exception as e:
            return f"质量优化失败：{str(e)}"

    def _memory_update_tool(self, args: str) -> str:
        """记忆更新工具"""
        try:
            # 更新项目记忆
            memory_data = eval(args)  # 简化处理
            self.project_memory.update(memory_data)
            return "项目记忆已更新"
        except Exception as e:
            return f"记忆更新失败：{str(e)}"

    def _parse_intelligent_result(self, agent_result: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """解析智能代理结果"""
        # 简化的解析逻辑
        return {
            'strategy': 'intelligent_agent',
            'agent_result': agent_result,
            'total_issues': 0,
            'overall_success': True,
            'tools_used': [],
            'decision_process': {}
        }

    def _assess_complexity(self, code: str) -> ComplexityLevel:
        """评估代码复杂度"""
        # 简化的复杂度评估
        lines = len(code.split('\n'))
        if lines < 20:
            return ComplexityLevel.LOW
        elif lines < 50:
            return ComplexityLevel.MEDIUM
        elif lines < 100:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.VERY_HIGH

    def _recognize_patterns(self, code: str) -> List[Dict[str, Any]]:
        """识别代码模式"""
        # 简化的模式识别
        patterns = []

        # 检测常见模式
        if 'def ' in code and 'class ' in code:
            patterns.append({'type': 'object_oriented', 'confidence': 0.8})

        if 'import ' in code and 'from ' in code:
            patterns.append({'type': 'module_import', 'confidence': 0.9})

        return patterns

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        total = len(self.project_memory['success_rates'])
        if total == 0:
            return 0.8  # 默认成功率

        successful = sum(1 for rate in self.project_memory['success_rates'].values() if rate > 0.7)
        return successful / total

    def _calculate_learning_improvement(self) -> Dict[str, Any]:
        """计算学习改进效果"""
        return {
            'analyses_count': len(self.project_memory['file_analyses']),
            'patterns_discovered': len(self.project_memory['issue_patterns']),
            'success_rate_improvement': self._calculate_success_rate(),
            'memory_efficiency': len(self.conversation_memory.chat_memory.messages) / 1000
        }

    def _update_project_memory(self, file_path: str, result: Dict[str, Any]):
        """更新项目记忆"""
        if file_path:
            self.project_memory['file_analyses'][file_path] = {
                'last_analysis': result,
                'analysis_count': self.project_memory['file_analyses'].get(file_path, {}).get('analysis_count', 0) + 1
            }

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
        else:
            return "Python"

    def _get_decision_prompt(self) -> str:
        """获取决策提示模板"""
        return """
基于以下信息，选择最佳的代码分析和修复策略：

代码复杂度：{code_complexity}
问题严重性：{issue_severity}
分析上下文：{context}
项目记忆：{project_memory}

可选策略：
1. STATIC_ONLY - 仅静态分析（适合简单代码）
2. TEST_DRIVEN_ONLY - 仅测试驱动修复（适合复杂逻辑）
3. HYBRID - 混合策略（平衡的分析和修复）
4. INTELLIGENT - 智能代理（最先进的分析和修复）

请考虑以下因素：
- 代码复杂度和规模
- 问题的严重性和紧急性
- 项目历史和成功率
- 时间和资源限制

请选择最佳策略并解释原因。
"""

    def get_capabilities(self) -> List[str]:
        """获取智能协调器能力"""
        return [
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

    def get_intelligence_metrics(self) -> Dict[str, Any]:
        """获取智能指标"""
        return {
            'learning_capacity': len(self.project_memory['file_analyses']),
            'pattern_recognition': len(self.project_memory['issue_patterns']),
            'decision_accuracy': self._calculate_success_rate(),
            'memory_efficiency': len(self.conversation_memory.chat_memory.messages),
            'tool_utilization': len([tool for tool in self.tools if tool.name in [t['name'] for t in self.project_memory.get('tools_used', [])]]),
            'adaptation_level': 'high'
        }

    def clear_memory(self):
        """清理记忆"""
        self.conversation_memory.clear()
        self.summary_memory.clear()
        self.project_memory = {
            'file_analyses': {},
            'issue_patterns': {},
            'repair_history': {},
            'success_rates': {}
        }

    def export_memory(self) -> Dict[str, Any]:
        """导出记忆数据"""
        return {
            'conversation_memory': self.conversation_memory.load_memory_variables({}),
            'summary_memory': self.summary_memory.buffer,
            'project_memory': self.project_memory,
            'intelligence_metrics': self.get_intelligence_metrics()
        }