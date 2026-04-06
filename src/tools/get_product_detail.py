import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.tools.init_db import get_connection

def get_product_detail(product_id: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"Không tìm thấy sản phẩm với id '{product_id}'"

    id, name, category, price, stock, specs = row
    stock_status = f"Còn {stock} sản phẩm" if stock > 0 else "Hết hàng"
    return (
        f"Tên: {name}\n"
        f"Danh mục: {category}\n"
        f"Giá: {price:,}đ\n"
        f"Thông số: {specs}\n"
        f"Tồn kho: {stock_status}"
    )

TOOL_SPEC = {
    "name": "get_product_detail",
    "description": "Xem thông tin chi tiết một sản phẩm theo ID. Input: product_id, ví dụ 'p001'.",
    "func": get_product_detail
}

from src.core.azure_provider import AzureOpenAIProvider
from src.agent.agent import ReActAgent
from dotenv import load_dotenv
import os
load_dotenv()

llm = AzureOpenAIProvider(
    model_name="gpt-4o",
    api_key= os.getenv('GithubAPI'),
    base_url="https://models.inference.ai.azure.com/"
)

# Your OpenAI-format tool list (unchanged)
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_product_detail",
            "description": "Xem thông tin chi tiết một sản phẩm theo ID, bao gồm tên, danh mục, giá, thông số kỹ thuật và tình trạng tồn kho.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID của sản phẩm cần xem. Ví dụ: 'p001', 'p042'"
                    }
                },
                "required": ["product_id"]
            }
        }
    }
]

# Map name → Python function
fn_map = {
    "get_product_detail": get_product_detail,
}
# --- Adapter: wrap OpenAI tool schema into ReAct format ---
def openai_tools_to_react(openai_tools: list, fn_map: dict) -> list:
    """
    openai_tools : your existing `tools` list (OpenAI JSON schema)
    fn_map       : { "tool_name": callable }
    """
    react_tools = []
    for t in openai_tools:
        fn_def = t["function"]
        name = fn_def["name"]
        react_tools.append({
            "name": name,
            "description": fn_def["description"],
            "parameters": fn_def["parameters"],   # kept for reference
            "fn": fn_map[name]                     # actual Python callable
        })
    return react_tools

react_tools = openai_tools_to_react(openai_tools, fn_map)
agent = ReActAgent(llm=llm, tools=react_tools, max_steps=3)
user_query = "Cho tôi biết thông tin chi tiết về sản phẩm có ID là p001."
final_answer = agent.run(user_query)
print(final_answer)