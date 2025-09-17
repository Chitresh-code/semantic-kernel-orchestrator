# Running the Chainlit UI

## Prerequisites

Make sure you have the environment activated and dependencies installed:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Install dependencies (if not already done)
uv sync
```

## Starting the UI

Run the Chainlit interface:

```bash
chainlit run ui.py
```

The UI will start on `http://localhost:8000` by default.

## Features

The Chainlit UI provides:

- **Real-time workflow visualization** - See each step of the orchestration
- **Detailed agent responses** - Full content from each agent with tool usage
- **Progress tracking** - Visual progress indicators during execution
- **Interactive chat interface** - Easy query submission and result viewing
- **Structured output display** - Organized presentation of all workflow details

## Sample Queries

Try these example queries:

1. `Review Acme Corporation's account and identify upselling opportunities`
2. `Generate a quote for Enterprise Software for manufacturing company`
3. `Pull customer data for TechCorp Industries and analyze their purchase history`
4. `Schedule a demo meeting with TechStart Inc and send follow-up email`

## Configuration

The UI is configured via `.chainlit` file for:

- Custom theming and colors
- Session settings
- Feature toggles
- Security settings

Modify the configuration file to customize the UI appearance and behavior.