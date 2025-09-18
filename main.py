import asyncio
import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestration import WorkflowManager


class OrchestrationChatLoop:
    """Enhanced chat loop interface showing detailed agent interactions."""

    def __init__(self):
        self.workflow_manager = WorkflowManager()
        self.session_start = datetime.now()
        self.query_count = 0

    async def initialize(self):
        """Initialize the orchestration system."""
        print("Initializing Multi-Agent Orchestration System...")
        print("-" * 60)

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
        print("-" * 60)

    async def handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.lower().strip()

        if command in ['exit', 'quit', 'bye']:
            print("\nThank you for using the Multi-Agent Orchestration System!")
            print(f"Session duration: {datetime.now() - self.session_start}")
            print(f"Queries processed: {self.query_count}")
            await self.cleanup()
            return True

        return False

    async def process_query(self, user_query: str) -> str:
        """Process a user query and return the response with detailed logging."""
        try:
            print(f"\nProcessing: {user_query}")
            print("-" * 60)

            # Process with detailed logging
            result = await self.workflow_manager.process_user_query_with_details(user_query)

            # Format and display results
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