"""
Test script for LLM and Embeddings Fallback functionality.
Tests both primary (Gemini) and fallback (GPT-3.5) providers.
"""

import os
import sys
from dotenv import load_dotenv

# Add Backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.llm_fallback import generate_with_fallback
from core.embeddings_fallback import get_embedding_with_fallback

load_dotenv()

def test_llm_fallback():
    """Test LLM fallback functionality."""
    print("\n" + "="*60)
    print("TEST 1: LLM Fallback (Gemini → GPT-3.5)")
    print("="*60)

    test_prompt = "What is 2+2? Answer with just the number."

    try:
        # Test with valid Gemini key (should use Gemini)
        print("\n✅ Testing with valid Gemini API key...")
        response_text, provider = generate_with_fallback(
            prompt=test_prompt,
            model_gemini="gemini-2.5-flash-lite",
            temperature=0.1
        )
        print(f"✅ Provider used: {provider}")
        print(f"✅ Response: {response_text.strip()}")

        if provider == "gemini":
            print("✅ PRIMARY PROVIDER (Gemini) working correctly!")
        else:
            print(f"⚠️  Used fallback provider: {provider}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_embeddings_fallback():
    """Test embeddings fallback functionality."""
    print("\n" + "="*60)
    print("TEST 2: Embeddings Fallback (Gemini → OpenAI)")
    print("="*60)

    test_text = "Python programming"

    try:
        # Test with valid Gemini key (should use Gemini)
        print("\n✅ Testing with valid Gemini API key...")
        embedding, provider = get_embedding_with_fallback(test_text)
        print(f"✅ Provider used: {provider}")
        print(f"✅ Embedding dimensions: {len(embedding)}")
        print(f"✅ First 5 values: {embedding[:5]}")

        if provider == "gemini":
            print("✅ PRIMARY PROVIDER (Gemini) working correctly!")
            if len(embedding) == 768:
                print("✅ Embedding dimension is correct (768)")
            else:
                print(f"⚠️  Expected 768 dimensions, got {len(embedding)}")
        else:
            print(f"⚠️  Used fallback provider: {provider}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_invalid_gemini_key():
    """Test fallback with invalid Gemini key (manual test)."""
    print("\n" + "="*60)
    print("TEST 3: Fallback with Invalid Gemini Key")
    print("="*60)

    print("\nℹ️  To test fallback with invalid Gemini key:")
    print("1. Temporarily set GEMINI_API_KEY to an invalid value in .env")
    print("2. Run this script again")
    print("3. You should see 'openai' as the provider used")
    print("4. Don't forget to restore the valid Gemini key afterwards!")

    print("\n⚠️  This test is MANUAL - not running automatically")
    print("⚠️  to avoid breaking the working configuration")

def test_multiple_llm_calls():
    """Test multiple LLM calls with different models."""
    print("\n" + "="*60)
    print("TEST 4: Multiple LLM Calls with Different Models")
    print("="*60)

    test_cases = [
        ("gemini-2.5-flash-lite", "What is the capital of France?"),
        ("gemini-2.0-flash-exp", "List 3 programming languages."),
    ]

    for model, prompt in test_cases:
        print(f"\n✅ Testing with model: {model}")
        try:
            response_text, provider = generate_with_fallback(
                prompt=prompt,
                model_gemini=model,
                temperature=0.2
            )
            print(f"   Provider: {provider}")
            print(f"   Response: {response_text.strip()[:100]}...")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting LLM & Embeddings Fallback Tests")
    print("="*60)

    # Check API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not gemini_key:
        print("❌ GEMINI_API_KEY not set in environment")
        sys.exit(1)
    else:
        print(f"✅ GEMINI_API_KEY set (length: {len(gemini_key)})")

    if not openai_key:
        print("⚠️  OPENAI_API_KEY not set - fallback will not work")
    else:
        print(f"✅ OPENAI_API_KEY set (length: {len(openai_key)})")

    # Run tests
    test_llm_fallback()
    test_embeddings_fallback()
    test_multiple_llm_calls()
    test_invalid_gemini_key()

    print("\n" + "="*60)
    print("✅ All automatic tests completed!")
    print("="*60)
    print("\nSUMMARY:")
    print("- ✅ LLM fallback structure tested")
    print("- ✅ Embeddings fallback structure tested")
    print("- ✅ Multiple model calls tested")
    print("- ⚠️  Manual test required: Invalid Gemini key fallback")
    print("\n💡 To test actual fallback behavior:")
    print("   1. Temporarily invalidate GEMINI_API_KEY in .env")
    print("   2. Run this script again")
    print("   3. Verify all calls use 'openai' provider")
    print("   4. Restore valid Gemini key")
    print("="*60 + "\n")
