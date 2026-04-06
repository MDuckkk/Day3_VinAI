# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Trần Thanh Nguyên]
- **Student ID**: [2A202600311]
- **Date**: [06/04/2026]

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: src/tools/get_product_detail.py, src/agent/agent.py, src/core/azure_provider.py
- **Code Highlights**: src/core/azure_provider.py — bridged the Azure OpenAI endpoint into the LLMProvider interface:
self.client = OpenAI(
    base_url="https://models.inference.ai.azure.com/",
    api_key=api_key
)
src/agent/agent.py — implemented the core ReAct loop with regex-based action parsing:
action_match = re.search(r"Action:\s*(\w+)\(([^)]*)\)", response_text)
if action_match:
    tool_name = action_match.group(1).strip()
    observation = self._execute_tool(tool_name, tool_args)
    conversation += f"Observation: {observation}\n"
- **Documentation**: Documentation: The agent maintains a running conversation string that accumulates Thought/Action/Observation turns. Each iteration feeds this full context back to the LLM, so the model can reason over previous observations before deciding the next action. The loop terminates when the LLM produces a Final Answer: token or max_steps is reached.

---

II. Debugging Case Study (10 Points)

Analyze a specific failure event you encountered during the lab using the logging system.

Problem Description:
During testing, the ReAct agent failed to correctly execute tasks that required multiple tool calls within a single reasoning step.

For example, with input:

Calculate tax for 500 dollars in US, then search for OpenAI

The LLM generated:

Thought: I need to compute tax and then search for information
Action: calc_tax(500, US)
Action: search_api(OpenAI)

However, the agent only executed the first tool (calc_tax) and ignored the second action. This resulted in incomplete reasoning and incorrect final answers.

Log Source:

Example log output:

LLM_RESPONSE (step=0):
Thought: I need to compute tax and then search for information
Action: calc_tax(500, US)
Action: search_api(OpenAI)

TOOL_CALL: calc_tax(500, US)
TOOL_RESULT: 50.0

# Missing TOOL_CALL for search_api
Diagnosis:
The issue was caused by the action parsing logic in the agent. Initially, the code used:
action_match = re.search(r"Action:\s*(\w+)\(([^)]*)\)", response_text)

This approach only captures the first occurrence of an Action: pattern in the LLM response.

As a result:

Additional actions were ignored
The agent failed to execute all required tools
The reasoning loop became incomplete

The problem was not due to the LLM itself, but due to a design limitation in the parser, which assumed only one tool call per step.

Solution:
The parser was updated to support multiple actions per step using re.findall:
action_matches = re.findall(
    r"Action:\s*(\w+)\(([^)]*)\)",
    response_text
)

for tool_name, tool_args in action_matches:
    observation = self._execute_tool(tool_name, tool_args)
    conversation += f"Observation: {observation}\n"

Additionally:

The system prompt was modified to explicitly allow multiple Action: lines per step
Each tool call is now executed sequentially within the same iteration
Observations from all tools are appended back into the conversation context

After applying this fix, the agent correctly handled multi-step tasks and produced complete, accurate results.

III. Personal Insights: Chatbot vs ReAct (10 Points)

Reflect on the reasoning capability difference.

Reasoning:
The Thought block significantly improves transparency and structured reasoning compared to a direct Chatbot response. Instead of producing a single final answer, the agent explicitly breaks down the problem into intermediate steps (Thought → Action → Observation).

In my implementation, this allowed the model to:

Plan multi-step tasks (e.g., calculate tax → then search information)
Use external tools in a controlled and interpretable way
Maintain a reasoning trace that can be debugged through logs

In contrast, a standard Chatbot would attempt to answer everything in one step, often hallucinating results instead of using tools.

Reliability:
The ReAct agent can perform worse than a Chatbot in several scenarios:
When the LLM generates incorrect or malformed Action: syntax, causing parsing failures
When the agent enters a loop due to missing or unclear Final Answer signals
When tool outputs are simple but the agent over-reasons, leading to unnecessary steps

For example, before fixing the parser, the agent failed to execute multiple tool calls in one step, producing incomplete results. In such cases, a direct Chatbot might still return a plausible (though not tool-grounded) answer.

Observation:
The Observation (tool output) plays a critical role in guiding the next reasoning step.

In my implementation:

Each tool result is appended back into the conversation context
The LLM uses this new information to decide the next action or produce a final answer

For example:

After calc_tax returns 50.0, the agent uses that result to proceed with search_api
The environment feedback prevents hallucination and anchors reasoning in real outputs

This creates a feedback loop where the agent dynamically adapts based on external information, which is not possible in a standard Chatbot.

IV. Future Improvements (5 Points)

How would you scale this for a production-level AI agent system?

Scalability:
Implement an asynchronous execution layer for tool calls, allowing multiple tools to run in parallel instead of sequentially. This is especially important when dealing with APIs or slow external services. Additionally, a task queue (e.g., message queue) can help distribute workloads across multiple workers.
Safety:
Introduce a Supervisor LLM or validation layer to review generated Action: steps before execution. This can prevent:
Invalid tool usage
Harmful or unintended actions
Incorrect parameter formats

Input/output validation and tool whitelisting should also be enforced.

Performance:
Use a vector database (e.g., FAISS, Pinecone) to dynamically select relevant tools or context instead of passing all tools in every prompt.

Other improvements include:

Caching tool results to avoid repeated calls
Reducing prompt size by summarizing conversation history
Optimizing parsing logic for faster execution

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
