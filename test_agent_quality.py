#!/usr/bin/env python3
"""
Test script to verify Debug Agent code quality
This simulates what the workflow should analyze
"""
import ast
import sys
import os
from pathlib import Path

def analyze_code_quality(file_path: str) -> dict:
    """Analyze Python code quality"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)
        analyzer = CodeQualityAnalyzer(file_path, code)
        analyzer.visit(tree)

        return {
            'file': file_path,
            'complexity': analyzer.complexity_score,
            'lines_of_code': len(code.split('\n')),
            'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            'issues': analyzer.issues
        }
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e)
        }

class CodeQualityAnalyzer(ast.NodeVisitor):
    """AST-based code quality analyzer"""
    def __init__(self, file_path: str, code: str):
        self.file_path = file_path
        self.code = code
        self.complexity_score = 0
        self.issues = []

    def visit_FunctionDef(self, node):
        # Calculate cyclomatic complexity
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or)):
                complexity += 1

        if complexity > 10:
            self.issues.append({
                'line': node.lineno,
                'type': 'complexity',
                'severity': 'medium',
                'message': f'Function "{node.name}" has high complexity ({complexity})'
            })

        self.complexity_score += complexity
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Check class size
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 10:
            self.issues.append({
                'line': node.lineno,
                'type': 'structure',
                'severity': 'low',
                'message': f'Class "{node.name}" has many methods ({len(methods)})'
            })

        self.generic_visit(node)

def main():
    """Main test function"""
    print("🔍 Testing Debug Agent code quality...")
    print("=" * 50)

    # Analyze our Debug Agent
    agent_file = "src/agents/debug_agent.py"
    if os.path.exists(agent_file):
        result = analyze_code_quality(agent_file)

        print(f"📁 File: {result['file']}")
        print(f"📊 Lines of Code: {result['lines_of_code']}")
        print(f"⚙️  Functions: {result['functions']}")
        print(f"🏗️  Classes: {result['classes']}")
        print(f"🧠 Complexity Score: {result.get('complexity', 0)}")

        if 'issues' in result and result['issues']:
            print("\n⚠️  Issues Found:")
            for issue in result['issues']:
                print(f"   Line {issue['line']}: {issue['message']} ({issue['severity']})")
        else:
            print("\n✅ No quality issues found!")

    else:
        print(f"❌ File {agent_file} not found")

    print("\n🚀 This simulates what the GitHub Actions workflow will analyze")
    print("📈 The workflow will also add AI-powered analysis using GLM-4.5")

if __name__ == "__main__":
    main()