# backend/services/tool_handlers.py
"""
Tool handlers for OpenAI Assistant function calls.
Each function in the assistant must have a corresponding handler here.
"""
import json
import logging
from typing import Dict, Any, Optional, Callable

# Set up logging
logger = logging.getLogger(__name__)

# Handler registry - maps function names to handler functions
TOOL_HANDLERS: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register_handler(function_name: str):
    """Decorator to register a function as a tool handler."""
    def decorator(func):
        TOOL_HANDLERS[function_name] = func
        logger.info(f"[ToolHandlers] Registered handler for function: {function_name}")
        return func
    return decorator


async def handle_tool_call(function_name: str, function_args: Dict[str, Any]) -> str:
    """
    Main entry point for handling tool calls from OpenAI Assistant.
    
    Args:
        function_name: The name of the function being called (must match exactly)
        function_args: The parsed arguments dictionary
        
    Returns:
        JSON string with the result or error
    """
    logger.info(f"[ToolHandlers] ========================================")
    logger.info(f"[ToolHandlers] HANDLING TOOL CALL")
    logger.info(f"[ToolHandlers] ========================================")
    logger.info(f"[ToolHandlers] Function name: '{function_name}'")
    logger.info(f"[ToolHandlers] Function args type: {type(function_args)}")
    logger.info(f"[ToolHandlers] Function args: {json.dumps(function_args, indent=2)}")
    
    # Check if handler exists
    if function_name not in TOOL_HANDLERS:
        error_msg = f"No handler registered for function '{function_name}'. Available handlers: {list(TOOL_HANDLERS.keys())}"
        logger.error(f"[ToolHandlers] {error_msg}")
        return json.dumps({
            "error": error_msg,
            "function": function_name,
            "available_handlers": list(TOOL_HANDLERS.keys())
        })
    
    # Get the handler
    handler = TOOL_HANDLERS[function_name]
    logger.info(f"[ToolHandlers] Found handler: {handler.__name__}")
    
    try:
        # Call the handler
        logger.info(f"[ToolHandlers] Calling handler with args: {function_args}")
        result = await handler(function_args)
        logger.info(f"[ToolHandlers] Handler returned result type: {type(result)}")
        logger.info(f"[ToolHandlers] Handler returned result: {result}")
        
        # Ensure result is a JSON string
        if isinstance(result, str):
            # Try to parse to validate it's valid JSON
            try:
                json.loads(result)
                logger.info(f"[ToolHandlers] Result is valid JSON string")
                return result
            except json.JSONDecodeError:
                # If it's not JSON, wrap it
                logger.warning(f"[ToolHandlers] Result is not valid JSON, wrapping it")
                return json.dumps({"result": result})
        else:
            # Convert to JSON string
            logger.info(f"[ToolHandlers] Converting result to JSON string")
            return json.dumps(result)
            
    except Exception as e:
        error_msg = f"Error executing handler for '{function_name}': {str(e)}"
        logger.error(f"[ToolHandlers] {error_msg}", exc_info=True)
        return json.dumps({
            "error": error_msg,
            "function": function_name,
            "exception_type": type(e).__name__
        })


@register_handler("search_recent_jobs")
async def search_recent_jobs_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the 'search_recent_jobs' function.
    
    Expected args (from assistant function definition):
    - titles: List[str] - Target job titles or keywords
    - locations: Optional[List[str]] - Preferred locations
    - date_posted_from: Optional[str] - ISO date (YYYY-MM-DD) for filtering
    - max_results: Optional[int] - Maximum number of jobs (default: 50)
    - seniority: Optional[str] - Seniority filter
    - min_salary: Optional[float] - Minimum yearly salary
    - max_salary: Optional[float] - Maximum yearly salary
    - work_type: Optional[str] - Work arrangement (remote, hybrid, onsite, any)
    - industries: Optional[List[str]] - Target industries
    
    Returns:
        Dict with job search results
    """
    logger.info(f"[ToolHandlers] ========================================")
    logger.info(f"[ToolHandlers] search_recent_jobs_handler CALLED")
    logger.info(f"[ToolHandlers] ========================================")
    logger.info(f"[ToolHandlers] Raw args received: {args}")
    logger.info(f"[ToolHandlers] Args type: {type(args)}")
    
    # Parse arguments
    titles = args.get("titles", [])
    locations = args.get("locations", [])
    date_posted_from = args.get("date_posted_from")
    max_results = args.get("max_results", 50)
    seniority = args.get("seniority")
    min_salary = args.get("min_salary")
    max_salary = args.get("max_salary")
    work_type = args.get("work_type", "any")
    industries = args.get("industries", [])
    
    logger.info(f"[ToolHandlers] Parsed arguments:")
    logger.info(f"[ToolHandlers]   - titles: {titles}")
    logger.info(f"[ToolHandlers]   - locations: {locations}")
    logger.info(f"[ToolHandlers]   - date_posted_from: {date_posted_from}")
    logger.info(f"[ToolHandlers]   - max_results: {max_results}")
    logger.info(f"[ToolHandlers]   - seniority: {seniority}")
    logger.info(f"[ToolHandlers]   - min_salary: {min_salary}")
    logger.info(f"[ToolHandlers]   - max_salary: {max_salary}")
    logger.info(f"[ToolHandlers]   - work_type: {work_type}")
    logger.info(f"[ToolHandlers]   - industries: {industries}")
    
    # Validate required arguments
    if not titles:
        error_msg = "Missing required argument: 'titles'"
        logger.error(f"[ToolHandlers] {error_msg}")
        return {"error": error_msg, "function": "search_recent_jobs"}
    
    # TODO: Integrate with actual job search API/service
    # For now, return a placeholder response
    logger.warning(f"[ToolHandlers] WARNING: Using placeholder response - job search API not integrated")
    
    # Return placeholder results
    placeholder_jobs = [
        {
            "Job_Title": f"Placeholder Job for {titles[0] if titles else 'Unknown'}",
            "Company": "Example Company",
            "Location": locations[0] if locations else "Remote",
            "Salary_Range": f"${min_salary or 50000}-${max_salary or 150000}" if min_salary or max_salary else "Not specified",
            "Work_Type": work_type,
            "Job_URL": "https://example.com/job/1",
            "Description_Summary": "This is a placeholder job result. Integrate with your job search API.",
            "Match_Score": 85,
            "Priority": "High",
            "Percentage": 85
        }
    ]
    
    result = {
        "jobs": placeholder_jobs,
        "total_results": len(placeholder_jobs),
        "filters_applied": {
            "titles": titles,
            "locations": locations,
            "date_posted_from": date_posted_from,
            "work_type": work_type,
            "industries": industries
        },
        "note": "This is a placeholder response. Please integrate with your actual job search service."
    }
    
    logger.info(f"[ToolHandlers] Returning result: {result}")
    logger.info(f"[ToolHandlers] ========================================")
    logger.info(f"[ToolHandlers] search_recent_jobs_handler COMPLETE")
    logger.info(f"[ToolHandlers] ========================================")
    
    return result

