#!/usr/bin/env python3
"""
Chainlit UI for Multi-Agent Orchestration System
Provides a web interface with detailed workflow visibility
"""
import chainlit as cl
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestration import WorkflowManager
from src.core.types import WorkflowResult, AgentResponse, Plan, Task

class WorkflowUI:
    """UI handler for the orchestration system."""

    def __init__(self):
        self.workflow_manager = None
        self.session_start = None
        self.query_count = 0

    async def initialize(self):
        """Initialize the workflow manager."""
        try:
            self.workflow_manager = WorkflowManager()
            await self.workflow_manager.initialize()
            self.session_start = datetime.now()
            return True
        except Exception as e:
            await cl.Message(content=f"❌ Failed to initialize system: {str(e)}").send()
            return False

    async def display_plan(self, plan: Plan):
        """Display the execution plan in a structured format."""
        plan_content = f"""## 📋 Execution Plan Created

**Plan ID:** `{plan.id}`
**Total Tasks:** {len(plan.tasks)}
**Estimated Duration:** {plan.estimated_total_duration or 'Unknown'} minutes

### Tasks:
"""

        for i, task in enumerate(plan.tasks, 1):
            deps_text = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            plan_content += f"""
**{i}. {task.title}** - `{task.priority.value}` priority
- **Description:** {task.description}
- **Tools:** {', '.join(task.required_tools)}
- **Duration:** {task.estimated_duration or 'Unknown'} min{deps_text}
"""

        await cl.Message(content=plan_content).send()

    async def display_agent_response(self, response: AgentResponse, task: Task = None, index: int = 1):
        """Display an individual agent response with details."""

        # Create header with agent info and index
        header = f"## 🤖 Agent Response #{index}: {response.agent_name}"
        if task:
            header += f"\n**Executing Task:** *{task.title}*"

        # Format tools used with more detail
        tools_section = ""
        if response.tools_used:
            tools_section = f"""
### 🔧 Tools Utilized:
{', '.join(f'`{tool}`' for tool in response.tools_used)}
"""

        # Format metadata
        metadata_section = f"""
### ℹ️ Response Details:
- **Content Length:** {len(response.content)} characters
- **Success Status:** {"✅ Success" if response.success else "❌ Failed"}
- **Task ID:** `{response.task_id}`
- **Timestamp:** {response.metadata.get('timestamp', 'Unknown')}
"""

        # Format the full response
        content = f"""{header}
{tools_section}
{metadata_section}

### 💬 Agent Response:

{response.content}

---
"""

        # Send with appropriate styling
        await cl.Message(content=content).send()

    async def display_workflow_progress(self, plan: Plan):
        """Display real-time workflow progress."""
        progress_msg = await cl.Message(content="🔄 **Workflow Execution Started**\n\nInitializing agents...").send()

        # Update progress periodically
        for i, task in enumerate(plan.tasks):
            await asyncio.sleep(0.5)  # Small delay for visual effect
            progress_content = f"""🔄 **Workflow Progress**

**Current Task:** {task.title}
**Progress:** {i + 1}/{len(plan.tasks)} tasks
**Status:** Executing with {', '.join(task.required_tools)}

{'▓' * (i + 1)}{'░' * (len(plan.tasks) - i - 1)} {int((i + 1) / len(plan.tasks) * 100)}%
"""
            progress_msg.content = progress_content
            await progress_msg.update()

        return progress_msg

    async def display_final_result(self, result: WorkflowResult):
        """Display the comprehensive final result."""

        # Status indicator
        status_icon = "✅" if result.success else "❌"
        status_text = "SUCCESS" if result.success else "FAILED"

        # Execution summary
        summary_content = f"""{status_icon} **Workflow {status_text}**

**Execution Time:** {result.total_execution_time:.2f} seconds
**Plan ID:** `{result.plan_id}`
**Agent Responses:** {len(result.agent_responses)}
**Query:** "{result.user_query}"
"""

        if result.errors:
            summary_content += f"\n**❌ Errors:**\n" + "\n".join(f"- {error}" for error in result.errors)

        await cl.Message(content=summary_content).send()

        # Final response in a highlighted box
        final_response_content = f"""## 🎯 Final Response

{result.final_response}
"""

        await cl.Message(content=final_response_content).send()

        # Agent activities summary
        if result.agent_responses:
            activities_content = "## 📊 Agent Activities Summary\n\n"

            for i, response in enumerate(result.agent_responses, 1):
                success_icon = "✅" if response.success else "❌"
                activities_content += f"{i}. {success_icon} **{response.agent_name}** - "
                activities_content += f"{len(response.content)} chars"
                if response.tools_used:
                    activities_content += f" (tools: {', '.join(response.tools_used)})"
                activities_content += "\n"

            await cl.Message(content=activities_content).send()

