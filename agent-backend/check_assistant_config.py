"""
Script to check the assistant configuration and list all functions.
This helps identify configuration issues.
"""
import os
import httpx
from openai import OpenAI
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

print("=" * 60)
print("Checking Assistant Configuration")
print("=" * 60)
print(f"Assistant ID: {ASSISTANT_ID}")
print()

try:
    # Retrieve the assistant
    assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)
    
    print("Assistant Details:")
    print(f"  Name: {assistant.name}")
    print(f"  Model: {assistant.model}")
    if assistant.instructions:
        # Encode to handle Unicode characters in Windows console
        try:
            instructions_preview = assistant.instructions[:200].encode('ascii', 'replace').decode('ascii')
            print(f"  Instructions: {instructions_preview}...")
        except:
            print(f"  Instructions: [Contains Unicode - {len(assistant.instructions)} chars]")
    else:
        print(f"  Instructions: None")
    
    # Check response format
    response_format = getattr(assistant, 'response_format', None)
    if response_format:
        if hasattr(response_format, 'type'):
            print(f"  Response Format Type: {response_format.type}")
        else:
            print(f"  Response Format: {response_format}")
    else:
        print(f"  Response Format: Not set (default)")
    
    # Check all attributes
    print(f"  All attributes: {[attr for attr in dir(assistant) if not attr.startswith('_')]}")
    print()
    
    # Check tools/functions
    if hasattr(assistant, 'tools') and assistant.tools:
        print(f"Tools/Functions configured: {len(assistant.tools)}")
        print()
        
        for i, tool in enumerate(assistant.tools, 1):
            print(f"Tool {i}:")
            if hasattr(tool, 'type'):
                print(f"  Type: {tool.type}")
            
            if hasattr(tool, 'function'):
                func = tool.function
                print(f"  Function Name: {func.name if hasattr(func, 'name') else 'N/A'}")
                print(f"  Description: {func.description if hasattr(func, 'description') else 'N/A'}")
                
                if hasattr(func, 'parameters'):
                    params = func.parameters
                    print(f"  Parameters: {params}")
                    
                    # Check for invalid fields
                    if isinstance(params, dict):
                        if 'strict' in params:
                            print(f"  [ERROR] Found 'strict' field - THIS IS INVALID! Remove it.")
                        if 'format' in params.get('properties', {}).get('date_posted_from', {}):
                            print(f"  [WARNING] Found 'format' in date_posted_from - may cause issues")
            print()
    else:
        print("No tools/functions configured")
        print()
    
    print("=" * 60)
    print("Configuration Check Complete")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. If you see '[ERROR] Found strict field', remove it from the function definition")
    print("2. Go to https://platform.openai.com/assistants")
    print("3. Edit your assistant and fix the function definition")
    print("4. Run test_assistant.py again to verify")

except Exception as e:
    print(f"[ERROR] Exception occurred: {e}")
    import traceback
    traceback.print_exc()

