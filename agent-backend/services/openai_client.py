# backend/services/openai_client.py
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure the agent-backend directory is in sys.path for absolute imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from openai import AsyncOpenAI
import httpx
import json
import logging
from config import settings
from services.tool_handlers import handle_tool_call

# Set up logging
logger = logging.getLogger(__name__)


class OpenAIAssistantClient:
    """
    Client for interacting with OpenAI Assistant API directly.
    Handles thread creation, message sending, and file uploads.
    """
    
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "Set it in your backend .env file before using the OpenAIAssistantClient."
            )
        if not settings.OPENAI_ASSISTANT_ID:
            raise RuntimeError(
                "OPENAI_ASSISTANT_ID is not configured. "
                "Set it in your backend .env file before using the OpenAIAssistantClient."
            )
        
        # Create httpx client explicitly to avoid proxies parameter issue
        http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=http_client
        )
        self.assistant_id = settings.OPENAI_ASSISTANT_ID

    async def create_thread(self) -> Dict[str, Any]:
        """
        Create a new thread for the OpenAI assistant.
        Returns a dict with 'thread_id' and 'id' keys for compatibility.
        """
        try:
            thread = await self.client.beta.threads.create()
            print(f"[OpenAIClient] Created thread with ID: {thread.id}")
            return {"thread_id": thread.id, "id": thread.id}
        except Exception as e:
            print(f"[OpenAIClient] Error creating thread: {e}")
            raise

    async def send_message(
        self,
        thread_id: str,
        message: str,
        files: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to the OpenAI assistant in an existing thread.
        
        Args:
            thread_id: The thread ID
            message: The message text
            files: Optional list of file dictionaries (not used directly, files should be uploaded first)
            file_ids: Optional list of file IDs from uploaded files
        """
        try:
            print(f"[OpenAIClient] Sending message to thread: {thread_id}")
            
            # Prepare attachments if file_ids are provided
            attachments = None
            if file_ids:
                print(f"[OpenAIClient] Attaching {len(file_ids)} file(s) to message")
                # Create attachments as dicts (OpenAI SDK will handle the conversion)
                attachments = [
                    {"file_id": file_id, "tools": [{"type": "file_search"}]}
                    for file_id in file_ids
                ]
            
            # Add message to thread
            if attachments:
                # Type ignore: OpenAI SDK accepts dict format for attachments at runtime
                await self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=message,
                    attachments=attachments  # type: ignore[arg-type]
                )
            else:
                await self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=message
                )
            
            # Create and wait for run
            print(f"[OpenAIClient] Creating run with assistant_id: {self.assistant_id}")
            import asyncio
            
            try:
                # Create the run (don't use create_and_poll - we need to handle requires_action manually)
                run = await self.client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant_id
                )
                
                # Poll for completion, handling requires_action status
                max_polls = 60  # Maximum 60 polls (60 seconds)
                poll_count = 0
                
                while poll_count < max_polls:
                    await asyncio.sleep(1)  # Wait 1 second between polls
                    run = await self.client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    
                    print(f"[OpenAIClient] Run status: {run.status} (poll {poll_count + 1})")
                    
                    # Log error immediately if present (even if status isn't "failed" yet)
                    if hasattr(run, 'last_error') and run.last_error:
                        error_code = getattr(run.last_error, 'code', None)
                        error_message = getattr(run.last_error, 'message', None)
                        error_type = getattr(run.last_error, 'type', None)
                        print(f"[OpenAIClient] ⚠️ ERROR detected during polling:")
                        print(f"[OpenAIClient]   - Status: {run.status}")
                        print(f"[OpenAIClient]   - Error Code: {error_code}")
                        print(f"[OpenAIClient]   - Error Type: {error_type}")
                        print(f"[OpenAIClient]   - Error Message: {error_message}")
                        print(f"[OpenAIClient]   - Full error object: {run.last_error}")
                    
                    # Log if requires_action is present
                    if hasattr(run, 'required_action') and run.required_action:
                        print(f"[OpenAIClient] Run has required_action: {run.required_action}")
                        if hasattr(run.required_action, 'submit_tool_outputs'):
                            tool_calls = getattr(run.required_action.submit_tool_outputs, 'tool_calls', [])
                            print(f"[OpenAIClient] Tool calls in required_action: {len(tool_calls)}")
                            for i, tc in enumerate(tool_calls):
                                func_obj = getattr(tc, 'function', None) if hasattr(tc, 'function') else None
                                func_name = getattr(func_obj, 'name', None) if func_obj else "unknown"
                                print(f"[OpenAIClient]   Tool call {i+1}: {func_name}")
                    
                    # If failed, break immediately to get full error details
                    if run.status == "failed":
                        print(f"[OpenAIClient] Run failed - breaking polling loop to capture full error details")
                        break
                    
                    # Handle requires_action (function calling)
                    if run.status == "requires_action":
                        print(f"[OpenAIClient] ========================================")
                        print(f"[OpenAIClient] REQUIRES_ACTION DETECTED")
                        print(f"[OpenAIClient] ========================================")
                        
                        required_action = run.required_action
                        print(f"[OpenAIClient] Required action type: {type(required_action)}")
                        print(f"[OpenAIClient] Required action: {required_action}")
                        
                        if required_action and hasattr(required_action, 'submit_tool_outputs'):
                            submit_tool_outputs = required_action.submit_tool_outputs
                            print(f"[OpenAIClient] submit_tool_outputs type: {type(submit_tool_outputs)}")
                            print(f"[OpenAIClient] submit_tool_outputs: {submit_tool_outputs}")
                            
                            tool_calls = getattr(submit_tool_outputs, 'tool_calls', [])
                            print(f"[OpenAIClient] Number of tool calls: {len(tool_calls)}")
                            print(f"[OpenAIClient] Tool calls type: {type(tool_calls)}")
                            
                            # Process each tool call
                            tool_outputs = []
                            for idx, tool_call in enumerate(tool_calls):
                                print(f"[OpenAIClient] ========================================")
                                print(f"[OpenAIClient] Processing tool call {idx + 1}/{len(tool_calls)}")
                                print(f"[OpenAIClient] ========================================")
                                print(f"[OpenAIClient] Tool call type: {type(tool_call)}")
                                print(f"[OpenAIClient] Tool call: {tool_call}")
                                print(f"[OpenAIClient] Tool call attributes: {[attr for attr in dir(tool_call) if not attr.startswith('_')]}")
                                
                                tool_call_id = getattr(tool_call, 'id', None)
                                print(f"[OpenAIClient] Tool call ID: {tool_call_id}")
                                
                                function_obj = getattr(tool_call, 'function', None) if hasattr(tool_call, 'function') else None
                                print(f"[OpenAIClient] Function object: {function_obj}")
                                print(f"[OpenAIClient] Function object type: {type(function_obj)}")
                                
                                if function_obj:
                                    function_name = getattr(function_obj, 'name', None)
                                    function_args_raw = getattr(function_obj, 'arguments', None)
                                    print(f"[OpenAIClient] Function name: '{function_name}'")
                                    print(f"[OpenAIClient] Function name type: {type(function_name)}")
                                    print(f"[OpenAIClient] Function args (raw): {function_args_raw}")
                                    print(f"[OpenAIClient] Function args type: {type(function_args_raw)}")
                                    
                                    # Parse function arguments (they come as a JSON string from OpenAI)
                                    function_args = {}
                                    if function_args_raw:
                                        if isinstance(function_args_raw, str):
                                            try:
                                                function_args = json.loads(function_args_raw)
                                                print(f"[OpenAIClient] Parsed function args: {function_args}")
                                            except json.JSONDecodeError as e:
                                                print(f"[OpenAIClient] ERROR: Failed to parse function args as JSON: {e}")
                                                print(f"[OpenAIClient] Raw args string: {repr(function_args_raw)}")
                                                function_args = {}
                                        elif isinstance(function_args_raw, dict):
                                            function_args = function_args_raw
                                            print(f"[OpenAIClient] Function args already a dict: {function_args}")
                                        else:
                                            print(f"[OpenAIClient] WARNING: Unexpected function_args type: {type(function_args_raw)}")
                                            function_args = {}
                                    
                                    # Check if function name matches exactly
                                    expected_function_name = "search_recent_jobs"
                                    if function_name != expected_function_name:
                                        print(f"[OpenAIClient] ⚠️  WARNING: Function name mismatch!")
                                        print(f"[OpenAIClient]   Expected: '{expected_function_name}'")
                                        print(f"[OpenAIClient]   Received: '{function_name}'")
                                        print(f"[OpenAIClient]   Match: {function_name == expected_function_name}")
                                    
                                    # Call the tool handler
                                    if not function_name:
                                        print(f"[OpenAIClient] ERROR: function_name is None or empty")
                                        tool_outputs.append({
                                            "tool_call_id": tool_call_id,
                                            "output": json.dumps({"error": "Function name is missing"})
                                        })
                                    else:
                                        print(f"[OpenAIClient] Calling tool handler for: '{function_name}'")
                                        try:
                                            handler_output = await handle_tool_call(function_name, function_args)
                                            print(f"[OpenAIClient] Handler output type: {type(handler_output)}")
                                            print(f"[OpenAIClient] Handler output: {handler_output}")
                                            
                                            # Handler should return a JSON string, but ensure it's valid
                                            if isinstance(handler_output, str):
                                                # Validate it's valid JSON
                                                try:
                                                    json.loads(handler_output)
                                                    output_str = handler_output
                                                except json.JSONDecodeError:
                                                    # Wrap in JSON if not valid
                                                    output_str = json.dumps({"result": handler_output})
                                            else:
                                                # Convert to JSON string
                                                output_str = json.dumps(handler_output)
                                            
                                            tool_outputs.append({
                                                "tool_call_id": tool_call_id,
                                                "output": output_str
                                            })
                                            print(f"[OpenAIClient] Added tool output for call {idx + 1}")
                                            
                                        except Exception as e:
                                            error_msg = f"Error in tool handler for '{function_name}': {str(e)}"
                                            print(f"[OpenAIClient] ERROR: {error_msg}")
                                            import traceback
                                            traceback.print_exc()
                                            
                                            # Return error output
                                            tool_outputs.append({
                                                "tool_call_id": tool_call_id,
                                                "output": json.dumps({
                                                    "error": error_msg,
                                                    "function": function_name,
                                                    "exception_type": type(e).__name__
                                                })
                                            })
                                else:
                                    print(f"[OpenAIClient] ERROR: No function object found in tool call")
                                    tool_outputs.append({
                                        "tool_call_id": tool_call_id,
                                        "output": json.dumps({"error": "No function object in tool call"})
                                    })
                            
                            # Submit tool outputs and continue
                            if tool_outputs:
                                print(f"[OpenAIClient] ========================================")
                                print(f"[OpenAIClient] Submitting {len(tool_outputs)} tool output(s)")
                                print(f"[OpenAIClient] ========================================")
                                for idx, output in enumerate(tool_outputs):
                                    print(f"[OpenAIClient] Tool output {idx + 1}:")
                                    print(f"[OpenAIClient]   - tool_call_id: {output.get('tool_call_id')}")
                                    print(f"[OpenAIClient]   - output: {output.get('output')[:200]}...")  # First 200 chars
                                
                                run = await self.client.beta.threads.runs.submit_tool_outputs(
                                    thread_id=thread_id,
                                    run_id=run.id,
                                    tool_outputs=tool_outputs
                                )
                                print(f"[OpenAIClient] Tool outputs submitted successfully")
                                print(f"[OpenAIClient] New run status: {run.status}")
                                # Continue polling
                                poll_count += 1
                                continue
                        else:
                            print(f"[OpenAIClient] WARNING: required_action exists but no submit_tool_outputs attribute")
                            print(f"[OpenAIClient] Required action attributes: {[attr for attr in dir(required_action) if not attr.startswith('_')] if required_action else 'None'}")
                    
                    # If completed or failed, break the loop
                    if run.status in ("completed", "failed", "cancelled", "expired"):
                        break
                    
                    poll_count += 1
                
                if poll_count >= max_polls:
                    print(f"[OpenAIClient] WARNING: Run polling timed out after {max_polls} seconds")
                    
            except Exception as e:
                # Handle specific OpenAI API errors
                error_msg = str(e)
                if "json" in error_msg.lower() and "response_format" in error_msg.lower():
                    raise RuntimeError(
                        "Your assistant is configured with 'json_object' response format. "
                        "This requires either:\n"
                        "1. The word 'json' to appear in your message, OR\n"
                        "2. The word 'json' to appear in your assistant's instructions.\n\n"
                        "To fix this permanently, update your assistant's instructions in OpenAI to include: "
                        "'Always respond in valid JSON format.'"
                    ) from e
                else:
                    raise
            
            print(f"[OpenAIClient] Run completed with status: {run.status}")
            
            # Log ALL run details for debugging
            print(f"[OpenAIClient] Full run object: {run}")
            print(f"[OpenAIClient] Run ID: {run.id}")
            print(f"[OpenAIClient] Run model: {getattr(run, 'model', 'N/A')}")
            print(f"[OpenAIClient] Run instructions: {getattr(run, 'instructions', 'N/A')}")
            
            # Log additional run details for debugging
            if hasattr(run, 'last_error') and run.last_error:
                print(f"[OpenAIClient] Run error details: {run.last_error}")
                error_code = getattr(run.last_error, 'code', None)
                error_type = getattr(run.last_error, 'type', None)
                error_message = getattr(run.last_error, 'message', None)
                if error_code:
                    print(f"[OpenAIClient] Error code: {error_code}")
                if error_type:
                    print(f"[OpenAIClient] Error type: {error_type}")
                if error_message:
                    print(f"[OpenAIClient] Error message: {error_message}")
            if hasattr(run, 'required_action') and run.required_action:
                print(f"[OpenAIClient] Run requires action: {run.required_action}")
                print(f"[OpenAIClient] Required action type: {getattr(run.required_action, 'type', 'unknown')}")
                if hasattr(run.required_action, 'submit_tool_outputs'):
                    tool_calls = getattr(run.required_action.submit_tool_outputs, 'tool_calls', [])
                    print(f"[OpenAIClient] Tool calls needed: {len(tool_calls)}")
                    for i, tc in enumerate(tool_calls):
                        print(f"[OpenAIClient] Tool call {i}: {tc}")
            
            if run.status == "completed":
                # Retrieve messages
                messages = await self.client.beta.threads.messages.list(
                    thread_id=thread_id,
                    order="asc"
                )
                
                # Find the latest assistant message
                assistant_messages = [
                    msg for msg in messages.data 
                    if msg.role == "assistant"
                ]
                
                if assistant_messages:
                    latest_message = assistant_messages[-1]
                    # Extract text content from the message
                    if latest_message.content:
                        text_content = ""
                        for content_block in latest_message.content:
                            # Check if it's a text content block (has 'text' attribute)
                            # Type ignore: We check for attribute existence at runtime
                            if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):  # type: ignore
                                text_content = content_block.text.value  # type: ignore
                                break
                        
                        if text_content:
                            # Return in standard format
                            return {
                                "messages": [
                                    {
                                        "type": "ai",
                                        "content": text_content
                                    }
                                ]
                            }
                
                # Fallback: return empty response
                return {"messages": [{"type": "ai", "content": "No response from assistant"}]}
            elif run.status == "failed":
                error_msg = "Run failed"
                error_code = None
                error_type = None
                
                if run.last_error:
                    error_msg = run.last_error.message or "Run failed: Sorry, something went wrong."
                    error_code = getattr(run.last_error, 'code', None)
                    error_type = getattr(run.last_error, 'type', None)
                    print(f"[OpenAIClient] Run failed - Type: {error_type}, Code: {error_code}, Message: {error_msg}")
                    print(f"[OpenAIClient] Full error object: {run.last_error}")
                else:
                    print(f"[OpenAIClient] Run failed but no error details available")
                    print(f"[OpenAIClient] Run object attributes: {[attr for attr in dir(run) if not attr.startswith('_')]}")
                
                # Check if there's a required_action that wasn't handled
                if hasattr(run, 'required_action') and run.required_action:
                    print(f"[OpenAIClient] WARNING: Run failed but has required_action: {run.required_action}")
                    print(f"[OpenAIClient] This suggests function calling may not have been handled properly")
                
                # Try to get more details from the run object
                run_details = {
                    "status": run.status,
                    "message": error_msg,
                    "suggestion": "Check your assistant's configuration in OpenAI dashboard. Common issues:\n"
                                "1. Function definitions may be incorrect\n"
                                "2. Assistant instructions may conflict with function calling\n"
                                "3. Response format (json_object) may require 'json' in instructions\n"
                                "4. The assistant may be trying to call functions that don't exist or are misconfigured"
                }
                if error_code:
                    run_details["code"] = error_code
                if error_type:
                    run_details["type"] = error_type
                
                return {"error": run_details}
            else:
                error_msg = f"Run ended with status: {run.status}"
                print(f"[OpenAIClient] {error_msg}")
                return {"error": {"message": error_msg}}
                
        except Exception as e:
            print(f"[OpenAIClient] ERROR sending message: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def upload_document(
        self,
        customer_id: int,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/pdf",
        thread_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Upload a document to OpenAI and return the file_id.
        
        Args:
            customer_id: The customer ID (not used by OpenAI, kept for compatibility)
            file_bytes: The file content as bytes
            filename: The filename
            content_type: The MIME type of the file
            thread_id: Optional thread ID (not used by OpenAI, kept for compatibility)
            
        Returns:
            file_id if upload successful, None otherwise
        """
        try:
            print(f"[OpenAIClient] Uploading file: {filename} ({len(file_bytes)} bytes)")
            
            # Upload file to OpenAI
            file = await self.client.files.create(
                file=(filename, file_bytes, content_type),
                purpose="assistants"
            )
            
            print(f"[OpenAIClient] File uploaded successfully, file_id: {file.id}")
            return file.id
            
        except Exception as e:
            print(f"[OpenAIClient] ERROR uploading file: {e}")
            import traceback
            traceback.print_exc()
            return None


# Create a singleton instance for the OpenAI client
openai_client: Optional[OpenAIAssistantClient] = None


def get_openai_client() -> OpenAIAssistantClient:
    """Get or create the OpenAI client instance"""
    global openai_client
    if openai_client is None:
        openai_client = OpenAIAssistantClient()
    return openai_client

