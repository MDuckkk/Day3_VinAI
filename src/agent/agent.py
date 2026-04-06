import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools          # ReAct-format tools (with "fn" key)
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        return f"""You are an intelligent assistant. You have access to these tools:
{tool_descriptions}

Always respond in this exact format:
Thought: <your reasoning>
Action: <tool_name>(<argument>)
Observation: <you will receive this after the action>
... repeat Thought/Action/Observation as needed ...
Final Answer: <your final response to the user>

Rules:
- Only call one tool per Action step.
- Arguments must be plain values, e.g. Action: get_product_detail(p001)
- Stop and give Final Answer once you have enough information.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        # Build a running conversation string passed as the prompt each turn
        conversation = f"User: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            result = self.llm.generate(conversation, system_prompt=self.get_system_prompt())
            response_text = result["content"]
            logger.log_event("LLM_RESPONSE", {"step": steps, "response": response_text})

            conversation += response_text + "\n"
            action = ''

            # ── Check for Final Answer ──────────────────────────────────────
            if "Final Answer:" in response_text:
                final = response_text.split("Final Answer:")[-1].strip()
                logger.log_event("AGENT_END", {"steps": steps, "final_answer": final})
                return final

            # ── Parse Action ────────────────────────────────────────────────
            action_match = re.search(r"Action:\s*(\w+)\(([^)]*)\)", response_text)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()

                logger.log_event("TOOL_CALL", {"tool": tool_name, "args": tool_args})
                observation = self._execute_tool(tool_name, tool_args)
                logger.log_event("TOOL_RESULT", {"tool": tool_name, "result": observation})

                # Feed observation back so LLM continues the loop
                conversation += f"Observation: {observation}\n"
                action += f"Observation: {observation}\n"
            else:
                # LLM gave neither an Action nor a Final Answer — nudge it
                conversation += "Observation: No action detected. Please continue.\n"

            steps += 1

        logger.log_event("AGENT_END", {"steps": steps, "reason": "max_steps_reached"})
        return action

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    # Parse comma-separated positional args (simple case)
                    # For keyword args extend this with inspect / ast.literal_eval
                    parsed_args = [a.strip().strip('"\'') for a in args.split(",") if a.strip()]
                    return str(tool["fn"](*parsed_args))
                except Exception as e:
                    return f"Tool error: {e}"
        return f"Tool '{tool_name}' not found."
