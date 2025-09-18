import json
import uuid
from datetime import datetime
from typing import Dict, Any

from semantic_kernel.agents import ChatCompletionAgent
# from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
# from semantic_kernel.connectors.ai.ollama import OllamaChatPromptExecutionSettings
# from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion, GoogleAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory

from src.core.config import config
from src.core.types import Plan, Task, TaskStatus
from src.planner.schemas import PlannerResponse, TaskCreateRequest


class PlannerAgent:
    """Agent responsible for breaking down user queries into structured task plans."""

    def __init__(self):
        self.config = config.get_planner_config()
        # self.ollama_config = config.get_ollama_config()
        # self.gemini_config = config.get_gemini_config()
        self.openai_config = config.get_openai_config()

        # Create Gemini chat completion service (commented out)
        # self.chat_service = GoogleAIChatCompletion(
        #     gemini_model_id=self.gemini_config["ai_model_id"],
        #     api_key=self.gemini_config["api_key"]
        # )

        # Create OpenAI chat completion service
        self.chat_service = OpenAIChatCompletion(
            ai_model_id=self.openai_config["ai_model_id"],
            api_key=self.openai_config["api_key"]
        )

        # # Create Ollama chat completion service (commented out)
        # self.chat_service = OllamaChatCompletion(
        #     ai_model_id=self.ollama_config.ai_model_id
        # )

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

CRITICAL REQUIREMENT: You MUST respond with EXACTLY this JSON structure - do not modify the field names or structure:

{{
    "tasks": [list of task objects],
    "summary": "string describing the overall plan",
    "estimated_total_duration": integer_in_minutes
}}

Each task must have EXACTLY these fields:
{{
    "title": "Brief descriptive title",
    "description": "What needs to be done",
    "priority": "low" or "medium" or "high" or "urgent",
    "agent_type": "sales_assistant",
    "required_tools": ["crm_api", "email_calendar", "product_catalog", "document_generator"],
    "estimated_duration": integer_in_minutes,
    "dependencies": []
}}

Valid tools: crm_api, email_calendar, product_catalog, document_generator
Valid priorities: low, medium, high, urgent
Only agent_type: sales_assistant

MANDATORY EXAMPLE FOR CUSTOMER DATA REQUEST:
{{
    "tasks": [
        {{
            "title": "Retrieve customer data",
            "description": "Pull complete customer information from CRM system",
            "priority": "high",
            "agent_type": "sales_assistant",
            "required_tools": ["crm_api"],
            "estimated_duration": 10,
            "dependencies": []
        }},
        {{
            "title": "Send follow-up email",
            "description": "Create and send personalized follow-up email to customer",
            "priority": "medium",
            "agent_type": "sales_assistant",
            "required_tools": ["email_calendar"],
            "estimated_duration": 15,
            "dependencies": []
        }}
    ],
    "summary": "Retrieve customer data and send follow-up communication",
    "estimated_total_duration": 25
}}

RESPOND WITH JSON ONLY - NO OTHER TEXT."""

    async def create_plan(self, user_query: str) -> Plan:
        """Create a structured plan from a user query."""
        try:
            # Create chat history with system message and user query
            chat_history = ChatHistory()
            chat_history.add_system_message("""You are a task planner. You MUST respond with valid JSON in this EXACT format:
{
    "tasks": [
        {
            "title": "Task title",
            "description": "What to do",
            "priority": "high",
            "agent_type": "sales_assistant",
            "required_tools": ["crm_api"],
            "estimated_duration": 15,
            "dependencies": []
        }
    ],
    "summary": "Plan summary",
    "estimated_total_duration": 15
}

Use only these tools: crm_api, email_calendar, product_catalog, document_generator
Only use agent_type: sales_assistant
Valid priorities: low, medium, high, urgent
IMPORTANT: For dependencies, use kebab-case IDs like "get-customer-information", not full titles.

CRITICAL: Break down complex requests into multiple specific tasks. For example:
- "Pull data AND analyze" = two separate tasks (pull data, then analyze data)
- "Create AND send" = two separate tasks (create document, then send document)
- "Research AND propose" = two separate tasks (research, then create proposal)""")
            chat_history.add_user_message(f"{user_query}\n\nRespond with JSON only.")

            # Set up execution settings for Gemini (commented out)
            # execution_settings = GoogleAIChatPromptExecutionSettings(
            #     max_tokens=self.config.max_tokens,
            #     temperature=self.config.temperature
            # )

            # Set up execution settings for OpenAI with JSON mode
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                response_format={"type": "json_object"}
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

        # Create tasks with proper IDs and resolve dependencies
        tasks = []
        task_title_to_id = {}  # Map from task title to generated task ID

        # First pass: create mapping from titles to IDs
        for task_req in planner_response.tasks:
            task_id = self._generate_task_id(task_req.title)
            task_title_to_id[task_req.title] = task_id

        # Second pass: create tasks with resolved dependencies
        for task_req in planner_response.tasks:
            task_id = self._generate_task_id(task_req.title)

            # Resolve dependencies by finding matching task IDs
            resolved_deps = []
            for dep in task_req.dependencies:
                # Find the task that matches this dependency
                found_dep = None
                for title, tid in task_title_to_id.items():
                    # Check if dependency matches task ID or if we can generate matching ID
                    generated_dep_id = self._generate_task_id(title)
                    if dep == generated_dep_id or dep == tid:
                        found_dep = tid
                        break

                if found_dep:
                    resolved_deps.append(found_dep)
                else:
                    # If no match found, keep the original dependency
                    resolved_deps.append(dep)

            task = Task(
                id=task_id,
                title=task_req.title,
                description=task_req.description,
                priority=task_req.priority,
                status=TaskStatus.PENDING,
                agent_type=task_req.agent_type,
                required_tools=task_req.required_tools,
                estimated_duration=task_req.estimated_duration,
                dependencies=resolved_deps,
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

        # Check if all dependency IDs exist (with flexible matching)
        task_ids = {task.id for task in plan.tasks}
        task_id_to_title = {task.id: task.title for task in plan.tasks}

        for task in plan.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    print(f"DEBUG: Dependency '{dep_id}' not found in task IDs: {list(task_ids)}")
                    # Try to find a close match by checking if dependency is a substring or similar
                    found_match = False
                    for existing_id in task_ids:
                        # Handle various apostrophe and normalization issues
                        # Normalize both IDs for comparison
                        def normalize_id(id_str):
                            # Handle corporation's -> corporation-s and other apostrophe issues
                            normalized = id_str.lower()
                            # Remove apostrophes and replace with nothing or hyphen
                            normalized = normalized.replace("'s", "s").replace("'", "")
                            # Handle corporation's -> corporations vs corporation-s
                            normalized = normalized.replace("-s-", "-").replace("corporations", "corporation")
                            # Normalize common variations
                            normalized = normalized.replace("--", "-")
                            # Remove extra hyphens and clean up
                            normalized = '-'.join(filter(None, normalized.split('-')))
                            return normalized

                        normalized_dep = normalize_id(dep_id)
                        normalized_existing = normalize_id(existing_id)

                        # Check multiple matching strategies
                        if (normalized_dep == normalized_existing or
                            normalized_dep in normalized_existing or
                            normalized_existing in normalized_dep or
                            dep_id in existing_id or existing_id in dep_id):
                            print(f"DEBUG: Found match for '{dep_id}' -> '{existing_id}' (normalized: '{normalized_dep}' vs '{normalized_existing}')")
                            found_match = True
                            # Fix the dependency in place
                            task.dependencies = [existing_id if d == dep_id else d for d in task.dependencies]
                            break

                    if not found_match:
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