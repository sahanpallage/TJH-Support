# Assistant Troubleshooting Guide

## Issue: Run Status "Failed" with `server_error`

**Current Error**: `server_error` with message "Sorry, something went wrong."

This is a generic error from OpenAI's servers that typically indicates a problem with the assistant configuration itself, not with the code.

## Most Likely Causes

### 1. **Invalid Function Definition** (MOST COMMON)

Your assistant has a function tool defined (likely `search_recent_jobs` or similar), but:

- The function schema is invalid JSON
- Required parameters are missing
- Parameter types don't match the schema
- The function name conflicts with reserved names

**Solution**:

1. Go to https://platform.openai.com/assistants
2. Open your assistant
3. Check the "Functions" section
4. Verify each function has:
   - Valid JSON schema
   - All required fields
   - Correct parameter types
5. **Temporarily remove all functions** to test if the assistant works without them

### 2. **Response Format Conflict**

If using `json_object` response format:

- The word "json" must be in instructions OR in the message
- Instructions may conflict with function calling

**Solution**:

- Add "Always respond in valid JSON format." to instructions
- OR change response format to `auto`

### 3. **Model Compatibility**

The model may not support the features you're using.

**Solution**:

- Check if your model (gpt-4.1-mini) supports function calling
- Try switching to a different model temporarily

Based on the OpenAI migration documentation and code analysis, here are the potential causes and solutions:

## Key Findings

1. **Migration Status**: The Assistants API is still functional but deprecated (will shut down August 26, 2026). The Responses API is the new approach, but Assistants API should still work.

2. **Function Calling**: The assistant likely has a function `search_recent_jobs` defined. When the assistant tries to call this function:

   - The run status changes to `requires_action`
   - We need to handle this by submitting tool outputs
   - If not handled properly, the run may fail

3. **Response Format**: If the assistant is configured with `json_object` response format:
   - The word "json" must appear in either the user message OR the assistant's instructions
   - We've added automatic handling for this, but it may need to be in the assistant's instructions

## Code Changes Made

1. **Manual Polling**: Changed from `create_and_poll()` to manual polling to properly handle `requires_action` status
2. **Function Call Handling**: Added proper handling for function calls with placeholder outputs
3. **Enhanced Logging**: Added detailed logging to diagnose issues

## What to Check in OpenAI Dashboard

1. **Assistant Configuration**:

   - Go to https://platform.openai.com/assistants
   - Open your assistant (ID: `asst_OLMs1Ux3tI60PidqhnlmXHgl`)
   - Check the following:

2. **Instructions**:

   - Ensure instructions include: "Always respond in valid JSON format." (if using json_object response format)
   - Verify instructions don't conflict with function calling

3. **Function Definitions**:

   - Check if `search_recent_jobs` function is defined
   - Verify the function schema is correct
   - Ensure function parameters match what the assistant expects

4. **Response Format**:

   - If using `json_object`, ensure instructions mention JSON
   - Consider switching to `auto` if JSON isn't strictly required

5. **Model**:
   - Verify the model supports function calling
   - Check if the model version is correct

## Common Issues

### Issue 1: Function Calling Not Implemented

**Symptom**: Run fails when assistant tries to call a function
**Solution**:

- Either remove the function from the assistant configuration
- Or implement the function handler in the backend
- Currently, we submit placeholder outputs which may cause the assistant to fail

### Issue 2: JSON Format Requirement

**Symptom**: Error about "json" not found in message
**Solution**:

- Add "Always respond in valid JSON format." to assistant instructions
- Or include "json" in every user message

### Issue 3: Assistant Configuration Error

**Symptom**: Generic "Sorry, something went wrong" error
**Solution**:

- Check assistant configuration in dashboard
- Verify all function definitions are valid JSON schemas
- Ensure model supports the features you're using

## Next Steps

1. **Check the logs**: The enhanced logging will show:

   - Exact error message from OpenAI
   - Function calls that were attempted
   - Run status at each step

2. **Test without functions**: Temporarily remove all functions from the assistant to see if it works

3. **Test with simple message**: Send a simple "Hello" message to see if basic functionality works

4. **Review assistant settings**: Go through all settings in the OpenAI dashboard

## Testing

After making changes, test with:

```bash
# Send a simple message
curl -X POST http://localhost:8000/chat/conversations/{conversation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

Check the server logs for detailed error information.
