"""
Constants for Debug Agent
定义项目中使用的常量
"""

import os

# 项目信息
PROJECT_NAME = "Debug Agent"
PROJECT_VERSION = "0.1.0"
PROJECT_DESCRIPTION = "AI-powered code analysis and repair system"

# 文件类型支持
SUPPORTED_FILE_TYPES = {
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

# 默认配置
DEFAULT_CONFIG = {
    'log_level': 'INFO',
    'max_file_size': 1024 * 1024,  # 1MB
    'timeout': 30,  # 30 seconds
    'max_retries': 3,
    'parallel_analysis': True,
    'enable_ai_analysis': True,
    'enable_auto_repair': True
}

# AI模型配置
AI_MODELS = {
    'zhipuai': {
        'model': 'glm-4.5',
        'max_tokens': 1000,
        'temperature': 0.3,
        'timeout': 30
    },
    'openai': {
        'model': 'gpt-4',
        'max_tokens': 1000,
        'temperature': 0.3,
        'timeout': 30
    }
}

# 分析规则
ANALYSIS_RULES = {
    'security': {
        'enabled': True,
        'severity_threshold': 'MEDIUM',
        'rules': [
            'hardcoded_passwords',
            'sql_injection',
            'xss_vulnerability',
            'insecure_random',
            'path_traversal'
        ]
    },
    'quality': {
        'enabled': True,
        'severity_threshold': 'LOW',
        'rules': [
            'todo_comments',
            'fixme_comments',
            'long_lines',
            'complex_functions',
            'unused_imports',
            'magic_numbers'
        ]
    },
    'performance': {
        'enabled': True,
        'severity_threshold': 'MEDIUM',
        'rules': [
            'inefficient_loops',
            'memory_leaks',
            'slow_database_queries',
            'blocking_operations'
        ]
    }
}

# 修复策略
REPAIR_STRATEGIES = {
    'security': {
        'enabled': True,
        'confidence_threshold': 0.8,
        'strategies': [
            'replace_hardcoded_secrets',
            'sanitize_input',
            'use_secure_random',
            'parameterize_queries'
        ]
    },
    'quality': {
        'enabled': True,
        'confidence_threshold': 0.7,
        'strategies': [
            'refactor_complex_functions',
            'remove_unused_code',
            'extract_constants',
            'improve_naming'
        ]
    },
    'performance': {
        'enabled': True,
        'confidence_threshold': 0.6,
        'strategies': [
            'optimize_loops',
            'add_caching',
            'use_async_operations',
            'optimize_memory_usage'
        ]
    }
}

# 测试配置
TEST_CONFIG = {
    'max_test_cases': 50,
    'test_timeout': 10,
    'coverage_threshold': 0.8,
    'enable_ai_test_generation': True
}

# 报告配置
REPORT_CONFIG = {
    'formats': ['json', 'html', 'console'],
    'include_source_code': True,
    'include_metrics': True,
    'include_suggestions': True
}

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, '..', 'configs')
LOGS_DIR = os.path.join(BASE_DIR, '..', 'logs')
REPORTS_DIR = os.path.join(BASE_DIR, '..', 'reports')
EXPERIMENTS_DIR = os.path.join(BASE_DIR, '..', 'experiments')

# 环境变量
ENV_VARS = {
    'ZHIPUAI_API_KEY': 'ZhipuAI API Key',
    'OPENAI_API_KEY': 'OpenAI API Key',
    'DEBUG_LEVEL': 'Debug Level (DEBUG, INFO, WARNING, ERROR)',
    'MAX_PARALLEL_JOBS': 'Maximum parallel jobs',
    'ENABLE_AI_ANALYSIS': 'Enable AI analysis (true/false)'
}

# 错误代码
ERROR_CODES = {
    'ANALYSIS_FAILED': 'E001',
    'REPAIR_FAILED': 'E002',
    'TEST_GENERATION_FAILED': 'E003',
    'VALIDATION_FAILED': 'E004',
    'TIMEOUT_EXCEEDED': 'E005',
    'RESOURCE_LIMIT_EXCEEDED': 'E006',
    'CONFIGURATION_ERROR': 'E007',
    'FILE_NOT_FOUND': 'E008',
    'PERMISSION_DENIED': 'E009'
}

# 成功代码
SUCCESS_CODES = {
    'ANALYSIS_COMPLETED': 'S001',
    'REPAIR_COMPLETED': 'S002',
    'TEST_GENERATED': 'S003',
    'VALIDATION_PASSED': 'S004',
    'WORKFLOW_COMPLETED': 'S005'
}