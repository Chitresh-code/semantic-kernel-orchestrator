import json
import uuid
from datetime import datetime
from typing import Dict, Any

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.prompt_execution_settings.ollama_prompt_execution_settings import OllamaChatPromptExecutionSettings

from src.core.config import config
from src.core.types import Plan, Task, TaskStatus
from src.planner.schemas import PlannerResponse, TaskCreateRequest


class PlannerAgent:
    """Agent responsible for breaking down user queries into structured task plans."""

    def __init__(self):
        self.config = config.get_planner_config()
        self.ollama_config = config.get_ollama_config()

        # Create Ollama chat completion service
        self.chat_service = OllamaChatCompletion(
            ai_model_id=self.ollama_config.ai_model_id,
            service_id=self.ollama_config.service_id,
            url=self.ollama_config.host
        )

        # Create the planner agent
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            name=self.config.name,
            description=self.config.description,
            instructions=self._get_enhanced_instructions()
        )

    def _get_enhanced_instructions(self) -> str:
        """Get enhanced instructions with structured output requirements."""
        return f"""{self.config.instructions}

IMPORTANT: You must respond with valid JSON that matches this exact schema:

{{
    "tasks": [
        {{
            "title": "Brief task title (max 100 chars)",
            "description": "Detailed description of what needs to be done (max 500 chars)",
            "priority": "low|medium|high|urgent",
            "agent_type": "sales_assistant",
            "required_tools": ["tool1", "tool2"],
            "estimated_duration": 30,
            "dependencies": ["task-id-1", "task-id-2"]
        }}
    ],
    "summary": "Brief summary of the plan (max 200 chars)",
    "estimated_total_duration": 60
}}

Available agent types:
- sales_assistant: For CRM operations, customer interactions, proposals, scheduling

Available tools:
- crm_api: Access customer data, update records
- email_calendar: Send emails, schedule meetings
- product_catalog: Access product information, pricing
- document_generator: Create proposals, contracts, reports

Task dependency format: Use kebab-case IDs (e.g., "pull-customer-data", "generate-proposal")

Always ensure your response is valid JSON and follows the schema exactly."""

    async def create_plan(self, user_query: str) -> Plan:
        """Create a structured plan from a user query."""
        try:
            # Create chat history with the user query
            chat_history = ChatHistory()
            chat_history.add_user_message(user_query)

            # Set up execution settings
            execution_settings = OllamaChatPromptExecutionSettings(
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            # Get response from the agent
            response = await self.chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=execution_settings
            )

            if not response or not response[0].content:
                raise ValueError("No response received from planner agent")

            # Parse the JSON response
            response_text = response[0].content.strip()

            # Try to extract JSON if it's wrapped in code blocks
            if "```json" in response_text:
                start_idx = response_text.find("```json") + 7
                end_idx = response_text.find("```", start_idx)
                response_text = response_text[start_idx:end_idx].strip()
            elif "```" in response_text:
                start_idx = response_text.find("```") + 3
                end_idx = response_text.find("```", start_idx)
                response_text = response_text[start_idx:end_idx].strip()

            # Parse the planner response
            planner_data = json.loads(response_text)
            planner_response = PlannerResponse(**planner_data)

            # Convert to our internal Plan format
            plan = self._convert_to_plan(user_query, planner_response)

            return plan

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse planner response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error creating plan: {e}")

    def _convert_to_plan(self, user_query: str, planner_response: PlannerResponse) -> Plan:
        """Convert PlannerResponse to internal Plan format."""
        plan_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()

        # Create tasks with proper IDs
        tasks = []
        for task_req in planner_response.tasks:
            task_id = self._generate_task_id(task_req.title)

            task = Task(
                id=task_id,
                title=task_req.title,
                description=task_req.description,
                priority=task_req.priority,
                status=TaskStatus.PENDING,
                agent_type=task_req.agent_type,
                required_tools=task_req.required_tools,
                estimated_duration=task_req.estimated_duration,
                dependencies=task_req.dependencies,
                metadata={"created_by": "planner_agent"}
            )
            tasks.append(task)

        return Plan(
            id=plan_id,
            user_query=user_query,
            tasks=tasks,
            estimated_total_duration=planner_response.estimated_total_duration,
            created_at=current_time
        )

    def _generate_task_id(self, title: str) -> str:
        """Generate a kebab-case task ID from the title."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        task_id = title.lower()
        task_id = ''.join(c if c.isalnum() else '-' for c in task_id)
        # Remove consecutive hyphens and strip leading/trailing hyphens
        task_id = '-'.join(filter(None, task_id.split('-')))
        return task_id

    async def validate_plan(self, plan: Plan) -> Dict[str, Any]:
        """Validate a plan for consistency and feasibility."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check for circular dependencies
        if self._has_circular_dependencies(plan.tasks):
            validation_result["valid"] = False
            validation_result["errors"].append("Circular dependencies detected in task plan")

        # Check if all dependency IDs exist
        task_ids = {task.id for task in plan.tasks}
        for task in plan.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Task '{task.title}' depends on non-existent task ID: {dep_id}")

        # Check for unrealistic duration estimates
        total_duration = sum(task.estimated_duration or 0 for task in plan.tasks)
        if total_duration > 480:  # More than 8 hours
            validation_result["warnings"].append("Plan duration exceeds 8 hours - consider breaking into smaller chunks")

        return validation_result

    def _has_circular_dependencies(self, tasks: list[Task]) -> bool:
        """Check if there are circular dependencies in the task list."""
        # Create adjacency list
        graph = {task.id: task.dependencies for task in tasks}

        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True

            rec_stack.remove(node)
            return False

        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True

        return False