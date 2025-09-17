#!/usr/bin/env python3
"""
Debug Agent Core Implementation
AI-powered code analysis and bug detection system
"""
import os
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    """Analysis result data structure"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    suggestion: str
    confidence: float

class DebugAgent:
    """Main Debug Agent class for code analysis"""

    def __init__(self, api_key: str = None):
        """Initialize Debug Agent with ZhipuAI API"""
        self.api_key = api_key or os.getenv('ZHIPUAI_API_KEY')
        self.logger = self._setup_logger()
        self.analysis_history = []

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analyze_code(self, code: str, file_path: str) -> List[AnalysisResult]:
        """
        Analyze code for potential bugs and quality issues

        Args:
            code: Source code to analyze
            file_path: Path of the file being analyzed

        Returns:
            List of AnalysisResult objects
        """
        self.logger.info(f"Analyzing code in {file_path}")

        results = []

        # Basic static analysis
        static_results = self._static_analysis(code, file_path)
        results.extend(static_results)

        # AI-powered analysis (if API key available)
        if self.api_key:
            ai_results = self._ai_analysis(code, file_path)
            results.extend(ai_results)

        # Store analysis history
        self.analysis_history.append({
            'file_path': file_path,
            'timestamp': str(__import__('datetime').datetime.now()),
            'results_count': len(results)
        })

        return results

    def _static_analysis(self, code: str, file_path: str) -> List[AnalysisResult]:
        """Perform static code analysis"""
        results = []
        lines = code.split('\n')

        # Basic pattern detection
        for i, line in enumerate(lines, 1):
            # Check for potential security issues
            if 'password' in line.lower() and '=' in line:
                results.append(AnalysisResult(
                    file_path=file_path,
                    line_number=i,
                    issue_type='security',
                    severity='high',
                    description='Potential hardcoded password detected',
                    suggestion='Use environment variables or secure storage',
                    confidence=0.8
                ))

            # Check for TODO comments
            if 'todo' in line.lower() or 'fixme' in line.lower():
                results.append(AnalysisResult(
                    file_path=file_path,
                    line_number=i,
                    issue_type='documentation',
                    severity='low',
                    description='TODO/FIXME comment found',
                    suggestion='Address the TODO item or create proper issue',
                    confidence=0.9
                ))

        return results

    def _ai_analysis(self, code: str, file_path: str) -> List[AnalysisResult]:
        """Perform AI-powered code analysis using ZhipuAI"""
        try:
            import zhipuai

            client = zhipuai.ZhipuAI(api_key=self.api_key)

            prompt = f"""
            As a code analysis expert, please analyze the following code for potential bugs, security issues, and quality problems:

            File: {file_path}
            Code:
            ```python
            {code[:1000]}  # Limit code length
            ```

            Please provide a JSON response with the following structure:
            {{
                "issues": [
                    {{
                        "line_number": integer,
                        "issue_type": "security|performance|logic|quality",
                        "severity": "low|medium|high|critical",
                        "description": "Detailed description of the issue",
                        "suggestion": "Specific suggestion to fix the issue",
                        "confidence": float between 0 and 1
                    }}
                ]
            }}
            """

            response = client.chat.completions.create(
                model="glm-4.5",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            # Parse AI response
            ai_content = response.choices[0].message.content
            self.logger.info(f"AI analysis completed for {file_path}")

            # For now, return empty list (will implement JSON parsing later)
            return []

        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return []

    def generate_report(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        report = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'total_issues': len(results),
            'issues_by_type': {},
            'issues_by_severity': {},
            'files_analyzed': len(set(r.file_path for r in results)),
            'detailed_results': []
        }

        # Categorize results
        for result in results:
            # By type
            if result.issue_type not in report['issues_by_type']:
                report['issues_by_type'][result.issue_type] = 0
            report['issues_by_type'][result.issue_type] += 1

            # By severity
            if result.severity not in report['issues_by_severity']:
                report['issues_by_severity'][result.severity] = 0
            report['issues_by_severity'][result.severity] += 1

            # Detailed results
            report['detailed_results'].append({
                'file': result.file_path,
                'line': result.line_number,
                'type': result.issue_type,
                'severity': result.severity,
                'description': result.description,
                'suggestion': result.suggestion,
                'confidence': result.confidence
            })

        return report

    def get_quality_score(self, results: List[AnalysisResult]) -> float:
        """Calculate overall quality score (0-100)"""
        if not results:
            return 100.0

        # Weight different severity levels
        weights = {'critical': 3.0, 'high': 2.0, 'medium': 1.0, 'low': 0.5}

        total_penalty = sum(weights.get(r.severity, 1.0) for r in results)
        max_penalty = len(results) * 3.0  # Maximum possible penalty

        score = max(0, 100 - (total_penalty / max_penalty) * 100)
        return round(score, 2)

    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """Analyze all Python files in a directory"""
        import os
        import glob

        all_results = []
        python_files = glob.glob(os.path.join(directory, '**', '*.py'), recursive=True)

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                results = self.analyze_code(code, file_path)
                all_results.extend(results)
            except Exception as e:
                self.logger.error(f"Failed to analyze {file_path}: {e}")

        report = self.generate_report(all_results)
        report['quality_score'] = self.get_quality_score(all_results)
        report['files_analyzed'] = len(python_files)

        return report

if __name__ == "__main__":
    # Test the Debug Agent
    agent = DebugAgent()
    test_code = """
def example_function(password="123456"):
    # TODO: Fix this security issue
    return password
"""
    results = agent.analyze_code(test_code, "test_file.py")
    report = agent.generate_report(results)
    print(json.dumps(report, indent=2))