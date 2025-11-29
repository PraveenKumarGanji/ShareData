# app/adapters/servicenow_adapter.py
import uuid
from typing import Dict, Any

class ServiceNowAdapterMock:
    def create_incident(self, short_description: str, caller_id: str, comments: str = "") -> Dict[str, Any]:
        ticket = {
            "number": f"INC{uuid.uuid4().hex[:6].upper()}",
            "sys_id": uuid.uuid4().hex,
            "short_description": short_description,
            "caller_id": caller_id,
            "comments": comments
        }
        return ticket

servicenow = ServiceNowAdapterMock()
