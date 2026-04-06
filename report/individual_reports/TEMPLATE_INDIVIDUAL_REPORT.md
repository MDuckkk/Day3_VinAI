# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Vũ Văn Huân]
- **Student ID**: [2A202600348]
- **Date**: [06/05/2026]

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- Em đã refactor toàn bộ Day 3 để chuyển từ local LLM (llama-cpp-python) sang kiến trúc OpenAI-compatible API sử dụng GitHub Models, đồng thời giữ tính linh hoạt multi-provider.

- **Modules Implementated**: [e.g., `src/tools/search_tool.py`]

src/core/openai_provider.py
src/core/local_provider.py (refactor thành optional dependency)
chat.py
run_demo.py
.env.example, QUICKSTART.md, README.md

- **Code Highlights**: [Copy snippets or link file lines]
# chat.py / run_demo.py

api_key = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")

if not api_key or api_key in {"your_github_token_here", "your_openai_api_key_here"}:
    print("❌ Error: Please set GITHUB_TOKEN (or OPENAI_API_KEY) in the .env file.")
    return

llm = OpenAIProvider(model_name=model_name, api_key=api_key)

- **Documentation**: [Brief explanation of how your code interacts with the ReAct loop]
- Em đã refactor hệ thống provider để sử dụng OpenAI-compatible API thông qua GitHub Models (GITHUB_TOKEN) thay cho local model mặc định.
---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: [e.g., Agent caught in an infinite loop with `Action: search(None)`]
Hệ thống bị crash khi chạy do thiếu llama-cpp-python, mặc dù người dùng chỉ muốn dùng provider openai.

- **Log Source**: [Link or snippet from `logs/YYYY-MM-DD.log`]

ImportError: No module named 'llama_cpp' 

- **Diagnosis**: [Why did the LLM do this? Was it the prompt, the model, or the tool spec?]

Nguyên nhân là do local_provider.py được import trực tiếp và trở thành hard dependency, khiến toàn bộ hệ thống fail ngay cả khi không sử dụng local model.

Đây là lỗi thiết kế (architecture issue), không phải lỗi của LLM hay prompt.

- **Solution**: [How did you fix it? (e.g., updated `Thought` examples in the system prompt)]

Chuyển llama-cpp-python thành dependency tùy chọn:

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?

ReAct Agent sử dụng Thought → Action → Observation giúp chia nhỏ quá trình suy luận.
So với Chatbot (trả lời trực tiếp)
Lập kế hoạch từng bước
Gọi tool khi cần
Điều chỉnh dựa trên kết quả trung gian

2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?

Tool trả dữ liệu không chính xác
Prompt chưa đủ rõ → chọn sai action
Vòng lặp reasoning quá dài → dễ bị loop hoặc hallucination

3.  **Observation**: How did the environment feedback (observations) influence the next steps?

Observation là yếu tố quyết định vì nó cung cấp feedback từ environment.
Agent sử dụng observation để:

Cập nhật trạng thái suy nghĩ (Thought)
Quyết định action tiếp theo

👉 Nếu observation sai → toàn bộ chuỗi reasoning bị sai theo.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: [e.g., Use an asynchronous queue for tool calls]
Sử dụng kiến trúc async (queue hoặc event-driven) để xử lý nhiều tool calls song song.

- **Safety**: [e.g., Implement a 'Supervisor' LLM to audit the agent's actions]

Thêm một “Supervisor Agent” để kiểm tra:
Action có hợp lệ không
Output có an toàn không

- **Performance**: [e.g., Vector DB for tool retrieval in a many-tool system]
Tích hợp Vector Database để truy xuất tool hiệu quả
Cache kết quả tool để giảm latency

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
