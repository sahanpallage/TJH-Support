"""
Check if the model name is valid and list available models.
"""
import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

http_client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
)

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    http_client=http_client
)

print("=" * 60)
print("Checking Model Availability")
print("=" * 60)

# Test different model names
test_models = [
    "gpt-4.1-mini",  # Your current model
    "gpt-4o-mini",   # Common alternative
    "gpt-4-turbo",   # Another option
    "gpt-3.5-turbo", # Fallback
]

print("\nTesting model names by creating test assistants...")
print()

for model in test_models:
    try:
        print(f"Testing model: {model}")
        test_assistant = client.beta.assistants.create(
            name=f"Test {model}",
            instructions="Test",
            model=model,
        )
        print(f"  [OK] Model '{model}' is valid - created assistant: {test_assistant.id}")
        # Clean up
        client.beta.assistants.delete(assistant_id=test_assistant.id)
        print()
    except Exception as e:
        error_msg = str(e)
        if "model" in error_msg.lower() or "invalid" in error_msg.lower():
            print(f"  [ERROR] Model '{model}' is INVALID or not available")
            print(f"  Error: {error_msg[:200]}")
        else:
            print(f"  [WARNING] Unexpected error: {error_msg[:200]}")
        print()

print("=" * 60)
print("Recommendation:")
print("If 'gpt-4.1-mini' shows as invalid, update your assistant to use:")
print("  - gpt-4o-mini (recommended)")
print("  - gpt-4-turbo")
print("  - gpt-3.5-turbo")
print("=" * 60)

