import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List

@dataclass
class TaskLease:
    agent_id: str; token: str; expires_at: datetime

@dataclass
class TaskEnvelope:
    task_id: str; repo_url: str; target_languages: List[str]; status: str
    producer_agent_id: str; consumer_agent_id: Optional[str] = None
    lease: Optional[TaskLease] = None; temp_storage_path: Optional[str] = None
    checkpoint_data: Optional[Dict] = None; raw_metrics_ref: Optional[str] = None
    attempts: int = 0; created_at: datetime = field(default_factory=datetime.now)

class HandoffManager:
    def __init__(self, temp_path): self.temp_path = temp_path; self.active_tasks = {}
    def create_task(self, repo_url, langs, producer):
        t = TaskEnvelope(task_id=str(uuid.uuid4()), repo_url=repo_url, target_languages=langs, status="CREATED", producer_agent_id=producer)
        self.active_tasks[t.task_id] = t; return t
    def acquire_lease(self, task_id, agent_id):
        t = self.active_tasks[task_id]
        t.lease = TaskLease(agent_id=agent_id, token=str(uuid.uuid4()), expires_at=datetime.now() + timedelta(seconds=60))
        t.status = "LEASED"; t.consumer_agent_id = agent_id; t.attempts += 1; return t.lease
    def share_raw_metrics(self, task_id, agent_id, token, ref):
        t = self.active_tasks.get(task_id)
        if t and t.lease and t.lease.token == token: t.raw_metrics_ref = ref
    def complete_task(self, task_id, agent_id, result):
        t = self.active_tasks.get(task_id); t.status = "DONE"; t.checkpoint_data = {"result": result}; return t
