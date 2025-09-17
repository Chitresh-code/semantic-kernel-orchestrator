import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from semantic_kernel.agents import (
    Agent,
    ChatCompletionAgent,
    MagenticOrchestration,
    StandardMagenticManager,
)
from semantic_kernel.agents.orchestration.tools import structured_outputs_transform
from semantic_kernel.agents.runtime import InProcessRuntime
# from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
# from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatMessageContent

from src.core.config import config
from src.core.types import Plan, Task, AgentResponse, WorkflowResult, TaskStatus
from src.agents import SalesAssistantAgent


class MagenticCoordinator:
    """Coordinates task execution using Magentic orchestration with Ollama-based agents."""

    def __init__(self):
        # self.ollama_config = config.get_ollama_config()
        # self.gemini_config = config.get_gemini_config()
        self.openai_config = config.get_openai_config()
        self.runtime: Optional[InProcessRuntime] = None
        self.orchestration: Optional[MagenticOrchestration] = None
        self.agent_responses: List[AgentResponse] = []

        # Initialize specialized agents
        self.sales_assistant = SalesAssistantAgent()

    async def initialize(self):
        """Initialize the Magentic orchestration system."""
        try:
            # Create and start runtime
            self.runtime = InProcessRuntime()
            self.runtime.start()

            # Create agents for Magentic orchestration
            agents = await self._create_magentic_agents()

            # Create Magentic orchestration (Gemini - commented out)
            # manager_service = GoogleAIChatCompletion(
            #     gemini_model_id=self.gemini_config["ai_model_id"],
            #     api_key=self.gemini_config["api_key"]
            # )

            # Create Magentic orchestration with OpenAI
            manager_service = OpenAIChatCompletion(
                ai_model_id=self.openai_config["ai_model_id"],
                api_key=self.openai_config["api_key"]
            )

            # # Create Magentic orchestration (Ollama - commented out)
            # manager_service = OllamaChatCompletion(
            #     ai_model_id=self.ollama_config.ai_model_id
            # )

            # Create Magentic orchestration without structured output requirement
            try:
                # First try with OpenAI manager
                self.orchestration = MagenticOrchestration(
                    members=agents,
                    manager=StandardMagenticManager(chat_completion_service=manager_service),
                    agent_response_callback=self._agent_response_callback,
                )
            except Exception as structured_error:
                print(f"Error: Could not create Magentic with OpenAI manager: {structured_error}")
                # print("Trying alternative approach...")

                # # Create a simple orchestration without the structured output requirement
                # from semantic_kernel.agents import AgentGroupChat
                # self.orchestration = AgentGroupChat(
                #     agents=agents,
                #     selection_strategy=None  # Use default selection
                # )

            print("Magentic orchestration initialized successfully")

        except Exception as e:
            print(f"Failed to initialize Magentic orchestration: {e}")
            raise

    async def _create_magentic_agents(self) -> List[Agent]:
        """Create agents for Magentic orchestration."""
        agents = []

        # Sales Assistant Agent (wrapped for Magentic)
        sales_agent = ChatCompletionAgent(
            name="SalesAssistant",
            description="A sales assistant with access to CRM, email/calendar, product catalog, and document generation tools",
            instructions="""You are a sales assistant AI with comprehensive sales support capabilities.

Your responsibilities include:
1. Managing customer relationships through CRM operations
2. Generating quotes and proposals for customers
3. Scheduling meetings and managing calendar coordination
4. Providing product recommendations based on customer needs
5. Creating professional documents like contracts and implementation plans

You have access to:
- CRM tools for customer data and interaction tracking
- Email and calendar tools for communication and scheduling
- Product catalog for pricing and recommendations
- Document generation for proposals and contracts

Always be professional, thorough, and focus on delivering value to customers and the sales team.
When given a task, use the appropriate tools to complete it effectively.""",
            # service=GoogleAIChatCompletion(
            #     gemini_model_id=self.gemini_config["ai_model_id"],
            #     api_key=self.gemini_config["api_key"]
            # ),
            service=OpenAIChatCompletion(
                ai_model_id=self.openai_config["ai_model_id"],
                api_key=self.openai_config["api_key"]
            ),

            # service=OllamaChatCompletion(
            #     ai_model_id=self.ollama_config.ai_model_id
            # ),
        )

        agents.append(sales_agent)

        # You can add more specialized agents here in the future
        # For example:
        # - Marketing Agent for lead generation and campaigns
        # - Customer Support Agent for issue resolution
        # - Finance Agent for pricing and contract terms

        return agents

    def _agent_response_callback(self, message: ChatMessageContent) -> None:
        """Callback function to capture agent responses."""
        print(f"**{message.name}**: {message.content[:200]}{'...' if len(message.content) > 200 else ''}")

        # Store response for later processing
        self.agent_responses.append(AgentResponse(
            agent_name=message.name or "Unknown",
            task_id="magentic_task",  # Will be updated with actual task ID
            content=message.content or "",
            success=True,
            tools_used=[],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "response_length": len(message.content or "")
            }
        ))

    async def execute_plan(self, plan: Plan) -> WorkflowResult:
        """Execute a plan using Magentic orchestration."""
        if not self.orchestration or not self.runtime:
            raise RuntimeError("Magentic orchestration not initialized. Call initialize() first.")

        start_time = datetime.now()
        self.agent_responses = []  # Reset responses for new execution
        errors = []

        try:
            # Convert plan to Magentic task description
            task_description = self._plan_to_task_description(plan)

            print(f"\nExecuting plan: {plan.id}")
            print(f"Tasks: {len(plan.tasks)}")
            print(f"Estimated duration: {plan.estimated_total_duration} minutes")
            print(f"\nTask description for Magentic:")
            print(task_description)
            print("\n" + "="*50)

            # Execute using Magentic orchestration
            orchestration_result = await self.orchestration.invoke(
                task=task_description,
                runtime=self.runtime,
            )

            # Wait for results
            final_result = await orchestration_result.get()

            # Update task statuses to completed
            for task in plan.tasks:
                task.status = TaskStatus.COMPLETED

            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # Update agent responses with actual task IDs
            for i, response in enumerate(self.agent_responses):
                if i < len(plan.tasks):
                    response.task_id = plan.tasks[i].id

            return WorkflowResult(
                plan_id=plan.id,
                user_query=plan.user_query,
                agent_responses=self.agent_responses,
                final_response=str(final_result) if final_result else "Task execution completed",
                total_execution_time=execution_time,
                success=True,
                errors=errors
            )

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            errors.append(error_msg)

            # Mark remaining tasks as failed
            for task in plan.tasks:
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.FAILED

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowResult(
                plan_id=plan.id,
                user_query=plan.user_query,
                agent_responses=self.agent_responses,
                final_response=f"Execution failed: {str(e)}",
                total_execution_time=execution_time,
                success=False,
                errors=errors
            )

    def _plan_to_task_description(self, plan: Plan) -> str:
        """Convert a Plan object to a task description for Magentic orchestration."""
        description_parts = [
            f"User Query: {plan.user_query}",
            "",
            "Please execute the following tasks in order:",
            ""
        ]

        for i, task in enumerate(plan.tasks, 1):
            task_desc = [
                f"{i}. {task.title}",
                f"   Description: {task.description}",
                f"   Priority: {task.priority.value}",
                f"   Required Tools: {', '.join(task.required_tools)}",
                f"   Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}",
                ""
            ]
            description_parts.extend(task_desc)

        description_parts.extend([
            "Important guidelines:",
            "- Execute tasks in the order specified, respecting dependencies",
            "- Use the appropriate tools for each task",
            "- Provide detailed and professional responses",
            "- If a task cannot be completed, explain why and suggest alternatives",
            "- Focus on delivering value to the customer and sales team",
            "- COMPLETE ALL TASKS AUTOMATICALLY without waiting for user confirmation",
            "- For emails/documents, create and finalize them without asking for approval",
            "- Provide a final summary of all completed tasks"
        ])

        return "\n".join(description_parts)

    async def execute_single_task(self, task: Task) -> AgentResponse:
        """Execute a single task using the appropriate specialized agent."""
        try:
            if task.agent_type == "sales_assistant":
                return await self.sales_assistant.execute_task(task)
            else:
                # For unknown agent types, use the sales assistant as fallback
                return await self.sales_assistant.execute_task(task)

        except Exception as e:
            return AgentResponse(
                agent_name="MagenticCoordinator",
                task_id=task.id,
                content=f"Failed to execute task: {str(e)}",
                success=False,
                tools_used=[],
                metadata={"error": str(e)}
            )

    async def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available agents."""
        return {
            "sales_assistant": self.sales_assistant.get_agent_info(),
            # Future agents can be added here
        }

    async def test_orchestration(self) -> Dict[str, Any]:
        """Test the orchestration system with a simple task."""
        try:
            if not self.orchestration or not self.runtime:
                await self.initialize()

            test_task = "Please provide a brief overview of your capabilities as a sales assistant."

            print("Testing Magentic orchestration...")

            orchestration_result = await self.orchestration.invoke(
                task=test_task,
                runtime=self.runtime,
            )

            result = await orchestration_result.get()

            return {
                "status": "success",
                "test_task": test_task,
                "result": result,
                "agents_available": len(self.orchestration.members) if self.orchestration else 0
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "test_task": test_task if 'test_task' in locals() else None
            }

    async def cleanup(self):
        """Clean up resources."""
        if self.runtime:
            try:
                await self.runtime.stop_when_idle()
                print("Magentic runtime stopped")
            except Exception as e:
                print(f"Warning: Error stopping runtime: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestration system."""
        return {
            "initialized": self.orchestration is not None and self.runtime is not None,
            "runtime_active": self.runtime is not None,
            "orchestration_ready": self.orchestration is not None,
            "available_agents": len(self.orchestration.members) if self.orchestration else 0,
            "last_execution_responses": len(self.agent_responses)
        }