"""
Debug script to find the Donely assistant ID from the API
"""
import httpx
import asyncio


async def get_assistants():
    """Fetch available assistants from Donely API"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Try to get assistants list
            resp = await client.get("https://job-apply-api.donely.ai/assistants")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            return resp.json()
        except Exception as e:
            print(f"Error: {e}")
            return None


async def get_graphs():
    """Fetch available graphs from Donely API"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get("https://job-apply-api.donely.ai/graphs")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            return resp.json()
        except Exception as e:
            print(f"Error: {e}")
            return None


if __name__ == "__main__":
    print("=== Trying to fetch assistants ===")
    asyncio.run(get_assistants())
    
    print("\n=== Trying to fetch graphs ===")
    asyncio.run(get_graphs())
