#!/usr/bin/env python3
"""
Debug the planner agent specifically
"""
import asyncio
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.planner.planner_agent import PlannerAgent

async def debug_planner():
    """Debug the planner agent"""
    print("Testing PlannerAgent...")

    try:
        # Initialize planner
        planner = PlannerAgent()

        # Simple test query
        test_query = "Get customer information for CUST001 and send them a follow-up email"

        print(f"Query: {test_query}")
        print("Creating plan...")

        # Get the plan
        plan = await planner.create_plan(test_query)

        print(f"Plan created successfully!")
        print(f"Plan ID: {plan.id}")
        print(f"Tasks: {len(plan.tasks)}")

        for i, task in enumerate(plan.tasks, 1):
            print(f"  {i}. {task.title}")
            print(f"     Description: {task.description}")
            print(f"     Tools: {task.required_tools}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_planner())
    sys.exit(0 if success else 1)