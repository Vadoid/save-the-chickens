# Save the Chickens - Retail Operations AI Agent (ADK + MCP + A2A)

A production-ready reference implementation of an autonomous retail agent built with **Google's Agent Development Kit (ADK)**. Features **Model Context Protocol (MCP)** for secure tool integration (BigQuery, IoT) and **Agent-to-Agent (A2A)** collaboration for creative workflows.

**What it does:**
- **Natural Language BI**: Query sales, inventory, and waste data using plain English.
- **IoT Integration**: Check real-time freezer temperatures (Mock).
- **Agent-to-Agent (A2A)**: Delegates creative tasks to a specialized Marketing Agent.
- **Agentic Workflow**: Uses Gemini 2.5 Flash to reason across multiple data sources.
- **Modular Architecture**: Built on MCP for easy extensibility.

> **Technical Details**: For a deep dive into the architecture, MCP implementation, and agent configuration, see [chickens_app/README.md](chickens_app/README.md).

## Implementation Overview

This project demonstrates a production-ready agent architecture:

1.  **MCP-First Design**:
    - The agent does not call BigQuery directly. It uses the **Model Context Protocol (MCP)** to communicate with a dedicated tools server.
    - This decouples the "Reasoning Engine" (Agent) from the "Execution Engine" (Tools), allowing for safer, more modular deployments.

2.  **Multi-Agent Collaboration (A2A)**:
    - **Main Agent**: Handles data analysis, SQL generation, and operational logic.
    - **Marketing Agent**: A specialized sub-agent for creative writing.
    - The Main Agent delegates tasks to the Marketing Agent using the `consult_marketing_expert` tool, demonstrating how specialized agents can work together.

3.  **Hybrid Tooling**:
    - Combines **Database Tools** (BigQuery SQL) with **Real-time Tools** (IoT Mock) and **Utility Tools** (Google Maps Links).
    - Shows how an agent can reason across static data and dynamic real-world states.

## Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud Project with BigQuery enabled
- Vertex AI API enabled

### Setup

1.  **Authenticate**
    ```bash
    gcloud auth application-default login
    gcloud config set project <your_project>
    ```

2.  **Configure Environment**
    Create a `.env` file:
    ```bash
    cat > .env << EOF
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    BIGQUERY_DATASET=save_the_chickens
    EOF
    ```

3.  **Install Dependencies**
    ```bash
    python -m venv .adkvenv
    source .adkvenv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Run the Agent**
    ```bash
    ./start_web.sh
    ```
    This opens the Web UI at `http://localhost:8000/dev-ui/?app=chickens_app`.

## Example Queries

**Sales & Inventory:**
- "What are the top 5 products by revenue this month?"
- "Which stores have low stock of Chicken Breasts?"

**Operations (MCP Demo):**
- "Check the freezer temperatures for store S001."
- "Find stores with low stock AND broken freezers."

**Marketing (A2A Demo):**
- "Find expiring chicken breasts and write a tweet to sell them."

**Waste Optimization:**
- "Which products are expiring soon?"
- "Recommend discount strategies for expiring items."

## Project Structure

```
save-the-chickens/
├── chickens_app/             # Agent Source Code
│   ├── agent.py             # Agent Configuration
│   ├── mcp_client.py        # MCP Client Adapter
│   ├── mcp_server.py        # MCP Server (BigQuery + IoT)
│   ├── agent_instructions.txt # System Prompt
│   └── README.md            # Technical Documentation
├── bigquery_source_data/     # Sample Data & Setup Scripts
├── run_agent.py             # CLI Runner
├── evaluate_agent.py        # Evaluation Script
└── start_web.sh             # Web UI Launcher
```

## License

Apache License 2.0
