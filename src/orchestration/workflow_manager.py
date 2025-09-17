import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.types import Plan, WorkflowResult
from src.planner import PlannerAgent
from src.orchestration.magentic_coordinator import MagenticCoordinator


class WorkflowManager:
    """Manages the complete workflow from user query to final response."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.coordinator = MagenticCoordinator()
        self.initialized = False

    async def initialize(self):
        """Initialize all components of the workflow."""
        try:
            print("Initializing workflow manager...")

            # Initialize the Magentic coordinator
            await self.coordinator.initialize()

            self.initialized = True
            print("Workflow manager initialized successfully")

        except Exception as e:
            print(f"Failed to initialize workflow manager: {e}")
            raise

    async def process_user_query(self, user_query: str) -> WorkflowResult:
        """Process a user query through the complete workflow."""
        if not self.initialized:
            await self.initialize()

        start_time = datetime.now()

        try:
            print(f"\nProcessing user query: {user_query}")

            # Step 1: Create plan using planner agent
            print("\nStep 1: Creating execution plan...")
            plan = await self.planner.create_plan(user_query)

            print(f"Plan created with {len(plan.tasks)} tasks")
            for i, task in enumerate(plan.tasks, 1):
                print(f"   {i}. {task.title} ({task.priority.value})")

            # Step 2: Validate the plan
            print("\nStep 2: Validating plan...")
            validation = await self.planner.validate_plan(plan)

            if not validation["valid"]:
                error_msg = f"Plan validation failed: {'; '.join(validation['errors'])}"
                print(f"{error_msg}")

                return WorkflowResult(
                    plan_id=plan.id,
                    user_query=user_query,
                    agent_responses=[],
                    final_response=error_msg,
                    total_execution_time=(datetime.now() - start_time).total_seconds(),
                    success=False,
                    errors=validation["errors"]
                )

            if validation["warnings"]:
                print(f"Plan warnings: {'; '.join(validation['warnings'])}")

            print("Plan validation passed")

            # Step 3: Execute plan using Magentic orchestration
            print("\nStep 3: Executing plan with Magentic orchestration...")
            result = await self.coordinator.execute_plan(plan)

            print(f"\nWorkflow completed in {result.total_execution_time:.2f} seconds")

            return result

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            print(f"{error_msg}")

            return WorkflowResult(
                plan_id="unknown",
                user_query=user_query,
                agent_responses=[],
                final_response=error_msg,
                total_execution_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                errors=[error_msg]
            )

    async def process_simple_query(self, user_query: str) -> str:
        """Process a simple query and return just the final response."""
        try:
            result = await self.process_user_query(user_query)
            return result.final_response

        except Exception as e:
            return f"Error processing query: {str(e)}"

    async def get_system_status(self) -> Dict[str, Any]:
        """Get the status of all workflow components."""
        status = {
            "workflow_manager": {
                "initialized": self.initialized,
                "ready": self.initialized
            },
            "planner": {
                "available": True,
                "model": self.planner.openai_config["ai_model_id"],
                "service": "OpenAI"
            },
            "coordinator": self.coordinator.get_status(),
            "timestamp": datetime.now().isoformat()
        }

        return status

    async def test_workflow(self) -> Dict[str, Any]:
        """Test the complete workflow with a simple query."""
        test_query = "I need to check on customer CUST001 and send them a follow-up email about our latest product offerings."

        print("\nTesting complete workflow...")
        print(f"Test query: {test_query}")

        try:
            # Test initialization
            if not self.initialized:
                await self.initialize()

            # Test planner
            print("\nTesting planner...")
            plan = await self.planner.create_plan(test_query)
            planner_test = {
                "status": "success",
                "tasks_created": len(plan.tasks),
                "plan_id": plan.id
            }

            # Test coordinator
            print("\nTesting Magentic coordinator...")
            coordinator_test = await self.coordinator.test_orchestration()

            # Test full workflow
            print("\nTesting full workflow...")
            result = await self.process_user_query(test_query)
            workflow_test = {
                "status": "success" if result.success else "failed",
                "execution_time": result.total_execution_time,
                "response_length": len(result.final_response),
                "errors": result.errors
            }

            return {
                "overall_status": "success",
                "planner_test": planner_test,
                "coordinator_test": coordinator_test,
                "workflow_test": workflow_test,
                "test_query": test_query
            }

        except Exception as e:
            return {
                "overall_status": "failed",
                "error": str(e),
                "test_query": test_query
            }

    async def get_available_capabilities(self) -> Dict[str, Any]:
        """Get information about available capabilities."""
        try:
            if not self.initialized:
                await self.initialize()

            # Get agent capabilities
            agents = await self.coordinator.get_available_agents()

            return {
                "workflow_capabilities": [
                    "Query planning and task breakdown",
                    "Multi-agent task execution",
                    "Structured response generation",
                    "Error handling and recovery"
                ],
                "available_agents": agents,
                "supported_queries": [
                    "Customer relationship management",
                    "Sales process automation",
                    "Quote and proposal generation",
                    "Meeting scheduling",
                    "Product recommendations",
                    "Document creation"
                ],
                "example_queries": [
                    "Pull customer data for CUST001 and suggest next best actions",
                    "Generate a quote for Enterprise Software License for a manufacturing company",
                    "Schedule a demo meeting with a prospect and send them a follow-up email",
                    "Create a sales proposal for TechStart Inc including product recommendations",
                    "Find available time slots next week and book a customer review meeting"
                ]
            }

        except Exception as e:
            return {
                "error": f"Failed to get capabilities: {str(e)}"
            }

    async def cleanup(self):
        """Clean up all workflow resources."""
        try:
            if self.coordinator:
                await self.coordinator.cleanup()

            self.initialized = False
            print("Workflow manager cleaned up")

        except Exception as e:
            print(f"Warning during cleanup: {e}")

    def format_result_for_user(self, result: WorkflowResult) -> str:
        """Format a workflow result for user-friendly display."""
        if not result.success:
            return f"Sorry, I encountered an error: {result.final_response}"

        # Create a formatted response
        formatted_parts = [
            f"Query processed successfully in {result.total_execution_time:.1f} seconds",
            "",
            "**Results:**",
            result.final_response
        ]

        if result.agent_responses:
            formatted_parts.extend([
                "",
                "**Agent Activities:**"
            ])

            for response in result.agent_responses:
                if response.success:
                    tools_info = f" (using {', '.join(response.tools_used)})" if response.tools_used else ""
                    formatted_parts.append(f"• {response.agent_name}{tools_info}")

        return "\n".join(formatted_parts)