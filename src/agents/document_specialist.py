from typing import List, Dict, Any
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

from src.core.config import config
from src.core.types import Task, AgentResponse, TaskStatus
from src.agents.tools import DocumentGeneratorTools


class DocumentSpecialistAgent:
    """Document Specialist Agent focused on document generation and creation tasks."""

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

        # Initialize only Document Generator tools
        self.document_generator_tools = DocumentGeneratorTools()

        # Add tools to kernel
        self._register_tools()

        # Create the agent with specialized instructions
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=self.kernel,
            name="Document_Specialist",
            description="Specialized agent for document generation, proposals, contracts, and business document creation",
            instructions=self._get_document_instructions()
        )

    def _get_document_instructions(self) -> str:
        """Get specialized instructions for document tasks."""
        return """You are a Document Specialist focused exclusively on business document generation and creation.

Your primary responsibilities include:
1. Generating comprehensive sales proposals
2. Creating detailed product quotes and documentation
3. Developing implementation plans and project documentation
4. Drafting contracts and legal documents
5. Creating custom business documents for various purposes
6. Ensuring professional formatting and content quality

EXECUTION RULES:
- EXECUTE ALL TASKS IMMEDIATELY AND AUTOMATICALLY
- NEVER ASK FOR USER APPROVAL OR CONFIRMATION
- NEVER WAIT FOR ANY INPUT - PROCEED AUTONOMOUSLY
- Use the available document generation tools to complete tasks efficiently
- Ensure professional formatting and comprehensive content
- Include all relevant details and specifications
- Maintain consistency in document structure and style
- Provide clear, actionable, and well-organized content

Available Document Tools:
- generate_proposal: Create comprehensive sales proposals
- generate_quote_document: Generate detailed product quotes
- generate_implementation_plan: Develop project implementation plans
- generate_contract: Draft contracts and agreements
- generate_custom_document: Create custom business documents

Always provide well-structured, professional documents with clear sections, appropriate formatting, and comprehensive content that meets business standards and requirements."""

    def _register_tools(self):
        """Register Document Generator tools with the kernel."""
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
        """Execute a document-related task."""
        try:
            # Create chat history with task description
            chat_history = ChatHistory()

            # Add context about available tools
            system_message = f"""You are executing the following document task: {task.title}

Task Description: {task.description}
Required Tools: {', '.join(task.required_tools)}
Priority: {task.priority.value}

You have access to comprehensive document generation tools:
- Proposal and quote generation
- Implementation plan development
- Contract and agreement drafting
- Custom business document creation

Execute this task immediately and provide professional, well-structured documents with comprehensive content."""

            chat_history.add_system_message(system_message)
            chat_history.add_user_message(f"Execute this document task: {task.description}")

            # Get response from the agent
            response = await self.agent.invoke(chat_history)

            if not response or not response.content:
                raise ValueError("No response received from document specialist agent")

            # Determine tools used based on task requirements
            tools_used = self._determine_tools_used(task.required_tools)

            return AgentResponse(
                agent_name="Document_Specialist",
                task_id=task.id,
                content=response.content,
                success=True,
                tools_used=tools_used,
                metadata={
                    "execution_time": "estimated",
                    "task_priority": task.priority.value,
                    "task_type": "document_generation",
                    "agent_type": "document_specialist"
                }
            )

        except Exception as e:
            return AgentResponse(
                agent_name="Document_Specialist",
                task_id=task.id,
                content=f"Failed to execute document task: {str(e)}",
                success=False,
                tools_used=[],
                metadata={
                    "error": str(e),
                    "task_type": "document_generation",
                    "agent_type": "document_specialist"
                }
            )

    def _determine_tools_used(self, required_tools: List[str]) -> List[str]:
        """Determine which document tools were likely used based on requirements."""
        tool_mapping = {
            "document_generator": "DocumentGenerator"
        }

        used_tools = []
        for tool in required_tools:
            if tool in tool_mapping:
                used_tools.append(tool_mapping[tool])
            elif tool == "document_generator":
                used_tools.append("DocumentGenerator")

        return used_tools if used_tools else ["DocumentGenerator"]

    async def get_available_tools(self) -> Dict[str, List[str]]:
        """Get list of available document tools."""
        return {
            "DocumentGenerator": [
                "generate_proposal",
                "generate_quote_document",
                "generate_implementation_plan",
                "generate_contract",
                "generate_custom_document"
            ]
        }

    async def test_tools(self) -> Dict[str, bool]:
        """Test document tools to ensure they're working properly."""
        tool_status = {}

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
        """Get information about the document specialist agent."""
        return {
            "name": "Document_Specialist",
            "description": "Specialized agent for document generation, proposals, contracts, and business document creation",
            "capabilities": [
                "Sales proposal generation",
                "Quote and pricing documentation",
                "Implementation plan development",
                "Contract and agreement drafting",
                "Custom business document creation",
                "Professional document formatting"
            ],
            "supported_tasks": [
                "Generate proposals",
                "Create quote documents",
                "Develop implementation plans",
                "Draft contracts",
                "Create custom documents",
                "Format business documents"
            ],
            "tool_categories": ["DocumentGenerator"]
        }


if __name__ == "__main__":
    async def main():
        agent = DocumentSpecialistAgent()
        tools = await agent.get_available_tools()
        print("Available Document Tools:")
        for category, tool_list in tools.items():
            print(f"{category}: {', '.join(tool_list)}")

    asyncio.run(main())