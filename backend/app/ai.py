import os
import requests

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = """
你是一名专门帮助考研学生的 AI 助手。
你的任务是：
1. 解答考研相关问题（数学、英语、政治、专业课、规划）
2. 语气冷静、鼓励、务实
3. 给出可执行建议，而不是空话
4. 如果问题偏离考研主题，可以简单回答后拉回到考研学习上
"""

def chat_with_ai(user_message: str) -> str:
    if not API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"]

def chat_with_ai_history(history: list[dict]) -> str:
    """
    history: [{"role":"user"|"assistant", "content":"..."}]
    """
    if not API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    # 你自己的系统提示词永远放最前面
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
