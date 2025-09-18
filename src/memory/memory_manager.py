"""
Memory Management System
记忆管理系统
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationKGMemory,
    CombinedMemory
)
from langchain.schema import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.config import AgentConfig


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    timestamp: datetime
    content: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class ProjectMemory:
    """项目记忆"""
    file_analyses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    issue_patterns: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    repair_history: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    success_rates: Dict[str, float] = field(default_factory=dict)
    code_patterns: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    optimization_history: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)


class MemoryManager:
    """记忆管理器"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = self._initialize_llm()

        # 对话记忆
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output"
        )

        # 摘要记忆
        self.summary_memory = ConversationSummaryMemory(
            llm=self.llm,
            input_key="input",
            memory_key="conversation_summary"
        )

        # 知识图谱记忆
        self.kg_memory = ConversationKGMemory(
            llm=self.llm,
            input_key="input",
            memory_key="knowledge_graph"
        )

        # 组合记忆
        self.combined_memory = CombinedMemory(
            memories=[
                self.conversation_memory,
                self.summary_memory,
                self.kg_memory
            ]
        )

        # 项目记忆
        self.project_memory = ProjectMemory()

        # 长期记忆存储
        self.long_term_memory: Dict[str, List[MemoryEntry]] = {}

        # 记忆配置
        self.memory_config = {
            'max_conversation_messages': 1000,
            'summary_threshold': 50,
            'importance_threshold': 0.7,
            'retention_period_days': 30
        }

    def _initialize_llm(self):
        """初始化LLM"""
        if self.config.ai_model and self.config.ai_model.startswith('gpt'):
            return ChatOpenAI(model=self.config.ai_model, temperature=0.1)
        elif self.config.ai_model and self.config.ai_model.startswith('claude'):
            return ChatAnthropic(model=self.config.ai_model, temperature=0.1)
        else:
            return ChatOpenAI(model="gpt-4", temperature=0.1)

    def add_conversation(self, user_input: str, assistant_response: str, metadata: Dict[str, Any] = None):
        """添加对话记录"""
        # 添加到对话记忆
        self.conversation_memory.save_context(
            {"input": user_input},
            {"output": assistant_response}
        )

        # 自动生成摘要
        self._auto_summarize()

        # 提取知识图谱
        self._extract_knowledge_graph(user_input, assistant_response)

        # 记录到长期记忆
        self._add_to_long_term_memory(
            content=f"User: {user_input}\nAssistant: {assistant_response}",
            type="conversation",
            importance=self._calculate_importance(user_input, assistant_response),
            metadata=metadata or {}
        )

    def add_analysis_result(self, file_path: str, analysis_result: Dict[str, Any]):
        """添加分析结果到项目记忆"""
        timestamp = datetime.now()

        # 更新文件分析记录
        self.project_memory.file_analyses[file_path] = {
            'last_analysis': analysis_result,
            'analysis_count': self.project_memory.file_analyses.get(file_path, {}).get('analysis_count', 0) + 1,
            'first_analysis': self.project_memory.file_analyses.get(file_path, {}).get('first_analysis', timestamp),
            'last_analysis_timestamp': timestamp
        }

        # 提取问题模式
        self._extract_issue_patterns(file_path, analysis_result)

        # 记录到长期记忆
        self._add_to_long_term_memory(
            content=f"Analysis of {file_path}: {analysis_result}",
            type="analysis",
            importance=0.8,
            metadata={'file_path': file_path, 'analysis_result': analysis_result}
        )

    def add_repair_result(self, issue_id: str, repair_result: Dict[str, Any]):
        """添加修复结果到项目记忆"""
        self.project_memory.repair_history[issue_id] = {
            'repair_result': repair_result,
            'timestamp': datetime.now(),
            'success_rate': repair_result.get('success', False)
        }

        # 更新成功率统计
        strategy = repair_result.get('strategy', 'unknown')
        current_rate = self.project_memory.success_rates.get(strategy, 0.5)
        success = repair_result.get('success', False)

        # 简单的移动平均更新
        new_rate = current_rate * 0.9 + (1.0 if success else 0.0) * 0.1
        self.project_memory.success_rates[strategy] = new_rate

        # 记录到长期记忆
        self._add_to_long_term_memory(
            content=f"Repair of {issue_id}: {repair_result}",
            type="repair",
            importance=0.9 if success else 0.5,
            metadata={'issue_id': issue_id, 'repair_result': repair_result}
        )

    def add_code_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """添加代码模式"""
        if pattern_type not in self.project_memory.code_patterns:
            self.project_memory.code_patterns[pattern_type] = []

        self.project_memory.code_patterns[pattern_type].append({
            'pattern_data': pattern_data,
            'timestamp': datetime.now(),
            'frequency': self.project_memory.code_patterns[pattern_type].count(pattern_data) + 1
        })

    def get_relevant_context(self, query: str, context_type: str = "all") -> Dict[str, Any]:
        """获取相关上下文"""
        context = {}

        if context_type in ["all", "conversation"]:
            context['recent_conversation'] = self.conversation_memory.load_memory_variables({})
            context['conversation_summary'] = self.summary_memory.load_memory_variables({})

        if context_type in ["all", "knowledge"]:
            context['knowledge_graph'] = self.kg_memory.load_memory_variables({})

        if context_type in ["all", "project"]:
            context['project_memory'] = self._get_project_memory_summary()

        if context_type in ["all", "long_term"]:
            context['long_term_memory'] = self._search_long_term_memory(query)

        return context

    def search_memory(self, query: str, memory_type: str = "all", limit: int = 10) -> List[MemoryEntry]:
        """搜索记忆"""
        results = []

        if memory_type in ["all", "long_term"]:
            results.extend(self._search_long_term_memory(query))

        if memory_type in ["all", "project"]:
            results.extend(self._search_project_memory(query))

        # 按重要性排序
        results.sort(key=lambda x: x.importance, reverse=True)

        return results[:limit]

    def _auto_summarize(self):
        """自动生成摘要"""
        messages = self.conversation_memory.chat_memory.messages

        if len(messages) >= self.memory_config['summary_threshold']:
            # 触发摘要生成
            self.summary_memory.predict_new_summary(
                input_text=messages[-1].content if messages else ""
            )

    def _extract_knowledge_graph(self, user_input: str, assistant_response: str):
        """提取知识图谱"""
        combined_text = f"{user_input} {assistant_response}"

        # 使用KG记忆自动提取实体和关系
        self.kg_memory.save_context(
            {"input": user_input},
            {"output": assistant_response}
        )

    def _extract_issue_patterns(self, file_path: str, analysis_result: Dict[str, Any]):
        """提取问题模式"""
        issues = analysis_result.get('issues', [])

        for issue in issues:
            issue_type = issue.get('type', 'unknown')

            if issue_type not in self.project_memory.issue_patterns:
                self.project_memory.issue_patterns[issue_type] = []

            # 添加模式记录
            pattern = {
                'file_path': file_path,
                'issue': issue,
                'timestamp': datetime.now(),
                'context': analysis_result.get('context', {})
            }

            self.project_memory.issue_patterns[issue_type].append(pattern)

    def _add_to_long_term_memory(self, content: str, type: str, importance: float, metadata: Dict[str, Any]):
        """添加到长期记忆"""
        entry = MemoryEntry(
            id=f"{type}_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            content=content,
            type=type,
            importance=importance,
            metadata=metadata,
            access_count=0
        )

        if type not in self.long_term_memory:
            self.long_term_memory[type] = []

        self.long_term_memory[type].append(entry)

        # 清理低重要性的记忆
        self._cleanup_low_importance_memory()

    def _search_long_term_memory(self, query: str) -> List[MemoryEntry]:
        """搜索长期记忆"""
        results = []
        query_lower = query.lower()

        for memory_type, entries in self.long_term_memory.items():
            for entry in entries:
                if query_lower in entry.content.lower():
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    results.append(entry)

        return results

    def _search_project_memory(self, query: str) -> List[MemoryEntry]:
        """搜索项目记忆"""
        results = []
        query_lower = query.lower()

        # 搜索文件分析记录
        for file_path, analysis in self.project_memory.file_analyses.items():
            if query_lower in file_path.lower():
                results.append(MemoryEntry(
                    id=f"file_analysis_{file_path}",
                    timestamp=analysis.get('last_analysis_timestamp', datetime.now()),
                    content=f"File analysis: {file_path}",
                    type="file_analysis",
                    importance=0.7
                ))

        # 搜索问题模式
        for issue_type, patterns in self.project_memory.issue_patterns.items():
            if query_lower in issue_type.lower():
                for pattern in patterns:
                    results.append(MemoryEntry(
                        id=f"issue_pattern_{pattern['timestamp'].isoformat()}",
                        timestamp=pattern['timestamp'],
                        content=f"Issue pattern: {issue_type}",
                        type="issue_pattern",
                        importance=0.8
                    ))

        return results

    def _get_project_memory_summary(self) -> Dict[str, Any]:
        """获取项目记忆摘要"""
        return {
            'total_files_analyzed': len(self.project_memory.file_analyses),
            'total_issue_patterns': len(self.project_memory.issue_patterns),
            'total_repairs': len(self.project_memory.repair_history),
            'success_rates': self.project_memory.success_rates,
            'code_patterns_count': len(self.project_memory.code_patterns),
            'most_analyzed_files': self._get_most_analyzed_files(),
            'common_issue_types': self._get_common_issue_types()
        }

    def _get_most_analyzed_files(self) -> List[str]:
        """获取分析最频繁的文件"""
        files_with_count = [
            (file_path, data.get('analysis_count', 0))
            for file_path, data in self.project_memory.file_analyses.items()
        ]
        return [file_path for file_path, count in sorted(files_with_count, key=lambda x: x[1], reverse=True)[:5]]

    def _get_common_issue_types(self) -> List[str]:
        """获取最常见的问题类型"""
        issue_counts = [
            (issue_type, len(patterns))
            for issue_type, patterns in self.project_memory.issue_patterns.items()
        ]
        return [issue_type for issue_type, count in sorted(issue_counts, key=lambda x: x[1], reverse=True)[:5]]

    def _calculate_importance(self, user_input: str, assistant_response: str) -> float:
        """计算重要性分数"""
        importance = 0.5  # 基础重要性

        # 基于关键词提升重要性
        important_keywords = ['error', 'bug', 'issue', 'problem', 'fix', 'repair', 'security', 'performance']

        for keyword in important_keywords:
            if keyword in user_input.lower() or keyword in assistant_response.lower():
                importance += 0.1

        # 基于长度调整重要性
        total_length = len(user_input) + len(assistant_response)
        if total_length > 500:
            importance += 0.1

        return min(1.0, importance)

    def _cleanup_low_importance_memory(self):
        """清理低重要性记忆"""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for memory_type, entries in self.long_term_memory.items():
            # 保留重要性和访问频率较高的记忆
            entries.sort(key=lambda x: (x.importance, x.access_count), reverse=True)

            # 只保留前100个最重要的记忆
            if len(entries) > 100:
                self.long_term_memory[memory_type] = entries[:100]

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return {
            'conversation_messages': len(self.conversation_memory.chat_memory.messages),
            'summary_length': len(self.summary_memory.buffer) if self.summary_memory.buffer else 0,
            'knowledge_graph_entities': len(self.kg_memory.kg.entities) if hasattr(self.kg_memory, 'kg') else 0,
            'project_memory': {
                'files_analyzed': len(self.project_memory.file_analyses),
                'issue_patterns': len(self.project_memory.issue_patterns),
                'repairs_history': len(self.project_memory.repair_history),
                'success_rates': self.project_memory.success_rates
            },
            'long_term_memory': {
                'total_entries': sum(len(entries) for entries in self.long_term_memory.values()),
                'memory_types': list(self.long_term_memory.keys()),
                'average_importance': sum(
                    entry.importance
                    for entries in self.long_term_memory.values()
                    for entry in entries
                ) / sum(len(entries) for entries in self.long_term_memory.values()) if self.long_term_memory else 0
            }
        }

    def export_memory(self) -> Dict[str, Any]:
        """导出所有记忆数据"""
        return {
            'conversation_memory': self.conversation_memory.load_memory_variables({}),
            'summary_memory': self.summary_memory.buffer,
            'knowledge_graph': {
                'entities': list(self.kg_memory.kg.entities) if hasattr(self.kg_memory, 'kg') else [],
                'relations': list(self.kg_memory.kg.relations) if hasattr(self.kg_memory, 'kg') else []
            },
            'project_memory': self.project_memory.__dict__,
            'long_term_memory': {
                memory_type: [
                    {
                        'id': entry.id,
                        'timestamp': entry.timestamp.isoformat(),
                        'content': entry.content,
                        'type': entry.type,
                        'importance': entry.importance,
                        'access_count': entry.access_count,
                        'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None,
                        'metadata': entry.metadata
                    }
                    for entry in entries
                ]
                for memory_type, entries in self.long_term_memory.items()
            },
            'memory_stats': self.get_memory_stats()
        }

    def clear_memory(self, memory_type: str = "all"):
        """清理记忆"""
        if memory_type in ["all", "conversation"]:
            self.conversation_memory.clear()
            self.summary_memory.clear()
            self.kg_memory.clear()

        if memory_type in ["all", "project"]:
            self.project_memory = ProjectMemory()

        if memory_type in ["all", "long_term"]:
            self.long_term_memory.clear()

    def optimize_memory(self):
        """优化记忆存储"""
        # 清理低重要性记忆
        self._cleanup_low_importance_memory()

        # 压缩对话记忆
        if len(self.conversation_memory.chat_memory.messages) > self.memory_config['max_conversation_messages']:
            # 保留最近的500条消息
            self.conversation_memory.chat_memory.messages = self.conversation_memory.chat_memory.messages[-500:]

        # 重新生成摘要
        if self.conversation_memory.chat_memory.messages:
            recent_messages = self.conversation_memory.chat_memory.messages[-10:]
            combined_text = " ".join([msg.content for msg in recent_messages])
            self.summary_memory.buffer = combined_text[:500] + "..." if len(combined_text) > 500 else combined_text