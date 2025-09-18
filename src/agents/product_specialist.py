from typing import List, Dict, Any
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

from src.core.config import config
from src.core.types import Task, AgentResponse, TaskStatus
from src.agents.tools import ProductCatalogTools


class ProductSpecialistAgent:
    """Product Specialist Agent focused on product catalog and recommendation tasks."""

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

        # Initialize only Product Catalog tools
        self.product_catalog_tools = ProductCatalogTools()

        # Add tools to kernel
        self._register_tools()

        # Create the agent with specialized instructions
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=self.kernel,
            name="Product_Specialist",
            description="Specialized agent for product catalog management, recommendations, and pricing",
            instructions=self._get_product_instructions()
        )

    def _get_product_instructions(self) -> str:
        """Get specialized instructions for product tasks."""
        return """You are a Product Specialist focused exclusively on product catalog management and recommendations.

Your primary responsibilities include:
1. Retrieving detailed product information
2. Searching for products based on criteria
3. Generating accurate quotes and pricing
4. Recommending products based on customer needs
5. Checking product compatibility and requirements
6. Providing comprehensive product analysis

EXECUTION RULES:
- EXECUTE ALL TASKS IMMEDIATELY AND AUTOMATICALLY
- NEVER ASK FOR USER APPROVAL OR CONFIRMATION
- NEVER WAIT FOR ANY INPUT - PROCEED AUTONOMOUSLY
- Use the available product catalog tools to complete tasks efficiently
- Provide accurate and detailed product information
- Focus on matching products to customer requirements
- Include pricing, specifications, and compatibility details
- Suggest optimal product combinations and configurations

Available Product Tools:
- get_product_info: Retrieve detailed product specifications and pricing
- search_products: Find products matching specific criteria
- generate_quote: Create accurate pricing quotes for products
- recommend_products: Suggest products based on customer needs
- check_compatibility: Verify product compatibility and requirements

Always provide comprehensive product information including specifications, pricing, compatibility notes, and relevant recommendations for optimal customer solutions."""

    def _register_tools(self):
        """Register Product Catalog tools with the kernel."""
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

    async def execute_task(self, task: Task) -> AgentResponse:
        """Execute a product-related task."""
        try:
            # Create chat history with task description
            chat_history = ChatHistory()

            # Add context about available tools
            system_message = f"""You are executing the following product task: {task.title}

Task Description: {task.description}
Required Tools: {', '.join(task.required_tools)}
Priority: {task.priority.value}

You have access to comprehensive product catalog management tools:
- Product information retrieval and search
- Quote generation and pricing analysis
- Product recommendations and compatibility checking
- Detailed product specifications and comparisons

Execute this task immediately and provide detailed product information and recommendations."""

            chat_history.add_system_message(system_message)
            chat_history.add_user_message(f"Execute this product task: {task.description}")

            # Get response from the agent
            response = await self.agent.invoke(chat_history)

            if not response or not response.content:
                raise ValueError("No response received from product specialist agent")

            # Determine tools used based on task requirements
            tools_used = self._determine_tools_used(task.required_tools)

            return AgentResponse(
                agent_name="Product_Specialist",
                task_id=task.id,
                content=response.content,
                success=True,
                tools_used=tools_used,
                metadata={
                    "execution_time": "estimated",
                    "task_priority": task.priority.value,
                    "task_type": "product_management",
                    "agent_type": "product_specialist"
                }
            )

        except Exception as e:
            return AgentResponse(
                agent_name="Product_Specialist",
                task_id=task.id,
                content=f"Failed to execute product task: {str(e)}",
                success=False,
                tools_used=[],
                metadata={
                    "error": str(e),
                    "task_type": "product_management",
                    "agent_type": "product_specialist"
                }
            )

    def _determine_tools_used(self, required_tools: List[str]) -> List[str]:
        """Determine which product tools were likely used based on requirements."""
        tool_mapping = {
            "product_catalog": "ProductCatalog"
        }

        used_tools = []
        for tool in required_tools:
            if tool in tool_mapping:
                used_tools.append(tool_mapping[tool])
            elif tool == "product_catalog":
                used_tools.append("ProductCatalog")

        return used_tools if used_tools else ["ProductCatalog"]

    async def get_available_tools(self) -> Dict[str, List[str]]:
        """Get list of available product tools."""
        return {
            "ProductCatalog": [
                "get_product_info",
                "search_products",
                "generate_quote",
                "recommend_products",
                "check_compatibility"
            ]
        }

    async def test_tools(self) -> Dict[str, bool]:
        """Test product tools to ensure they're working properly."""
        tool_status = {}

        try:
            # Test Product Catalog tools
            test_result = self.product_catalog_tools.search_products("software")
            tool_status["ProductCatalog"] = "error" not in test_result.lower()
        except Exception:
            tool_status["ProductCatalog"] = False

        return tool_status

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the product specialist agent."""
        return {
            "name": "Product_Specialist",
            "description": "Specialized agent for product catalog management, recommendations, and pricing",
            "capabilities": [
                "Product information retrieval",
                "Product search and filtering",
                "Quote generation and pricing",
                "Product recommendations",
                "Compatibility analysis",
                "Product comparison and analysis"
            ],
            "supported_tasks": [
                "Search for products",
                "Generate product quotes",
                "Recommend products",
                "Check compatibility",
                "Analyze product specifications",
                "Create product comparisons"
            ],
            "tool_categories": ["ProductCatalog"]
        }


if __name__ == "__main__":
    async def main():
        agent = ProductSpecialistAgent()
        tools = await agent.get_available_tools()
        print("Available Product Tools:")
        for category, tool_list in tools.items():
            print(f"{category}: {', '.join(tool_list)}")

    asyncio.run(main())