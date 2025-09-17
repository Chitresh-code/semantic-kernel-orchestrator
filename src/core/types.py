from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    id: str = Field(..., description="Unique identifier for the task")
    title: str = Field(..., description="Brief title of the task")
    description: str = Field(..., description="Detailed description of what needs to be done")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task")
    agent_type: str = Field(..., description="Type of agent best suited for this task")
    required_tools: List[str] = Field(default_factory=list, description="Tools required to complete this task")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must be completed first")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task-specific metadata")


class Plan(BaseModel):
    id: str = Field(..., description="Unique identifier for the plan")
    user_query: str = Field(..., description="Original user query that generated this plan")
    tasks: List[Task] = Field(..., description="List of tasks to be executed")
    estimated_total_duration: Optional[int] = Field(None, description="Total estimated duration in minutes")
    created_at: str = Field(..., description="Timestamp when the plan was created")

    def get_ready_tasks(self) -> List[Task]:
        """Return tasks that are ready to be executed (no pending dependencies)."""
        completed_task_ids = {task.id for task in self.tasks if task.status == TaskStatus.COMPLETED}

        ready_tasks = []
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                if all(dep_id in completed_task_ids for dep_id in task.dependencies):
                    ready_tasks.append(task)

        return ready_tasks


class AgentResponse(BaseModel):
    agent_name: str = Field(..., description="Name of the agent that generated this response")
    task_id: str = Field(..., description="ID of the task this response addresses")
    content: str = Field(..., description="The actual response content")
    success: bool = Field(..., description="Whether the task was completed successfully")
    tools_used: List[str] = Field(default_factory=list, description="Tools that were used in this response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")


class WorkflowResult(BaseModel):
    plan_id: str = Field(..., description="ID of the plan that was executed")
    user_query: str = Field(..., description="Original user query")
    agent_responses: List[AgentResponse] = Field(..., description="All agent responses in order")
    final_response: str = Field(..., description="Consolidated final response to the user")
    total_execution_time: float = Field(..., description="Total time taken to execute the workflow in seconds")
    success: bool = Field(..., description="Whether the overall workflow was successful")
    errors: List[str] = Field(default_factory=list, description="Any errors that occurred during execution")