#!/usr/bin/env python3
"""
Test script to verify ZhipuAI API key integration
"""
import os
import sys
sys.path.append('src')

def test_zhipuai_connection():
    """Test ZhipuAI API connection"""
    try:
        # Test if we can import the library
        import zhipuai

        # Test API key from environment
        api_key = os.getenv('ZHIPUAI_API_KEY')
        if not api_key:
            print("❌ ZHIPUAI_API_KEY not found in environment")
            return False

        print(f"✅ ZHIPUAI_API_KEY found (length: {len(api_key)})")

        # Initialize client
        client = zhipuai.ZhipuAI(api_key=api_key)
        print("✅ ZhipuAI client initialized successfully")

        # Test a simple API call
        try:
            response = client.chat.completions.create(
                model="glm-4.5",
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                max_tokens=50
            )
            print("✅ API call successful")
            print(f"✅ Response: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return False

    except ImportError as e:
        print(f"❌ Failed to import zhipuai: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ZhipuAI API integration...")
    success = test_zhipuai_connection()
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!")
        sys.exit(1)