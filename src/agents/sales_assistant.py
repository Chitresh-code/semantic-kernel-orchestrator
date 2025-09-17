from typing import List, Dict, Any
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.contents import ChatHistory

from src.core.config import config
from src.core.types import Task, AgentResponse, TaskStatus
from src.agents.tools import CRMTools, EmailCalendarTools, ProductCatalogTools, DocumentGeneratorTools


class SalesAssistantAgent:
    """Sales Assistant Agent with comprehensive CRM and sales tools."""

    def __init__(self):
        self.config = config.get_sales_assistant_config()
        self.ollama_config = config.get_ollama_config()

        # Initialize kernel and services
        self.kernel = Kernel()
        self.chat_service = OllamaChatCompletion(
            ai_model_id=self.ollama_config.ai_model_id,
            service_id=self.ollama_config.service_id,
            url=self.ollama_config.host
        )
        self.kernel.add_service(self.chat_service)

        # Initialize tools
        self.crm_tools = CRMTools()
        self.email_calendar_tools = EmailCalendarTools()
        self.product_catalog_tools = ProductCatalogTools()
        self.document_generator_tools = DocumentGeneratorTools()

        # Add tools to kernel
        self._register_tools()

        # Create the agent
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=self.kernel,
            name=self.config.name,
            description=self.config.description,
            instructions=self.config.instructions
        )

    def _register_tools(self):
        """Register all tools with the kernel."""
        # CRM Tools
        self.kernel.add_function(
            plugin_name="CRM",
            function=self.crm_tools.get_customer_data
        )
        self.kernel.add_function(
            plugin_name="CRM",
            function=self.crm_tools.search_customers
        )
        self.kernel.add_function(
            plugin_name="CRM",
            function=self.crm_tools.get_interaction_history
        )
        self.kernel.add_function(
            plugin_name="CRM",
            function=self.crm_tools.update_customer
        )
        self.kernel.add_function(
            plugin_name="CRM",
            function=self.crm_tools.log_interaction
        )
        self.kernel.add_function(
            plugin_name="CRM",
            function=self.crm_tools.suggest_next_action
        )

        # Email and Calendar Tools
        self.kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.email_calendar_tools.send_email
        )
        self.kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.email_calendar_tools.send_custom_email
        )
        self.kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.email_calendar_tools.schedule_meeting
        )
        self.kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.email_calendar_tools.find_available_slots
        )
        self.kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.email_calendar_tools.get_calendar_events
        )
        self.kernel.add_function(
            plugin_name="EmailCalendar",
            function=self.email_calendar_tools.manage_meeting
        )

        # Product Catalog Tools
        self.kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_catalog_tools.get_product_info
        )
        self.kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_catalog_tools.search_products
        )
        self.kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_catalog_tools.generate_quote
        )
        self.kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_catalog_tools.recommend_products
        )
        self.kernel.add_function(
            plugin_name="ProductCatalog",
            function=self.product_catalog_tools.check_compatibility
        )

        # Document Generator Tools
        self.kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_generator_tools.generate_proposal
        )
        self.kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_generator_tools.generate_quote_document
        )
        self.kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_generator_tools.generate_implementation_plan
        )
        self.kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_generator_tools.generate_contract
        )
        self.kernel.add_function(
            plugin_name="DocumentGenerator",
            function=self.document_generator_tools.generate_custom_document
        )

    async def execute_task(self, task: Task) -> AgentResponse:
        """Execute a sales-related task."""
        try:
            # Create chat history with task description
            chat_history = ChatHistory()

            # Add context about available tools
            system_message = f"""You are executing the following task: {task.title}

Task Description: {task.description}
Required Tools: {', '.join(task.required_tools)}
Priority: {task.priority.value}

You have access to the following tool categories:
1. CRM: Customer data, interaction history, next action suggestions
2. EmailCalendar: Email templates, meeting scheduling, calendar management
3. ProductCatalog: Product information, quotes, recommendations
4. DocumentGenerator: Proposals, contracts, implementation plans

Please execute this task efficiently and provide a comprehensive response."""

            chat_history.add_system_message(system_message)
            chat_history.add_user_message(f"Please execute this task: {task.description}")

            # Get response from the agent
            response = await self.agent.invoke(chat_history)

            if not response or not response.content:
                raise ValueError("No response received from sales assistant agent")

            # Determine tools used based on task requirements
            tools_used = self._determine_tools_used(task.required_tools)

            return AgentResponse(
                agent_name=self.config.name,
                task_id=task.id,
                content=response.content,
                success=True,
                tools_used=tools_used,
                metadata={
                    "execution_time": "estimated",
                    "task_priority": task.priority.value,
                    "task_type": "sales_assistance"
                }
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.config.name,
                task_id=task.id,
                content=f"Failed to execute task: {str(e)}",
                success=False,
                tools_used=[],
                metadata={
                    "error": str(e),
                    "task_type": "sales_assistance"
                }
            )

    def _determine_tools_used(self, required_tools: List[str]) -> List[str]:
        """Determine which tools were likely used based on requirements."""
        tool_mapping = {
            "crm_api": "CRM",
            "email_calendar": "EmailCalendar",
            "product_catalog": "ProductCatalog",
            "document_generator": "DocumentGenerator"
        }

        used_tools = []
        for tool in required_tools:
            if tool in tool_mapping:
                used_tools.append(tool_mapping[tool])
            else:
                used_tools.append(tool)

        return used_tools

    async def get_available_tools(self) -> Dict[str, List[str]]:
        """Get list of available tools organized by category."""
        return {
            "CRM": [
                "get_customer_data",
                "search_customers",
                "get_interaction_history",
                "update_customer",
                "log_interaction",
                "suggest_next_action"
            ],
            "EmailCalendar": [
                "send_email",
                "send_custom_email",
                "schedule_meeting",
                "find_available_slots",
                "get_calendar_events",
                "manage_meeting"
            ],
            "ProductCatalog": [
                "get_product_info",
                "search_products",
                "generate_quote",
                "recommend_products",
                "check_compatibility"
            ],
            "DocumentGenerator": [
                "generate_proposal",
                "generate_quote_document",
                "generate_implementation_plan",
                "generate_contract",
                "generate_custom_document"
            ]
        }

    async def test_tools(self) -> Dict[str, bool]:
        """Test all tools to ensure they're working properly."""
        tool_status = {}

        try:
            # Test CRM tools
            test_result = self.crm_tools.search_customers("test", "name")
            tool_status["CRM"] = "error" not in test_result.lower()
        except Exception:
            tool_status["CRM"] = False

        try:
            # Test Email/Calendar tools
            test_result = self.email_calendar_tools.find_available_slots(
                "2024-12-20T09:00:00", "2024-12-21T17:00:00"
            )
            tool_status["EmailCalendar"] = "error" not in test_result.lower()
        except Exception:
            tool_status["EmailCalendar"] = False

        try:
            # Test Product Catalog tools
            test_result = self.product_catalog_tools.search_products("software")
            tool_status["ProductCatalog"] = "error" not in test_result.lower()
        except Exception:
            tool_status["ProductCatalog"] = False

        try:
            # Test Document Generator tools
            test_data = '{"name": "Test Customer"}'
            test_products = '{"items": []}'
            test_result = self.document_generator_tools.generate_proposal(
                test_data, test_products
            )
            tool_status["DocumentGenerator"] = "error" not in test_result.lower()
        except Exception:
            tool_status["DocumentGenerator"] = False

        return tool_status

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the sales assistant agent."""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "capabilities": [
                "Customer relationship management",
                "Sales process automation",
                "Quote and proposal generation",
                "Meeting scheduling and coordination",
                "Product recommendations",
                "Document creation and management"
            ],
            "supported_tasks": [
                "Pull CRM records",
                "Suggest next best actions",
                "Generate customer proposals",
                "Schedule meetings",
                "Create quotes",
                "Manage customer interactions"
            ],
            "tool_categories": ["CRM", "EmailCalendar", "ProductCatalog", "DocumentGenerator"]
        }