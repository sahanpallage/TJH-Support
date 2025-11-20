# backend/services/job_apply_client.py
import sys
from pathlib import Path
import uuid

# Ensure the agent-backend directory is in sys.path for absolute imports
# This allows 'from config import settings' to work
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import httpx
from typing import Any, Dict, Optional
from config import settings


class JobApplyClient:
    def __init__(self) -> None:
        self.base_url = settings.JOB_APPLY_API_BASE
        self.api_key = settings.JOB_APPLY_API_KEY
        self.assistant_id = settings.JOB_APPLY_ASSISTANT_ID

    def _require_base_url(self) -> str:
        if not self.base_url:
            raise RuntimeError(
                "JOB_APPLY_API_BASE is not configured. "
                "Set it in your backend .env file before using the JobApplyClient."
            )
        return self.base_url

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def create_thread(self) -> Dict[str, Any]:
        """
        Create a new thread/conversation for the Donely agent.
        Uses the LangGraph API endpoint.
        """
        async with httpx.AsyncClient(headers=self._headers()) as client:
            # POST to the /threads endpoint to create a new thread
            resp = await client.post(
                f"{self._require_base_url()}/threads",
                json={},
            )
            resp.raise_for_status()
            return resp.json()

    async def send_message(self, thread_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message to the Donely agent in an existing thread.
        Uses the LangGraph streaming API.
        
        The agent expects input in the format:
        {
            "input": {
                "messages": [
                    {"role": "user", "content": "message text"}
                ]
            },
            "assistant_id": "your-assistant-id"
        }
        """
        if not self.assistant_id:
            raise RuntimeError(
                "JOB_APPLY_ASSISTANT_ID is not configured. "
                "Set it in your backend .env file before using the JobApplyClient."
            )
        
        async with httpx.AsyncClient(headers=self._headers(), timeout=30.0) as client:
            # Standard LangGraph format with messages and assistant_id
            payload = {
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": message,
                        }
                    ]
                },
                "assistant_id": self.assistant_id
            }
            
            url = f"{self._require_base_url()}/threads/{thread_id}/runs/wait"
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def create_conversation(self, customer_id: int, title: str) -> Dict[str, Any]:
        """
        Create a new conversation session by creating a thread.
        """
        return await self.create_thread()

    async def upload_document(
        self,
        customer_id: int,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/pdf",
    ) -> Dict[str, Any]:
        """
        Upload a document to the Donely agent.
        Note: Implementation depends on the agent's document handling.
        """
        async with httpx.AsyncClient(headers=self._headers()) as client:
            files = {
                "file": (filename, file_bytes, content_type),
            }
            data = {"customer_id": str(customer_id)}
            resp = await client.post(
                f"{self._require_base_url()}/documents/upload",
                data=data,
                files=files,
            )
            resp.raise_for_status()
            return resp.json()


job_apply_client = JobApplyClient()
