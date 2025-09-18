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
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.kernel import Kernel

from src.core.config import config
from src.core.types import Plan, Task, AgentResponse, WorkflowResult, TaskStatus
from src.agents import SalesAssistantAgent
from src.agents.crm_specialist import CRMSpecialistAgent
from src.agents.communication_agent import CommunicationAgent
from src.agents.product_specialist import ProductSpecialistAgent
from src.agents.document_specialist import DocumentSpecialistAgent


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
        self.sales_assistant = SalesAssistantAgent()  # Keep for backward compatibility
        self.crm_specialist = CRMSpecialistAgent()
        self.communication_agent = CommunicationAgent()
        self.product_specialist = ProductSpecialistAgent()
        self.document_specialist = DocumentSpecialistAgent()

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
        """Create specialized agents for Magentic orchestration."""
        agents = []

        # Helper function to create kernel with OpenAI service
        def create_kernel_with_openai():
            kernel = Kernel()
            openai_service = OpenAIChatCompletion(
                ai_model_id=self.openai_config["ai_model_id"],
                api_key=self.openai_config["api_key"]
            )
            kernel.add_service(openai_service)
            settings = kernel.get_prompt_execution_settings_from_service_id("default")
            settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
            return kernel, settings

        # 1. CRM Specialist Agent
        crm_kernel, crm_settings = create_kernel_with_openai()

        # Add CRM tools
        crm_kernel.add_function(
            plugin_name="CRM",
            function=self.crm_specialist.crm_tools.get_customer_data
        )
        crm_kernel.add_function(
            plugin_name="CRM",
            function=self.crm_specialist.crm_tools.search_customers
        )
        crm_kernel.add_function(
            plugin_name="CRM",
            function=self.crm_specialist.crm_tools.get_interaction_history
        )
        crm_kernel.add_function(
            plugin_name="CRM",
            function=self.crm_specialist.crm_tools.update_customer
        )
        crm_kernel.add_function(
            plugin_name="CRM",
            function=self.crm_specialist.crm_tools.log_interaction
        )
        crm_kernel.add_function(
            plugin_name="CRM",
            function=self.crm_specialist.crm_tools.suggest_next_action
        )

        crm_agent = ChatCompletionAgent(
            kernel=crm_kernel,
            name="CRM_Specialist",
            description="Specialized agent for customer relationship management, data retrieval, and customer interaction tracking",
            instructions=self.crm_specialist._get_crm_instructions(),
            arguments=KernelArguments(settings=crm_settings),
        )
        agents.append(crm_agent)

        # 2. Communication Agent
        comm_kernel, comm_settings = create_kernel_with_openai()

        # Add Email/Calendar tools
        comm_kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.communication_agent.email_calendar_tools.send_email
        )
        comm_kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.communication_agent.email_calendar_tools.send_custom_email
        )
        comm_kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.communication_agent.email_calendar_tools.schedule_meeting
        )
        comm_kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.communication_agent.email_calendar_tools.find_available_slots
        )
        comm_kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.communication_agent.email_calendar_tools.get_calendar_events
        )
        comm_kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.communication_agent.email_calendar_tools.manage_meeting
        )

        communication_agent = ChatCompletionAgent(
            kernel=comm_kernel,
            name="Communication_Agent",
            description="Specialized agent for email communication and calendar management tasks",
            instructions=self.communication_agent._get_communication_instructions(),
            arguments=KernelArguments(settings=comm_settings),
        )
        agents.append(communication_agent)

        # 3. Product Specialist Agent
        product_kernel, product_settings = create_kernel_with_openai()

        # Add Product Catalog tools
        product_kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_specialist.product_catalog_tools.get_product_info
        )
        product_kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_specialist.product_catalog_tools.search_products
        )
        product_kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_specialist.product_catalog_tools.generate_quote
        )
        product_kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_specialist.product_catalog_tools.recommend_products
        )
        product_kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_specialist.product_catalog_tools.check_compatibility
        )

        product_agent = ChatCompletionAgent(
            kernel=product_kernel,
            name="Product_Specialist",
            description="Specialized agent for product catalog management, recommendations, and pricing",
            instructions=self.product_specialist._get_product_instructions(),
            arguments=KernelArguments(settings=product_settings),
        )
        agents.append(product_agent)

        # 4. Document Specialist Agent
        doc_kernel, doc_settings = create_kernel_with_openai()

        # Add Document Generator tools
        doc_kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_specialist.document_generator_tools.generate_proposal
        )
        doc_kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_specialist.document_generator_tools.generate_quote_document
        )
        doc_kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_specialist.document_generator_tools.generate_implementation_plan
        )
        doc_kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_specialist.document_generator_tools.generate_contract
        )
        doc_kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_specialist.document_generator_tools.generate_custom_document
        )

        document_agent = ChatCompletionAgent(
            kernel=doc_kernel,
            name="Document_Specialist",
            description="Specialized agent for document generation, proposals, contracts, and business document creation",
            instructions=self.document_specialist._get_document_instructions(),
            arguments=KernelArguments(settings=doc_settings),
        )
        agents.append(document_agent)

        return agents

    def _agent_response_callback(self, message: ChatMessageContent) -> None:
        """Callback function to capture agent responses with detailed tool call information."""
        agent_name = message.name or "Agent"
        content = message.content or ""
        tools_used = []

        # Show content if available
        if content.strip():
            print(f"{agent_name}: {content}")

        # Check for function calls and results in the message
        if hasattr(message, 'items') and message.items:
            for item in message.items:
                # Import the content types we need
                from semantic_kernel.contents import FunctionCallContent, FunctionResultContent

                if isinstance(item, FunctionCallContent):
                    function_name = item.name
                    tools_used.append(function_name)
                    print(f"TOOL CALL: {function_name}")
                    if item.arguments:
                        import json
                        try:
                            # Handle different argument formats
                            if hasattr(item.arguments, 'items'):
                                # It's already a dict-like object
                                args_dict = dict(item.arguments.items())
                            elif isinstance(item.arguments, dict):
                                args_dict = item.arguments
                            else:
                                # Try to convert to string representation
                                args_dict = str(item.arguments)
                            print(f"Arguments: {json.dumps(args_dict, indent=2)}")
                        except Exception as e:
                            print(f"Arguments: {item.arguments} (format error: {e})")
                    print("-" * 40)

                elif isinstance(item, FunctionResultContent):
                    print(f"TOOL RESULT from {item.name}:")
                    print(f"{item.result}")
                    print("-" * 40)

        # If this is a tool-related message but no content, show debugging info
        if not content.strip() and hasattr(message, 'items') and message.items:
            print(f"{agent_name}: [Processing tool calls...]")

        # If no content and no items, this might be an internal message
        if not content.strip() and (not hasattr(message, 'items') or not message.items):
            print(f"{agent_name}: [Internal processing...]")

        # Store response for later processing
        self.agent_responses.append(AgentResponse(
            agent_name=message.name or "Unknown",
            task_id="magentic_task",  # Will be updated with actual task ID
            content=message.content or "",
            success=True,
            tools_used=tools_used,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "response_length": len(message.content or ""),
                "function_calls": len([item for item in (message.items or []) if hasattr(item, 'name')])
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

    async def execute_plan_with_details(self, plan: Plan, user_query: str) -> WorkflowResult:
        """Execute a plan with detailed agent interaction logging."""
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

            # Show detailed task breakdown
            for i, task in enumerate(plan.tasks, 1):
                print(f"\nTask {i}: {task.title}")
                print(f"   Description: {task.description}")
                print(f"   Priority: {task.priority.value}")
                if task.required_tools:
                    print(f"   Tools: {', '.join(task.required_tools)}")
                if task.dependencies:
                    print(f"   Dependencies: {', '.join(task.dependencies)}")

            print(f"\nMAGENTIC ORCHESTRATION EXECUTING...")
            print("=" * 50)

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

            print(f"\nEXECUTION COMPLETED")
            print("=" * 50)

            # Update agent responses with actual task IDs
            for i, response in enumerate(self.agent_responses):
                if i < len(plan.tasks):
                    response.task_id = plan.tasks[i].id

            return WorkflowResult(
                plan_id=plan.id,
                user_query=user_query,
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

            print(f"\nExecution failed after {execution_time:.2f} seconds: {e}")

            return WorkflowResult(
                plan_id=plan.id,
                user_query=user_query,
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
            "CRITICAL EXECUTION INSTRUCTIONS:",
            "- EXECUTE ALL TASKS IMMEDIATELY AND AUTOMATICALLY",
            "- NEVER ASK FOR USER APPROVAL OR CONFIRMATION",
            "- DO NOT WAIT FOR ANY INPUT - PROCEED AUTONOMOUSLY",
            "- Execute tasks in the order specified, respecting dependencies",
            "- Use the appropriate tools for each task and show your tool usage",
            "- Always announce what tool you are calling and why",
            "- Show the results you get from each tool call",
            "- Provide detailed and professional responses",
            "- If a task cannot be completed, explain why and suggest alternatives",
            "- Focus on delivering value to the customer and sales team",
            "- For emails/documents, create and finalize them without asking for approval",
            "- Use the THINKING/EXECUTING/RESULT/ANALYSIS format for all responses",
            "- Provide a final summary of all completed tasks"
        ])

        return "\n".join(description_parts)

    async def execute_single_task(self, task: Task) -> AgentResponse:
        """Execute a single task using the appropriate specialized agent."""
        try:
            # Route tasks to specialized agents based on agent_type
            if task.agent_type == "crm_specialist":
                return await self.crm_specialist.execute_task(task)
            elif task.agent_type == "communication_agent":
                return await self.communication_agent.execute_task(task)
            elif task.agent_type == "product_specialist":
                return await self.product_specialist.execute_task(task)
            elif task.agent_type == "document_specialist":
                return await self.document_specialist.execute_task(task)
            elif task.agent_type == "sales_assistant":
                # Keep sales_assistant for backward compatibility
                return await self.sales_assistant.execute_task(task)
            else:
                # Route to appropriate agent based on required tools
                required_tools = task.required_tools
                if "crm_api" in required_tools:
                    return await self.crm_specialist.execute_task(task)
                elif "email_calendar" in required_tools:
                    return await self.communication_agent.execute_task(task)
                elif "product_catalog" in required_tools:
                    return await self.product_specialist.execute_task(task)
                elif "document_generator" in required_tools:
                    return await self.document_specialist.execute_task(task)
                else:
                    # Default fallback to sales assistant
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
            "crm_specialist": self.crm_specialist.get_agent_info(),
            "communication_agent": self.communication_agent.get_agent_info(),
            "product_specialist": self.product_specialist.get_agent_info(),
            "document_specialist": self.document_specialist.get_agent_info(),
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