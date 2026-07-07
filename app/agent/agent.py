"""
agent.py
The autonomous AI agent.

The agent loop"
1. Send task+ tools to claude
2. Claude decides with tool to call
3. we execute the tool and get the result
4. send result back to Calude
5. Claude either calls another tool OR gives final answer
6. Repeat until Claude says it's done(stop_reason = end_turn)
"""

import os 
import anthropic # type: ignore
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from app.agent.tools import TOOL_DEFINATIONS, execute_tool

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a retail analytics assistant for a New Zealand supermarket chain.

You have access to live warehouse data through tools.
Always call the relevant tools first to get real data before answering.

Rules for your response:
- Write in plain simple English only
- No markdown, no tables, no bullet points, no headers, no bold text, no emojis
- Maximum 5 sentences
- Include specific numbers from the data
- Sound like a helpful colleague, not a report
"""

def run_agent(task: str) -> str:
    """
    Run the agent on a task.
    The agent autonomously decides which tools to call and 
    chains them together until it has a complete answer.
    """

    # start the conversation
    messages = [{"role": "user", "content": task}]

    # Agent loop - keeps running until Claude ays its done
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINATIONS,
            messages=messages,
        )

        # Case1: Claude want to call a tool
        if response.stop_reason == "tool_use":
            # Add Claudes response to message history
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # find all tool calls in the response
            tool_results =[]
            for block in response.content:
                if block.type =="tool_use":
                    # Execute the tool
                    result = execute_tool(block.name, block.input)

                    # Collect the result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Send tool results back to Claude
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # case2: Claude has finished and gives final answer
        elif response.stop_reason =="end_turn":
            final_answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_answer += block.text
            return final_answer
        
        # case3: something unexpected
        else:
            return f"Agent stopped unexpectedly: {response.stop_reason}"
