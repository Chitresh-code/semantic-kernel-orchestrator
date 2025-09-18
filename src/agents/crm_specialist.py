from typing import List, Dict, Any
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

from src.core.config import config
from src.core.types import Task, AgentResponse, TaskStatus
from src.agents.tools import CRMTools


class CRMSpecialistAgent:
    """CRM Specialist Agent focused on customer relationship management tasks."""

    def __init__(self):
        self.config = config.get_sales_assistant_config()  # Use sales config for now
        self.openai_config = config.get_openai_config()

        # Initialize kernel and services
        self.kernel = Kernel()

        # Initialize with OpenAI chat service
        self.chat_service = OpenAIChatCompletion(
            ai_model_id=self.openai_config["ai_model_id"],
            api_key=self.openai_config["api_key"]
        )

        self.kernel.add_service(self.chat_service)

        # Initialize only CRM tools
        self.crm_tools = CRMTools()

        # Add tools to kernel
        self._register_tools()

        # Create the agent with specialized instructions
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=self.kernel,
            name="CRM_Specialist",
            description="Specialized agent for customer relationship management, data retrieval, and customer interaction tracking",
            instructions=self._get_crm_instructions()
        )

    def _get_crm_instructions(self) -> str:
        """Get specialized instructions for CRM tasks."""
        return """You are a CRM Specialist focused exclusively on customer relationship management tasks.

Your primary responsibilities include:
1. Retrieving customer data from CRM systems
2. Searching for customers by various criteria
3. Managing customer interaction history
4. Updating customer information
5. Logging new customer interactions
6. Suggesting next best actions based on customer data

EXECUTION RULES:
- EXECUTE ALL TASKS IMMEDIATELY AND AUTOMATICALLY
- NEVER ASK FOR USER APPROVAL OR CONFIRMATION
- NEVER WAIT FOR ANY INPUT - PROCEED AUTONOMOUSLY
- Use the available CRM tools to complete tasks efficiently
- Provide detailed, actionable information from CRM data
- Focus on data accuracy and completeness
- Suggest relevant next actions based on customer status and history

Available CRM Tools:
- get_customer_data: Retrieve comprehensive customer information
- search_customers: Find customers by name, industry, or status
- get_interaction_history: Get recent customer interactions
- update_customer: Modify customer information fields
- log_interaction: Record new customer interactions
- suggest_next_action: Recommend next best actions for customers

Always provide structured, detailed responses that include relevant customer data and actionable insights."""

    def _register_tools(self):
        """Register CRM tools with the kernel."""
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

    async def execute_task(self, task: Task) -> AgentResponse:
        """Execute a CRM-related task."""
        try:
            # Create chat history with task description
            chat_history = ChatHistory()

            # Add context about available tools
            system_message = f"""You are executing the following CRM task: {task.title}

Task Description: {task.description}
Required Tools: {', '.join(task.required_tools)}
Priority: {task.priority.value}

You have access to comprehensive CRM tools for customer data management:
- Customer data retrieval and search
- Interaction history tracking
- Customer information updates
- Next action recommendations

Execute this task immediately and provide detailed results."""

            chat_history.add_system_message(system_message)
            chat_history.add_user_message(f"Execute this CRM task: {task.description}")

            # Get response from the agent
            response = await self.agent.invoke(chat_history)

            if not response or not response.content:
                raise ValueError("No response received from CRM specialist agent")

            # Determine tools used based on task requirements
            tools_used = self._determine_tools_used(task.required_tools)

            return AgentResponse(
                agent_name="CRM_Specialist",
                task_id=task.id,
                content=response.content,
                success=True,
                tools_used=tools_used,
                metadata={
                    "execution_time": "estimated",
                    "task_priority": task.priority.value,
                    "task_type": "crm_management",
                    "agent_type": "crm_specialist"
                }
            )

        except Exception as e:
            return AgentResponse(
                agent_name="CRM_Specialist",
                task_id=task.id,
                content=f"Failed to execute CRM task: {str(e)}",
                success=False,
                tools_used=[],
                metadata={
                    "error": str(e),
                    "task_type": "crm_management",
                    "agent_type": "crm_specialist"
                }
            )

    def _determine_tools_used(self, required_tools: List[str]) -> List[str]:
        """Determine which CRM tools were likely used based on requirements."""
        tool_mapping = {
            "crm_api": "CRM"
        }

        used_tools = []
        for tool in required_tools:
            if tool in tool_mapping:
                used_tools.append(tool_mapping[tool])
            elif tool == "crm_api":
                used_tools.append("CRM")

        return used_tools if used_tools else ["CRM"]

    async def get_available_tools(self) -> Dict[str, List[str]]:
        """Get list of available CRM tools."""
        return {
            "CRM": [
                "get_customer_data",
                "search_customers",
                "get_interaction_history",
                "update_customer",
                "log_interaction",
                "suggest_next_action"
            ]
        }

    async def test_tools(self) -> Dict[str, bool]:
        """Test CRM tools to ensure they're working properly."""
        tool_status = {}

        try:
            # Test CRM tools
            test_result = self.crm_tools.search_customers("test", "name")
            tool_status["CRM"] = "error" not in test_result.lower()
        except Exception:
            tool_status["CRM"] = False

        return tool_status

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the CRM specialist agent."""
        return {
            "name": "CRM_Specialist",
            "description": "Specialized agent for customer relationship management, data retrieval, and customer interaction tracking",
            "capabilities": [
                "Customer data retrieval and management",
                "Customer search and filtering",
                "Interaction history tracking",
                "Customer information updates",
                "Next best action recommendations",
                "Customer relationship analysis"
            ],
            "supported_tasks": [
                "Retrieve customer data",
                "Search for customers",
                "Update customer information",
                "Log customer interactions",
                "Analyze customer relationships",
                "Suggest next actions"
            ],
            "tool_categories": ["CRM"]
        }


if __name__ == "__main__":
    async def main():
        agent = CRMSpecialistAgent()
        tools = await agent.get_available_tools()
        print("Available CRM Tools:")
        for category, tool_list in tools.items():
            print(f"{category}: {', '.join(tool_list)}")

    asyncio.run(main())