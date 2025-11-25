# Marketing Agent (Creative Brain)

This is a specialized sub-agent designed to generate creative social media content for the "Save the Chickens" retail chain.

> **Note**: This is a sub-component. For the main project documentation, see [../README.md](../README.md).

## Role
The **Marketing Agent** acts as the "Right Brain" to the main agent's "Left Brain". It takes dry data (stock levels, expiry dates) and turns it into engaging, witty, and urgent marketing copy.

## Persona
- **Tone**: Witty, energetic, pun-loving.
- **Platform**: Optimized for Twitter/X and Instagram (short, emoji-heavy).
- **Goal**: Reduce food waste by driving immediate sales.

## Integration
This agent is **not** meant to be run standalone by the user. Instead, it is called programmatically by the main **Chickens Agent** via the `consult_marketing_expert` tool.

### Flow
1.  **Main Agent** identifies expiring stock.
2.  **Main Agent** calls `consult_marketing_expert(context, goal)`.
3.  **Marketing Agent** receives the prompt, generates copy, and returns it.
4.  **Main Agent** presents the copy to the user.

## Files
- `agent.py`: Defines the agent configuration.
- `instructions.txt`: The system prompt defining the persona and rules.
