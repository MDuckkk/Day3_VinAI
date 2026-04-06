# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyen Phan Tuan Anh
- **Student ID**: 2A202600403
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implemented**: `check_inventory`, `web_search_product`, `read_web_page`, `get_product_detail`, `compare_product`, `search_product`
- **Code Highlights**:
	1. Designed and implemented the complete codebase for both modes: direct Chatbot and ReAct Agent.
	2. Built a clean tool architecture where each tool is isolated by function (search, detail retrieval, comparison, inventory check, and web grounding), making the system easy to maintain and extend.
	3. Implemented end-to-end ReAct execution flow support: model reasoning output is parsed into actions, actions are mapped to the correct tool, tool outputs are returned as observations, and the next reasoning step uses those observations.
	4. Added robust handling for invalid tool calls and noisy model outputs (e.g., malformed action format or missing arguments), reducing crashes and improving answer reliability.
	5. Integrated logging and telemetry hooks so agent behavior can be audited step-by-step during debugging and evaluation.
	6. Structured the project into reusable modules (`agent`, `core`, `tools`, `telemetry`) to separate concerns and support faster testing/iteration.
- **Documentation**: My tools are invoked by the ReAct loop after the model emits an `Action`. Each tool returns a structured observation (product facts, inventory status, or web evidence), and that observation is injected back into the next reasoning turn (`Thought`) so the agent can refine or finalize its answer based on real tool feedback instead of pure generation.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: The model produced an incorrect conclusion and remained overconfident even after follow-up prompts challenged the answer.
- **Log Source**: `bug.log`
- **Diagnosis**: The failure likely came from outdated model knowledge. I used `gemini-2.5-pro`, whose effective knowledge did not reliably cover the iPhone 16 Pro Max at the time of testing, so the model kept reinforcing a wrong assumption.
- **Solution**: I switched to a newer model (`Gemma 4`), then re-ran the same prompt flow. The updated model handled the case more accurately and reduced this failure pattern.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: The `Thought` block enables explicit reasoning steps, allowing the model to break complex questions into sub-goals (e.g., "search for product" → "check inventory" → "compare options"). This mirrors human problem-solving better than a direct Chatbot, which attempts to answer in one shot without intermediate reasoning, leading to fewer hallucinations and more grounded responses.
2.  **Reliability**: The ReAct Agent underperformed a direct Chatbot when queries required real-time or speculative information not available through tools. For instance, a Chatbot could directly apologize and explain "I don't have up-to-date info," whereas the Agent would loop through tool calls, waste tokens, and eventually fail or time out. The extra reasoning overhead also introduced failure modes—e.g., malformed action syntax or incorrect tool name—where a Chatbot would gracefully decline to respond.
3.  **Observation**: Observations were crucial to coherent multi-step behavior. When a tool returned unexpected results (e.g., a search returned no products), the agent's next `Thought` would see that observation and adapt—either retry with different keywords or escalate to a web search. Without this feedback loop, the agent would blindly repeat the same failed action. Well-formatted observations kept reasoning paths aligned; noisy or missing observations caused the agent to hallucinate or diverge entirely.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Convert the synchronous ReAct loop to async/await with a request queue (e.g., FastAPI + Celery). Currently, each user request blocks for 5–15 seconds while tools execute sequentially; async would allow interleaving multiple query executions and parallel tool dispatch. For high concurrency, add connection pooling for database and API calls (currently opens a fresh connection per tool invocation), and implement request batching for LLM calls.

- **Safety**: (1) Harden the action parser—replace regex-based extraction with a structured format (JSON or YAML) to prevent injection and argument confusion; (2) Add input sanitization and validation layers before tool execution to block SQL injection and prompt-injection attempts; (3) Implement token budget tracking and hard limits to prevent API quota exhaustion and runaway costs; (4) Build a "supervisor" audit layer that logs all tool calls and validates them against a safety policy (e.g., reject searches for sensitive terms, cap tool call counts per query).

- **Performance**: (1) Cache query results and tool outputs using a vector database or Redis to avoid redundant calls; (2) Implement scratchpad summarization—the current full-history approach balloons tokens quadratically; replace with a rolling summary of the last N steps or use a vector store for relevant history retrieval; (3) Optimize LLM provider integration by using batch APIs and reducing system prompt overhead. Profile and measure latency at each step to identify the actual bottleneck (model inference, tool execution, or I/O).

---

Link to the group assignment can be found here [https://github.com/MDuckkk/Day3_VinAI]