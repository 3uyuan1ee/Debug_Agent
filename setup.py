"""
Setup script for Debug Agent package
Debug Agent包的安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="debug-agent",
    version="1.0.0",
    author="Debug Agent Team",
    author_email="team@debugagent.com",
    description="AI驱动的代码缺陷检测与修复工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/debugagent/debug-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.6.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "debug-agent=debug_agent.cli:cli",
            "debug-agent-init=debug_agent.cli:init",
            "debug-agent-analyze=debug_agent.cli:analyze",
            "debug-agent-scan=debug_agent.cli:scan",
            "debug-agent-status=debug_agent.cli:status",
        ],
    },
    include_package_data=True,
    package_data={
        "debug_agent": [
            "config.sample.json",
            "*.json",
            "*.yaml",
            "*.yml",
        ],
    },
    zip_safe=False,
    keywords="debug agent code analysis static analysis test-driven repair",
    project_urls={
        "Bug Reports": "https://github.com/debugagent/debug-agent/issues",
        "Source": "https://github.com/debugagent/debug-agent",
        "Documentation": "https://debug-agent.readthedocs.io/",
    },
)