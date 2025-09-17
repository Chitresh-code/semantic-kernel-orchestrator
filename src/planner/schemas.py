from typing import List
from pydantic import BaseModel, Field
from src.core.types import Task, TaskPriority


class TaskCreateRequest(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., description="Brief title of the task", max_length=100)
    description: str = Field(..., description="Detailed description of what needs to be done", max_length=500)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    agent_type: str = Field(..., description="Type of agent best suited for this task (e.g., 'sales_assistant')")
    required_tools: List[str] = Field(default_factory=list, description="Tools required to complete this task")
    estimated_duration: int = Field(default=30, description="Estimated duration in minutes", ge=1, le=480)
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must be completed first")


class PlannerResponse(BaseModel):
    """Structured response from the planner agent."""
    tasks: List[TaskCreateRequest] = Field(..., description="List of tasks to be executed")
    summary: str = Field(..., description="Brief summary of the plan", max_length=200)
    estimated_total_duration: int = Field(..., description="Total estimated duration in minutes", ge=1)

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "title": "Pull customer CRM data",
                        "description": "Retrieve comprehensive customer information from CRM system including contact details, purchase history, and interaction logs",
                        "priority": "high",
                        "agent_type": "sales_assistant",
                        "required_tools": ["crm_api"],
                        "estimated_duration": 15,
                        "dependencies": []
                    },
                    {
                        "title": "Generate sales proposal",
                        "description": "Create a customized sales proposal based on customer data and product recommendations",
                        "priority": "medium",
                        "agent_type": "sales_assistant",
                        "required_tools": ["document_generator", "product_catalog"],
                        "estimated_duration": 45,
                        "dependencies": ["pull-customer-crm-data"]
                    }
                ],
                "summary": "Retrieve customer data and generate a personalized sales proposal",
                "estimated_total_duration": 60
            }
        }