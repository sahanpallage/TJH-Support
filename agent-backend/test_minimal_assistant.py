"""
Test with a minimal assistant to see if the issue is with the specific assistant
or a general problem.
"""
import os
import time
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
print("Testing with Minimal Assistant")
print("=" * 60)

try:
    # Create a minimal assistant
    print("1. Creating minimal test assistant...")
    test_assistant = client.beta.assistants.create(
        name="Test Assistant",
        instructions="You are a helpful assistant. Respond briefly and clearly.",
        model="gpt-4o-mini",  # Using a different model
    )
    print(f"   [OK] Created assistant: {test_assistant.id}")
    print()
    
    # Test it
    print("2. Testing the minimal assistant...")
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Say hello"
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=test_assistant.id,
    )
    
    # Poll
    for i in range(30):
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"   Poll {i+1}: Status = {run.status}")
        
        if hasattr(run, 'last_error') and run.last_error:
            print(f"   [ERROR] {run.last_error}")
        
        if run.status in ("completed", "failed", "cancelled", "expired"):
            break
        time.sleep(1)
    
    if run.status == "completed":
        print("\n[SUCCESS] Minimal assistant works!")
        messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        for m in messages.data:
            if m.role == "assistant" and m.content:
                for content in m.content:
                    if hasattr(content, 'type') and content.type == 'text':
                        if hasattr(content, 'text') and hasattr(content.text, 'value'):
                            print(f"Response: {content.text.value}")
    else:
        print(f"\n[FAILED] Status: {run.status}")
        if hasattr(run, 'last_error') and run.last_error:
            print(f"Error: {run.last_error}")
    
    # Clean up
    print("\n3. Cleaning up test assistant...")
    client.beta.assistants.delete(assistant_id=test_assistant.id)
    print("   [OK] Test assistant deleted")
    
    print("\n" + "=" * 60)
    print("Conclusion:")
    if run.status == "completed":
        print("Minimal assistant works - the issue is with your specific assistant")
        print("Check the assistant instructions or model configuration")
    else:
        print("Even minimal assistant fails - might be an OpenAI API issue")
        print("Check OpenAI status page: https://status.openai.com")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

