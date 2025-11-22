"""
Sanity-check script to test OpenAI Assistant directly.
Run this outside of FastAPI to verify the assistant configuration.
"""
import os
import time
from openai import OpenAI
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create httpx client explicitly to avoid proxies parameter issue
http_client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
)

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    http_client=http_client
)

ASSISTANT_ID = "asst_OLMs1Ux3tI60PidqhnlmXHgl"

# Try testing with a different model by creating a temporary assistant
TEST_WITH_DIFFERENT_MODEL = False  # Set to True to test with gpt-4o-mini

print("=" * 60)
print("Testing OpenAI Assistant Directly")
print("=" * 60)
print(f"Assistant ID: {ASSISTANT_ID}")
print(f"API Key present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
print()

try:
    # Optionally test with a different model
    if TEST_WITH_DIFFERENT_MODEL:
        print("Creating temporary test assistant with gpt-4o-mini...")
        test_assistant = client.beta.assistants.create(
            name="Temp Test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
        )
        test_assistant_id = test_assistant.id
        print(f"Using test assistant: {test_assistant_id}")
    else:
        test_assistant_id = ASSISTANT_ID
        test_assistant = None
    
    # Create a thread
    print("1. Creating thread...")
    thread = client.beta.threads.create()
    print(f"   [OK] Thread created: {thread.id}")
    print()

    # Add a simple message
    print("2. Sending message 'Hi'...")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi"
    )
    print(f"   [OK] Message sent: {message.id}")
    print()

    # Run the assistant
    print("3. Creating run...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=test_assistant_id,
    )
    print(f"   [OK] Run created: {run.id}")
    print()

    # Poll until completed
    print("4. Polling for completion...")
    poll_count = 0
    max_polls = 60
    
    while poll_count < max_polls:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"   Poll {poll_count + 1}: Status = {run.status}")
        
        # Check for errors during polling
        if hasattr(run, 'last_error') and run.last_error:
            error_code = getattr(run.last_error, 'code', None)
            error_message = getattr(run.last_error, 'message', None)
            print(f"   [WARNING] Error detected: Code={error_code}, Message={error_message}")
        
        # Check for required_action (function calling)
        if hasattr(run, 'required_action') and run.required_action:
            print(f"   [WARNING] Required action detected: {run.required_action}")
            if hasattr(run.required_action, 'submit_tool_outputs'):
                tool_calls = getattr(run.required_action.submit_tool_outputs, 'tool_calls', [])
                print(f"   [WARNING] Tool calls needed: {len(tool_calls)}")
                for i, tc in enumerate(tool_calls):
                    func_obj = getattr(tc, 'function', None) if hasattr(tc, 'function') else None
                    func_name = getattr(func_obj, 'name', None) if func_obj else "unknown"
                    func_args = getattr(func_obj, 'arguments', None) if func_obj else "{}"
                    print(f"      Tool call {i+1}: {func_name}({func_args})")
        
        if run.status in ("completed", "failed", "cancelled", "expired"):
            break
        
        poll_count += 1
        time.sleep(1)
    
    print()
    print("=" * 60)
    print("Final Status:", run.status)
    print("=" * 60)
    
    if run.status == "completed":
        print("\n[SUCCESS] Run completed successfully!")
        print("\nMessages:")
        messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        for m in messages.data:
            if m.role == "assistant" and m.content:
                for content in m.content:
                    # Check if it's a text content block
                    if hasattr(content, 'type') and content.type == 'text':
                        if hasattr(content, 'text') and hasattr(content.text, 'value'):
                            print(f"\n{m.role.upper()}: {content.text.value}")
                        else:
                            print(f"\n{m.role.upper()}: [Text content without value]")
                    elif hasattr(content, 'type'):
                        print(f"\n{m.role.upper()}: [Content type: {content.type}]")
                    else:
                        print(f"\n{m.role.upper()}: [Unknown content format]")
    else:
        print("\n[FAILED] Run failed or was cancelled/expired")
        if hasattr(run, 'last_error') and run.last_error:
            error_code = getattr(run.last_error, 'code', None)
            error_type = getattr(run.last_error, 'type', None)
            error_message = getattr(run.last_error, 'message', None)
            print(f"\nError Details:")
            print(f"  Code: {error_code}")
            print(f"  Type: {error_type}")
            print(f"  Message: {error_message}")
            print(f"  Full error: {run.last_error}")
        else:
            print("  No error details available")
    
    # Clean up test assistant if created
    if test_assistant:
        print("\nCleaning up test assistant...")
        client.beta.assistants.delete(assistant_id=test_assistant.id)
        print("   [OK] Test assistant deleted")
    
    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)
    
    if run.status == "failed":
        print("\nTROUBLESHOOTING:")
        print("1. Check OpenAI status: https://status.openai.com")
        print("2. Verify your API key has access to Assistants API")
        print("3. Check if your account has usage/quota issues")
        print("4. Try a different model (set TEST_WITH_DIFFERENT_MODEL = True)")
        print("5. The model 'gpt-4.1-mini' might not be available - try 'gpt-4o-mini'")

except Exception as e:
    print(f"\n[ERROR] Exception occurred: {e}")
    import traceback
    traceback.print_exc()

