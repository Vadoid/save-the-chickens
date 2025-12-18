# Marketing Agent App

This application hosts the **Marketing Agent** as a standalone service utilizing the **Agent2Agent (A2A) Protocol**.

## Overview
The Marketing Agent is an AI expert specialized in generating creative social media copy for retail products. It is exposed via an A2A-compliant HTTP server, allowing other agents (like the Chickens Agent) to consult it remotely.

## A2A Terminology
This implementation follows the [A2A Protocol Specification](https://a2a-protocol.org/).

### Agent Card
The **Agent Card** is a JSON document that acts as the agent's "digital business card." It describes the agent's identity, capabilities, and endpoints.
-   **Endpoint**: `GET /.well-known/agent-card`
-   **Purpose**: Allows clients to discover and understand how to interact with this agent.

### Agent Executor
The logic of the agent is encapsulated in an **Agent Executor**. This component receives A2A tasks/messages, processes them using the Google ADK `Runner`, and returns the results.

### A2A Server
The server wraps the executor and exposes standard endpoints:
-   `POST /sendMessage`: accepts JSON-RPC 2.0 requests to interact with the agent.

## Running the Server
To start the Marketing Agent server:

1.  Ensure you are in the project root (`save-the-chickens`).
2.  Run the server module using the ADK virtual environment:
    ```bash
    # Option 1: Using the venv directly
    ./.adkvenv/bin/python -m marketing_app.server

    # Option 2: Active venv first
    # source .adkvenv/bin/activate
    # python -m marketing_app.server
    ```
3.  The server will listen on `http://localhost:8001`.

## Interaction
Once running, you can interact with it using any A2A Client or by sending a raw JSON-RPC request to `/`.

### Example (curl)
Messages are sent using `jsonrpc: 2.0` and the `message/send` method. The `params` must contain a `message` object with a `role` and `parts`.

```bash
curl -X POST http://localhost:8001/ \
-H "Content-Type: application/json" \
-d '{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": 1,
  "params": {
    "message": {
      "role": "user",
      "parts": [{"text": "Hello, can you help me with a slogan for organic eggs?"}]
    }
  }
}'
```

### Get Agent Card (curl)
To check the agent's capabilities and identity:
```bash
curl http://localhost:8001/.well-known/agent-card.json
```
