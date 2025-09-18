from typing import List, Dict, Any
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

from src.core.config import config
from src.core.types import Task, AgentResponse, TaskStatus
from src.agents.tools import EmailCalendarTools


class CommunicationAgent:
    """Communication Agent focused on email and calendar management tasks."""

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

        # Initialize only Email/Calendar tools
        self.email_calendar_tools = EmailCalendarTools()

        # Add tools to kernel
        self._register_tools()

        # Create the agent with specialized instructions
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=self.kernel,
            name="Communication_Agent",
            description="Specialized agent for email communication and calendar management tasks",
            instructions=self._get_communication_instructions()
        )

    def _get_communication_instructions(self) -> str:
        """Get specialized instructions for communication tasks."""
        return """You are a Communication Agent focused exclusively on email and calendar management tasks.

Your primary responsibilities include:
1. Sending emails (both templated and custom)
2. Scheduling meetings and appointments
3. Finding available time slots for meetings
4. Managing calendar events
5. Coordinating communication workflows
6. Managing meeting logistics

EXECUTION RULES:
- EXECUTE ALL TASKS IMMEDIATELY AND AUTOMATICALLY
- NEVER ASK FOR USER APPROVAL OR CONFIRMATION
- NEVER WAIT FOR ANY INPUT - PROCEED AUTONOMOUSLY
- Use the available email and calendar tools to complete tasks efficiently
- Ensure professional and clear communication
- Schedule meetings at optimal times based on availability
- Provide confirmation details for all communication actions

Available Communication Tools:
- send_email: Send templated emails for common scenarios
- send_custom_email: Create and send personalized emails
- schedule_meeting: Book meetings and appointments
- find_available_slots: Check calendar availability
- get_calendar_events: Retrieve calendar information
- manage_meeting: Update or modify existing meetings

Always provide clear confirmations of communication actions taken and include relevant details like scheduled times, email subjects, and recipient information."""

    def _register_tools(self):
        """Register Email and Calendar tools with the kernel."""
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

    async def execute_task(self, task: Task) -> AgentResponse:
        """Execute a communication-related task."""
        try:
            # Create chat history with task description
            chat_history = ChatHistory()

            # Add context about available tools
            system_message = f"""You are executing the following communication task: {task.title}

Task Description: {task.description}
Required Tools: {', '.join(task.required_tools)}
Priority: {task.priority.value}

You have access to comprehensive email and calendar management tools:
- Email composition and delivery (templated and custom)
- Meeting scheduling and coordination
- Calendar availability checking
- Event management and updates

Execute this task immediately and provide detailed confirmation of actions taken."""

            chat_history.add_system_message(system_message)
            chat_history.add_user_message(f"Execute this communication task: {task.description}")

            # Get response from the agent
            response = await self.agent.invoke(chat_history)

            if not response or not response.content:
                raise ValueError("No response received from communication agent")

            # Determine tools used based on task requirements
            tools_used = self._determine_tools_used(task.required_tools)

            return AgentResponse(
                agent_name="Communication_Agent",
                task_id=task.id,
                content=response.content,
                success=True,
                tools_used=tools_used,
                metadata={
                    "execution_time": "estimated",
                    "task_priority": task.priority.value,
                    "task_type": "communication",
                    "agent_type": "communication_agent"
                }
            )

        except Exception as e:
            return AgentResponse(
                agent_name="Communication_Agent",
                task_id=task.id,
                content=f"Failed to execute communication task: {str(e)}",
                success=False,
                tools_used=[],
                metadata={
                    "error": str(e),
                    "task_type": "communication",
                    "agent_type": "communication_agent"
                }
            )

    def _determine_tools_used(self, required_tools: List[str]) -> List[str]:
        """Determine which communication tools were likely used based on requirements."""
        tool_mapping = {
            "email_calendar": "EmailCalendar"
        }

        used_tools = []
        for tool in required_tools:
            if tool in tool_mapping:
                used_tools.append(tool_mapping[tool])
            elif tool == "email_calendar":
                used_tools.append("EmailCalendar")

        return used_tools if used_tools else ["EmailCalendar"]

    async def get_available_tools(self) -> Dict[str, List[str]]:
        """Get list of available communication tools."""
        return {
            "EmailCalendar": [
                "send_email",
                "send_custom_email",
                "schedule_meeting",
                "find_available_slots",
                "get_calendar_events",
                "manage_meeting"
            ]
        }

    async def test_tools(self) -> Dict[str, bool]:
        """Test communication tools to ensure they're working properly."""
        tool_status = {}

        try:
            # Test Email/Calendar tools
            test_result = self.email_calendar_tools.find_available_slots(
                "2024-12-20T09:00:00", "2024-12-21T17:00:00"
            )
            tool_status["EmailCalendar"] = "error" not in test_result.lower()
        except Exception:
            tool_status["EmailCalendar"] = False

        return tool_status

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the communication agent."""
        return {
            "name": "Communication_Agent",
            "description": "Specialized agent for email communication and calendar management tasks",
            "capabilities": [
                "Email composition and delivery",
                "Meeting scheduling and coordination",
                "Calendar management",
                "Availability checking",
                "Communication workflow automation",
                "Professional correspondence"
            ],
            "supported_tasks": [
                "Send emails",
                "Schedule meetings",
                "Check calendar availability",
                "Manage appointments",
                "Coordinate communication",
                "Update calendar events"
            ],
            "tool_categories": ["EmailCalendar"]
        }


if __name__ == "__main__":
    async def main():
        agent = CommunicationAgent()
        tools = await agent.get_available_tools()
        print("Available Communication Tools:")
        for category, tool_list in tools.items():
            print(f"{category}: {', '.join(tool_list)}")

    asyncio.run(main())