# Global UI instance
ui = WorkflowUI()

@cl.on_chat_start
async def start():
    """Initialize the chat session."""

    # Welcome message
    welcome_content = """# 🚀 Multi-Agent Sales Orchestration System

Welcome! This system uses intelligent planning and specialized AI agents to handle complex sales workflows.

## 🎯 What I can help you with:
- **Customer relationship management** (CRM operations)
- **Sales process automation** and next best actions
- **Quote and proposal generation**
- **Meeting scheduling** and calendar management
- **Product recommendations** and compatibility checks
- **Document creation** (proposals, contracts, plans)

## 💡 Example queries:
- "Pull customer data for CUST001 and suggest next actions"
- "Generate a quote for Enterprise Software for manufacturing company"
- "Review Acme Corporation's account and identify upselling opportunities"
- "Schedule a demo meeting with TechStart Inc and send follow-up email"
- "Create a sales proposal for a new prospect in the finance industry"

---

🔧 Initializing system...
"""

    await cl.Message(content=welcome_content).send()

    # Initialize the system
    if await ui.initialize():
        await cl.Message(content="✅ **System Ready!** You can now submit your sales workflow queries.").send()
    else:
        await cl.Message(content="❌ **System Failed to Initialize.** Please check the logs.").send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""

    if not ui.workflow_manager:
        await cl.Message(content="❌ System not initialized. Please refresh the page.").send()
        return

    user_query = message.content.strip()

    if not user_query:
        await cl.Message(content="Please provide a query for the workflow system.").send()
        return

    ui.query_count += 1

    # Show processing indicator
    processing_msg = await cl.Message(content=f"🔄 **Processing Query #{ui.query_count}**\n\n*{user_query}*\n\nAnalyzing and creating execution plan...").send()

    try:
        # Step 1: Create plan
        processing_msg.content = f"🔄 **Step 1:** Creating execution plan for your query..."
        await processing_msg.update()

        # Process the query (this will create the plan internally)
        result = await ui.workflow_manager.process_user_query(user_query)

        # Get the plan that was created (we'll need to modify the workflow manager to expose this)
        # For now, we'll extract plan info from the result

        processing_msg.content = "✅ **Plan Created!** Displaying execution details..."
        await processing_msg.update()

        # Display the workflow execution in stages
        if result.success:

            # Show execution summary
            execution_content = f"""## 🚀 Workflow Execution Summary

**Query:** "{user_query}"
**Execution Time:** {result.total_execution_time:.2f} seconds
**Agent Responses:** {len(result.agent_responses)}
**Status:** {"✅ Success" if result.success else "❌ Failed"}

### 🔄 Agent Execution Flow:
"""

            # Show each agent response in order
            for i, response in enumerate(result.agent_responses, 1):
                execution_content += f"""
**{i}. {response.agent_name}**
- **Content Length:** {len(response.content)} characters
- **Tools Used:** {', '.join(response.tools_used) if response.tools_used else 'None'}
- **Status:** {"✅ Success" if response.success else "❌ Failed"}
- **Timestamp:** {response.metadata.get('timestamp', 'Unknown')}
"""

            await cl.Message(content=execution_content).send()

            # Show individual agent responses with full content
            for i, response in enumerate(result.agent_responses, 1):
                await ui.display_agent_response(response, index=i)

            # Show final result
            await ui.display_final_result(result)

        else:
            # Handle failure case
            error_content = f"""## ❌ Workflow Failed

**Query:** "{user_query}"
**Errors:** {', '.join(result.errors)}

Please try rephrasing your query or contact support if the issue persists.
"""
            await cl.Message(content=error_content).send()

        # Update processing message to completion
        processing_msg.content = f"✅ **Query #{ui.query_count} Completed** in {result.total_execution_time:.2f}s"
        await processing_msg.update()

    except Exception as e:
        await cl.Message(content=f"❌ **Error processing query:** {str(e)}").send()
        processing_msg.content = f"❌ **Query #{ui.query_count} Failed:** {str(e)}"
        await processing_msg.update()

@cl.on_chat_end
async def end():
    """Handle chat session end."""
    if ui.workflow_manager:
        try:
            await ui.workflow_manager.cleanup()
        except:
            pass

    if ui.session_start:
        session_duration = datetime.now() - ui.session_start
        print(f"Session ended. Duration: {session_duration}, Queries processed: {ui.query_count}")

if __name__ == "__main__":
    # For testing purposes
    print("Starting Chainlit UI for Multi-Agent Orchestration System...")
    print("Run with: chainlit run ui.py")