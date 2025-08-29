import requests
import json
import os


def get_chat_response(messages, model="Qwen3-8B"):
    api_key = os.getenv("SILICONFLOW_API_KEY")

    print(messages)
    
    model_map ={
        "Qwen3-8B": r"Qwen/Qwen3-8B",
        "deepseek-R1-Distillation": r"deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
    }
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 构建请求数据，注意模型名称要写对
    data = {
        "model": model_map[model],  # 或你使用的其他GLM3模型名称
        "messages": messages,
        "temperature": 0.5
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 解析响应
    if response.status_code == 200:
        result = response.json()
        reasoning_content = result['choices'][0]['message']['reasoning_content']
        content = result['choices'][0]['message']['content']
        return {"reasoning_content":reasoning_content, "content":content}
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print(f"错误信息：{response.text}")
        return None, None