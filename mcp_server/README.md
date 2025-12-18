# MCP Server Tools

This module (`mcp_server`) consolidates all external tool integrations for the "Save the Chickens" agent.

## Tools Included

### 1. Maps MCP Toolset (`get_maps_mcp_toolset`)
-   **Source**: Google Maps Platform via MCP.
-   **Capabilities**: Place search, routing, distance matrix.
-   **Auth**: Requires `MAPS_API_KEY` defined in environment.

### 2. BigQuery MCP Toolset (`get_bigquery_mcp_toolset`)
-   **Source**: Google BigQuery via MCP.
-   **Capabilities**: SQL query execution, dataset schema inspection.
-   **Auth**: Uses Application Default Credentials (ADC) with the `GOOGLE_CLOUD_PROJECT`.

### 3. Store Temperature IoT (`get_store_temperature`)
-   **Source**: Simulated IoT data.
-   **Capabilities**: Retrieve real-time temperature stats for store units.

### 4. Marketing Agent Client (`consult_marketing_expert`)
-   **Source**: A2A Protocol connection to `marketing_app`.
-   **Capabilities**: Specialist marketing content generation.
-   **Connection**: Connects to `http://localhost:8001/` (Marketing Agent Server).

## Usage

Import the tools in your agent definition:

```python
from mcp_server.tools import (
    get_maps_mcp_toolset,
    get_bigquery_mcp_toolset,
    get_store_temperature,
    consult_marketing_expert
)

tools = [
    get_maps_mcp_toolset(),
    get_bigquery_mcp_toolset(),
    get_store_temperature,
    consult_marketing_expert
]
```
