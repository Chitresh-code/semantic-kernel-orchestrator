import asyncio
import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestration import WorkflowManager


class OrchestrationChatLoop:
    """Simple chat loop interface for the multi-agent orchestration system."""

    def __init__(self):
        self.workflow_manager = WorkflowManager()
        self.session_start = datetime.now()
        self.query_count = 0

    async def initialize(self):
        """Initialize the orchestration system."""
        print("Initializing Multi-Agent Orchestration System...")
        print("=" * 60)

        try:
            await self.workflow_manager.initialize()
            print("System ready!")
            return True

        except Exception as e:
            print(f"Initialization failed: {e}")
            return False

    def print_welcome(self):
        """Print welcome message and instructions."""
        print("\nMulti-Agent Sales Orchestration System")
        print("=" * 60)
        print("This system uses a planner agent to break down your queries")
        print("into tasks, then coordinates specialized sales agents to execute them.")
        print()
        print("What I can help you with:")
        print("• Customer relationship management (CRM operations)")
        print("• Sales process automation and next best actions")
        print("• Quote and proposal generation")
        print("• Meeting scheduling and calendar management")
        print("• Product recommendations and compatibility checks")
        print("• Document creation (proposals, contracts, plans)")
        print()
        print("Example queries:")
        print("• 'Pull customer data for CUST001 and suggest next actions'")
        print("• 'Generate a quote for Enterprise Software for manufacturing company'")
        print("• 'Schedule a demo meeting with TechStart Inc and send follow-up email'")
        print("• 'Create a sales proposal for a new prospect in the finance industry'")
        print()
        print("Commands:")
        print("• 'help' - Show this help message")
        print("• 'status' - Show system status")
        print("• 'test' - Run system tests")
        print("• 'capabilities' - Show detailed capabilities")
        print("• 'exit' or 'quit' - Exit the system")
        print("=" * 60)

    async def handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.lower().strip()

        if command in ['exit', 'quit', 'bye']:
            print("\nThank you for using the Multi-Agent Orchestration System!")
            print(f"Session duration: {datetime.now() - self.session_start}")
            print(f"Queries processed: {self.query_count}")
            await self.cleanup()
            return True

        elif command == 'help':
            self.print_welcome()
            return True

        elif command == 'status':
            print("\nSystem Status:")
            print("-" * 30)
            status = await self.workflow_manager.get_system_status()
            self.print_status(status)
            return True

        elif command == 'test':
            print("\nRunning System Tests...")
            print("-" * 30)
            test_results = await self.workflow_manager.test_workflow()
            self.print_test_results(test_results)
            return True

        elif command == 'capabilities':
            print("\nSystem Capabilities:")
            print("-" * 30)
            capabilities = await self.workflow_manager.get_available_capabilities()
            self.print_capabilities(capabilities)
            return True

        return False

    def print_status(self, status: dict):
        """Print system status in a readable format."""
        wm_status = status.get("workflow_manager", {})
        planner_status = status.get("planner", {})
        coord_status = status.get("coordinator", {})

        print(f"Workflow Manager: {'Ready' if wm_status.get('ready') else 'Not Ready'}")
        print(f"Planner: {'Available' if planner_status.get('available') else 'Unavailable'}")
        print(f"   Model: {planner_status.get('model', 'Unknown')}")
        print(f"Coordinator: {'Ready' if coord_status.get('orchestration_ready') else 'Not Ready'}")
        print(f"   Agents: {coord_status.get('available_agents', 0)}")
        print(f"Status Time: {status.get('timestamp', 'Unknown')}")

    def print_test_results(self, results: dict):
        """Print test results in a readable format."""
        overall = results.get("overall_status", "unknown")
        print(f"Overall Status: {'PASSED' if overall == 'success' else 'FAILED'}")

        if "planner_test" in results:
            planner = results["planner_test"]
            print(f"Planner: {'PASS' if planner.get('status') == 'success' else 'FAIL'}")
            print(f"   Tasks Created: {planner.get('tasks_created', 0)}")

        if "coordinator_test" in results:
            coordinator = results["coordinator_test"]
            print(f"Coordinator: {'PASS' if coordinator.get('status') == 'success' else 'FAIL'}")

        if "workflow_test" in results:
            workflow = results["workflow_test"]
            print(f"Full Workflow: {'PASS' if workflow.get('status') == 'success' else 'FAIL'}")
            print(f"   Execution Time: {workflow.get('execution_time', 0):.2f}s")

        if results.get("overall_status") == "failed":
            print(f"Error: {results.get('error', 'Unknown error')}")

    def print_capabilities(self, capabilities: dict):
        """Print system capabilities in a readable format."""
        if "error" in capabilities:
            print(f"Error getting capabilities: {capabilities['error']}")
            return

        # Workflow capabilities
        wf_caps = capabilities.get("workflow_capabilities", [])
        print("Workflow Capabilities:")
        for cap in wf_caps:
            print(f"   • {cap}")

        # Supported queries
        supported = capabilities.get("supported_queries", [])
        print("\nSupported Query Types:")
        for query_type in supported:
            print(f"   • {query_type}")

        # Example queries
        examples = capabilities.get("example_queries", [])
        print("\nExample Queries:")
        for i, example in enumerate(examples[:3], 1):  # Show first 3 examples
            print(f"   {i}. {example}")

    async def process_query(self, user_query: str) -> str:
        """Process a user query and return the response."""
        try:
            print(f"\nProcessing: {user_query}")
            print("-" * 50)

            result = await self.workflow_manager.process_user_query(user_query)
            response = self.workflow_manager.format_result_for_user(result)

            self.query_count += 1
            return response

        except Exception as e:
            return f"Error processing query: {str(e)}"

    async def run(self):
        """Run the main chat loop."""
        # Initialize system
        if not await self.initialize():
            print("System initialization failed. Exiting.")
            return

        # Show welcome message
        self.print_welcome()

        # Main chat loop
        while True:
            try:
                # Get user input
                print(f"\nQuery #{self.query_count + 1}")
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if await self.handle_special_commands(user_input):
                    break

                # Process regular query
                response = await self.process_query(user_input)
                print(f"\nAssistant:\n{response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye! (Ctrl+C detected)")
                await self.cleanup()
                break

            except Exception as e:
                print(f"\nUnexpected error: {e}")
                print("Please try again or type 'exit' to quit.")

    async def cleanup(self):
        """Clean up system resources."""
        try:
            await self.workflow_manager.cleanup()
        except Exception as e:
            print(f"Cleanup warning: {e}")


async def main():
    """Main entry point."""
    chat_loop = OrchestrationChatLoop()
    await chat_loop.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
