# Multi-Agent Sales Orchestration System

A comprehensive multi-agent orchestration system built with Semantic Kernel and OpenAI for automated sales operations, customer relationship management, and workflow coordination.

## Overview

This system implements an intelligent workflow orchestration architecture where user queries are automatically broken down into structured tasks and executed by specialized AI agents. The system follows a three-stage pipeline:

1. **Planning**: User queries are analyzed and decomposed into specific, actionable tasks
2. **Orchestration**: Tasks are coordinated and executed by specialized agents using Magentic orchestration
3. **Execution**: Agents utilize various tools (CRM, email, documents) to complete tasks and generate results

## Architecture Components

### Core Components

- **Workflow Manager**: Central coordinator that manages the entire pipeline from query to response
- **Planner Agent**: Analyzes user requests and creates structured execution plans with task dependencies
- **Magentic Coordinator**: Orchestrates task execution using Semantic Kernel's Magentic framework
- **Specialized Agents**: Four focused agents handle distinct business functions

### Specialized Agents

The system employs four specialized agents with distributed tool access:

### **CRM Specialist Agent (6 tools)**

- Customer data retrieval and search
- Interaction history tracking
- Customer information updates
- Next action recommendations

### **Communication Agent (6 tools)**

- Email composition and delivery
- Meeting scheduling and calendar coordination
- Calendar availability management
- Meeting logistics coordination

### **Product Specialist Agent (5 tools)**

- Product information and pricing access
- Product search and recommendations
- Quote generation and pricing analysis
- Compatibility verification

### **Document Specialist Agent (5 tools)**

- Proposal and quote document generation
- Contract drafting
- Implementation plan development
- Custom business document creation

## Requirements

- Python 3.8+
- OpenAI API access
- Required Python packages (see pyproject.toml)

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd orchestration
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Configure environment variables**
   Create a `.env` file with your OpenAI credentials:

   ```bash
   OPENAI_API_KEY="your-openai-api-key"
   OPENAI_MODEL_ID="gpt-4o-mini"
   ```

4. **Run the test suite**

   ```bash
   python test.py
   ```

5. **Run quick test**

   ```bash
   python quick_test.py
   ```

## Usage

### Basic Usage

```python
from src.orchestration import WorkflowManager

# Initialize the system
workflow_manager = WorkflowManager()
await workflow_manager.initialize()

# Process a user query
result = await workflow_manager.process_user_query(
    "Pull customer data for Acme Corp and send them a follow-up email"
)

print(result.final_response)
```

## Sample Test Prompts

### Customer Management

```text
"Pull customer data for TechCorp Industries and analyze their purchase history"
"Find all customers who haven't been contacted in the last 30 days"
"Look up customer ABC123 and update their status based on recent interactions"
```

### Sales & Upselling

```text
"Review Acme Corporation's account and identify upselling opportunities"
"Generate a quote for Microsoft Corp for our Enterprise Software License"
"Analyze Global Solutions Inc's spending pattern and recommend product bundles"
```

### Communication & Scheduling

```text
"Send follow-up emails to all customers who requested demos last week"
"Schedule demo meetings with all prospects in the Enterprise pipeline"
"Draft a product announcement email for our new analytics tool"
```

### Complex Multi-Step Workflows

```text
"Research Netflix as a prospect, create a proposal for our streaming analytics platform, and schedule a presentation"

"Pull data for all Q4 renewals, generate renewal quotes with 10% discount, and send follow-up emails"

"Analyze Apple Inc's interaction history, generate an Enterprise upgrade quote, create a proposal document, and draft a meeting invitation"
```

### Document Generation

```text
"Create a proposal for Samsung Electronics including pricing and implementation timeline"
"Generate a contract for the Enterprise Software License deal with Oracle"
"Draft an implementation plan for the new CRM integration project"
```

## Configuration

The system supports multiple AI providers through configuration:

- **OpenAI**: Currently active (gpt-4o-mini)
- **Gemini**: Available (commented out in config)
- **Ollama**: Available with limited structured output support

## Testing

Run the comprehensive test suite:

```bash
python test.py
```

This will execute:

- Individual component tests (planner validation)
- Full workflow integration tests
- System status verification

## Project Structure

```text
src/
  core/           # Core types and configuration
  agents/         # Specialized agents and tools
    crm_specialist.py      # CRM operations agent
    communication_agent.py # Email and calendar agent
    product_specialist.py  # Product catalog agent
    document_specialist.py # Document generation agent
  planner/        # Task planning and decomposition
  orchestration/  # Workflow coordination and execution
  main.py         # CLI interface

tests/            # Test files
test.py           # Main test suite
quick_test.py     # Quick validation test
```

## Features

- Automatic task decomposition from natural language queries
- Specialized agent architecture with distributed tool access
- Multi-agent coordination with dependency management
- Comprehensive tool integration for sales operations
- Professional document and communication generation
- Structured JSON output with validation
- Error handling and workflow recovery
- Intelligent task routing based on agent capabilities

This system demonstrates advanced AI orchestration capabilities for business process automation, specifically tailored for sales and customer relationship management workflows
