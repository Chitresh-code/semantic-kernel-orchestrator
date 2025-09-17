#!/usr/bin/env python3
"""
Test script for the multi-agent orchestration system.
Tests the complete workflow from user query to final response.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestration import WorkflowManager


async def test_orchestration_system():
    """Test the complete orchestration system with a comprehensive query."""
    print("Multi-Agent Orchestration System Test")
    print("=" * 50)

    # Initialize the workflow manager
    workflow_manager = WorkflowManager()

    try:
        print("\nInitializing system...")
        await workflow_manager.initialize()
        print("System initialized successfully.")

        # Test query that exercises multiple tools and capabilities
        test_query = """
        I need help with customer Acme Corporation. Please pull their complete customer data,
        analyze their interaction history, and suggest the next best actions.
        If they look like a good candidate for upselling, generate a quote for
        our Enterprise Software License professional tier and create a follow-up
        email to schedule a demo meeting.
        """

        print(f"\nTest Query:")
        print(f"'{test_query.strip()}'")
        print("\nProcessing query...")
        print("-" * 30)

        # Process the query through the complete workflow
        start_time = datetime.now()
        result = await workflow_manager.process_user_query(test_query)
        end_time = datetime.now()

        # Display results
        print(f"\nExecution completed in {(end_time - start_time).total_seconds():.2f} seconds")
        print(f"Success: {result.success}")

        if result.success:
            print("\nFinal Response:")
            print("-" * 15)
            print(result.final_response)

            print(f"\nAgent Activities ({len(result.agent_responses)} responses):")
            for i, response in enumerate(result.agent_responses, 1):
                tools_used = f" (used: {', '.join(response.tools_used)})" if response.tools_used else ""
                status = "SUCCESS" if response.success else "FAILED"
                print(f"  {i}. {response.agent_name}: {status}{tools_used}")
        else:
            print("\nExecution failed:")
            for error in result.errors:
                print(f"  - {error}")

        print(f"\nPlan Details:")
        print(f"  Plan ID: {result.plan_id}")
        print(f"  Total execution time: {result.total_execution_time:.2f} seconds")

        # Test system status
        print("\nSystem Status Check:")
        print("-" * 20)
        status = await workflow_manager.get_system_status()

        wm_status = status.get("workflow_manager", {})
        planner_status = status.get("planner", {})
        coord_status = status.get("coordinator", {})

        print(f"Workflow Manager: {'Ready' if wm_status.get('ready') else 'Not Ready'}")
        print(f"Planner: {'Available' if planner_status.get('available') else 'Unavailable'}")
        print(f"Coordinator: {'Ready' if coord_status.get('orchestration_ready') else 'Not Ready'}")
        print(f"Available Agents: {coord_status.get('available_agents', 0)}")

        # Test capabilities
        print("\nSystem Capabilities:")
        print("-" * 20)
        capabilities = await workflow_manager.get_available_capabilities()

        if "error" not in capabilities:
            agents = capabilities.get("available_agents", {})
            print(f"Available agent types: {list(agents.keys())}")

            supported_queries = capabilities.get("supported_queries", [])
            print(f"Supported query types: {len(supported_queries)}")

            example_queries = capabilities.get("example_queries", [])
            print(f"Example queries available: {len(example_queries)}")
        else:
            print(f"Error getting capabilities: {capabilities['error']}")

        return result.success

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        return False

    finally:
        # Cleanup
        try:
            await workflow_manager.cleanup()
            print("\nSystem cleanup completed.")
        except Exception as e:
            print(f"Warning during cleanup: {e}")


async def test_individual_components():
    """Test individual components separately."""
    print("\nIndividual Component Tests")
    print("=" * 30)

    workflow_manager = WorkflowManager()

    try:
        # Test planner only
        print("\nTesting Planner Agent...")
        simple_query = "Get customer information for CUST001 and send them a follow-up email"

        plan = await workflow_manager.planner.create_plan(simple_query)
        print(f"Plan created with {len(plan.tasks)} tasks:")

        for i, task in enumerate(plan.tasks, 1):
            print(f"  {i}. {task.title} (priority: {task.priority.value})")
            print(f"     Tools needed: {', '.join(task.required_tools)}")
            if task.dependencies:
                print(f"     Dependencies: {', '.join(task.dependencies)}")

        # Validate the plan
        validation = await workflow_manager.planner.validate_plan(plan)
        print(f"\nPlan validation: {'PASSED' if validation['valid'] else 'FAILED'}")

        if not validation['valid']:
            print("Validation errors:")
            for error in validation['errors']:
                print(f"  - {error}")

        if validation['warnings']:
            print("Validation warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")

        return validation['valid']

    except Exception as e:
        print(f"Component test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests and provide summary."""
    print("Starting Multi-Agent Orchestration System Tests")
    print("=" * 55)
    print(f"Test started at: {datetime.now()}")

    test_results = []

    # Test 1: Individual components
    print("\n" + "=" * 55)
    print("TEST 1: Individual Component Tests")
    print("=" * 55)

    try:
        component_result = await test_individual_components()
        test_results.append(("Component Tests", component_result))
        print(f"\nComponent test result: {'PASSED' if component_result else 'FAILED'}")
    except Exception as e:
        print(f"Component test error: {e}")
        test_results.append(("Component Tests", False))

    # Test 2: Full workflow
    print("\n" + "=" * 55)
    print("TEST 2: Full Workflow Integration Test")
    print("=" * 55)

    try:
        workflow_result = await test_orchestration_system()
        test_results.append(("Full Workflow", workflow_result))
        print(f"\nFull workflow test result: {'PASSED' if workflow_result else 'FAILED'}")
    except Exception as e:
        print(f"Full workflow test error: {e}")
        test_results.append(("Full Workflow", False))

    # Test summary
    print("\n" + "=" * 55)
    print("TEST SUMMARY")
    print("=" * 55)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1

    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    print(f"Test completed at: {datetime.now()}")

    if passed_tests == total_tests:
        print("\nAll tests PASSED! The orchestration system is working correctly.")
        return True
    else:
        print(f"\n{total_tests - passed_tests} test(s) FAILED. Please check the error messages above.")
        return False


if __name__ == "__main__":
    try:
        # Run the test suite
        success = asyncio.run(run_all_tests())

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal test error: {e}")
        sys.exit(1)