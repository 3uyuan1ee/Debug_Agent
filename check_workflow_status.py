#!/usr/bin/env python3
"""
Check workflow implementation and provide setup guidance
"""
import os
import json
from pathlib import Path

def check_workflow_setup():
    """Check if workflow is properly set up"""
    print("🔍 Checking GitHub Actions workflow setup...")
    print("=" * 50)

    checks = []

    # Check workflow files
    workflow_dir = Path(".github/workflows")
    if workflow_dir.exists():
        workflow_files = list(workflow_dir.glob("*.yml"))
        checks.append(("Workflow files", f"✅ Found {len(workflow_files)} workflow files"))

        for file in workflow_files:
            if file.name == "bug-detection.yml":
                checks.append(("Main workflow", "✅ bug-detection.yml found"))
                with open(file, 'r') as f:
                    content = f.read()
                    if "ZHIPUAI_API_KEY" in content:
                        checks.append(("ZhipuAI integration", "✅ API key configured"))
                    else:
                        checks.append(("ZhipuAI integration", "❌ API key not configured"))
    else:
        checks.append(("Workflow directory", "❌ .github/workflows not found"))

    # Check Agent implementation
    agent_file = "src/agents/debug_agent.py"
    if os.path.exists(agent_file):
        checks.append(("Agent core", "✅ Debug Agent implemented"))
        with open(agent_file, 'r') as f:
            content = f.read()
            if "zhipuai" in content.lower():
                checks.append(("ZhipuAI usage", "✅ Agent uses ZhipuAI"))
            else:
                checks.append(("ZhipuAI usage", "⚠️ Agent may not use ZhipuAI"))
    else:
        checks.append(("Agent core", "❌ Debug Agent not found"))

    # Check configuration
    config_file = ".github/agent-config.yml"
    if os.path.exists(config_file):
        checks.append(("Agent config", "✅ Configuration file found"))
        with open(config_file, 'r') as f:
            content = f.read()
            if "glm-4.5" in content:
                checks.append(("GLM-4.5 config", "✅ GLM-4.5 configured"))
            else:
                checks.append(("GLM-4.5 config", "❌ GLM-4.5 not configured"))
    else:
        checks.append(("Agent config", "❌ Configuration file not found"))

    # Print results
    for check, status in checks:
        print(f"{check:.<30} {status}")

    print("\n📋 Summary:")
    success_count = sum(1 for _, status in checks if "✅" in status)
    total_count = len(checks)
    print(f"Setup completeness: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    if success_count == total_count:
        print("\n🎉 All checks passed! Workflow should work correctly.")
        print("\n🚀 To test the workflow:")
        print("1. Make a commit to trigger the workflow")
        print("2. Check GitHub Actions tab for results")
        print("3. Look for analysis reports in Artifacts")
    else:
        print(f"\n⚠️  {total_count - success_count} issues found. Please fix them.")

    return success_count == total_count

def print_next_steps():
    """Print next steps for the user"""
    print("\n📝 Next Steps:")
    print("1. ✅ Set up ZHIPUAI_API_KEY in GitHub repository secrets")
    print("2. ✅ Implement Debug Agent core functionality")
    print("3. 🔄 Test workflow by making a commit")
    print("4. 📊 Check analysis results in GitHub Actions")
    print("5. 🎯 Choose experimental projects for testing")
    print("6. 🔧 Refine Agent based on results")

if __name__ == "__main__":
    success = check_workflow_setup()
    print_next_steps()