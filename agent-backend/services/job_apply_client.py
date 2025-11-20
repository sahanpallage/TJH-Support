# backend/services/job_apply_client.py
import sys
from pathlib import Path

# Ensure the agent-backend directory is in sys.path for absolute imports
# This allows 'from config import settings' to work
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import httpx
from typing import Any, Dict
from config import settings


class JobApplyClient:
    def __init__(self) -> None:
        self.base_url = (settings.JOB_APPLY_API_BASE or "").rstrip("/")
        self.api_key = settings.JOB_APPLY_API_KEY

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

    async def create_conversation(self, customer_id: int, title: str) -> Dict[str, Any]:
        """
        Call job-apply API to create a new chat session/thread.
        Adjust path and payload according to their docs.
        """
        async with httpx.AsyncClient(
            base_url=self._require_base_url(), headers=self._headers()
        ) as client:
            payload = {
                "customer_id": customer_id,
                "title": title,
            }
            # TODO: adjust /chat/sessions path and payload from swagger
            resp = await client.post("/chat/sessions", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def send_message(self, external_thread_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message into an existing chat session.
        """
        async with httpx.AsyncClient(
            base_url=self._require_base_url(), headers=self._headers()
        ) as client:
            payload = {
                "thread_id": external_thread_id,
                "message": message,
            }
            # TODO: adjust path / payload from swagger
            resp = await client.post("/chat/messages", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def upload_document(
        self,
        customer_id: int,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/pdf",
    ) -> Dict[str, Any]:
        """
        Upload resume/doc to job-apply API if supported.
        """
        async with httpx.AsyncClient(
            base_url=self._require_base_url(), headers=self._headers()
        ) as client:
            files = {
                "file": (filename, file_bytes, content_type),
            }
            data = {"customer_id": str(customer_id)}
            # TODO: adjust path from swagger, e.g. /documents/upload
            resp = await client.post("/documents/upload", data=data, files=files)
            resp.raise_for_status()
            return resp.json()


job_apply_client = JobApplyClient()
