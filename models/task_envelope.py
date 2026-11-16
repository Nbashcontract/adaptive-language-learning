import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List


@dataclass
class TaskLease:
    agent_id: str
    token: str
    expires_at: datetime


@dataclass
class TaskEnvelope:
    task_id: str
    repo_url: str
    target_languages: List[str]
    status: str  # "CREATED", "LEASED", "CHECKPOINTED", "DONE", "FAILED"
    producer_agent_id: str
    consumer_agent_id: Optional[str] = None
    lease: Optional[TaskLease] = None
    temp_storage_path: Optional[str] = None  # Ссылка на артефакты во временном хранилище
    checkpoint_data: Optional[Dict[str, Any]] = None
    raw_metrics_ref: Optional[str] = None  # Ссылка на RawMetrics от другого агента
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @classmethod
    def create(cls, repo_url: str, target_languages: List[str], producer_agent_id: str) -> "TaskEnvelope":
        return cls(
            task_id=str(uuid.uuid4()),
            repo_url=repo_url,
            target_languages=target_languages,
            status="CREATED",
            producer_agent_id=producer_agent_id,
        )


class HandoffManager:
    def __init__(self, temp_storage_path: str):
        self.temp_storage_path = temp_storage_path
        self.active_tasks: Dict[str, TaskEnvelope] = {}

    def create_task(self, repo_url: str, target_languages: List[str], producer_agent_id: str) -> TaskEnvelope:
        task = TaskEnvelope.create(repo_url, target_languages, producer_agent_id)
        self.active_tasks[task.task_id] = task
        return task

    def acquire_lease(self, task_id: str, agent_id: str, ttl_seconds: int = 60) -> TaskLease:
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.lease and task.lease.expires_at > datetime.now():
            if task.lease.agent_id != agent_id:
                raise PermissionError(f"Task {task_id} already leased by agent {task.lease.agent_id}")

        task.lease = TaskLease(
            agent_id=agent_id,
            token=str(uuid.uuid4()),
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds),
        )
        task.status = "LEASED"
        task.attempts += 1
        task.consumer_agent_id = agent_id
        return task.lease

    def save_checkpoint(self, task_id: str, agent_id: str, token: str, data: Dict[str, Any]) -> str:
        """Агент сохраняет промежуточный результат во временное хранилище"""
        task = self.active_tasks.get(task_id)
        if not task or task.lease.agent_id != agent_id or task.lease.token != token:
            raise PermissionError("Invalid lease or token")

        checkpoint_path = f"{self.temp_storage_path}/{task_id}/checkpoint.json"
        task.checkpoint_data = data
        task.temp_storage_path = checkpoint_path
        task.status = "CHECKPOINTED"
        # В реальности: записать data в файл по checkpoint_path
        return checkpoint_path

    def share_raw_metrics(self, task_id: str, agent_id: str, token: str, metrics_ref: str):
        """Агент делится сырыми метриками с другими агентами (обмен данными)"""
        task = self.active_tasks.get(task_id)
        if not task or task.lease.agent_id != agent_id or task.lease.token != token:
            raise PermissionError("Invalid lease or token")
        task.raw_metrics_ref = metrics_ref

    def complete_task(self, task_id: str, agent_id: str, token: str, result: Dict[str, Any]) -> TaskEnvelope:
        """Агент завершает задачу"""
        task = self.active_tasks.get(task_id)
        if not task or task.lease.agent_id != agent_id:
            raise PermissionError("Invalid lease")

        task.status = "DONE"
        task.lease = None  # Освобождаем аренду
        task.checkpoint_data = {"final_result": result}
        task.completed_at = datetime.now()
        return task

    def get_task(self, task_id: str) -> TaskEnvelope:
        """Получить задачу по ID"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.active_tasks[task_id]

    def get_raw_metrics_ref(self, task_id: str) -> Optional[str]:
        """Другой агент может получить ссылку на RawMetrics для обмена данными"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        return task.raw_metrics_ref