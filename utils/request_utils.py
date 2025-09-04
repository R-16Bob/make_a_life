import requests
import json
import os
import copy
from datetime import datetime

def get_chat_response(messages, model="Qwen3-8B", enable_search=False):
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
    # 如果支持联网搜索，就先进行搜索，再修改prompt提供搜索结果。
    if enable_search:
        from utils.agent_utils import tavily_search
        search_resutls = tavily_search(messages[-1]["content"])["results"]
        result = json.dumps(search_resutls, ensure_ascii=False)
        # 更新messages，引用将同时修改session.state
        messages_copy = copy.deepcopy(messages)
        messages_copy[-1]["content"] = messages[-1]["content"]+"\n请根据以下检索的网页内容进行回答："+result
        # 构建请求数据，注意模型名称要写对
        data = {
            "model": model_map[model],  # 或你使用的其他GLM3模型名称
            "messages": messages_copy,
            "temperature": 0.5
        }
    else:
        data = {
            "model": model_map[model],  # 或你使用的其他GLM3模型名称
            "messages": messages,
            "temperature": 0.5
        }
    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 解析响应
    if response.status_code == 200:
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = response.json()
        reasoning_content = result['choices'][0]['message']['reasoning_content']

        content = result['choices'][0]['message']['content']
        # 记录tokens消耗
        # prompt_tokens = result["usage"]["prompt_tokens"]
        # completion_tokens = result["usage"]["completion_tokens"]
        total_tokens = result["usage"]["total_tokens"]
        # token_cost = {
        #     "prompt_tokens": prompt_tokens,
        #     "completion_tokens": completion_tokens,
        #     "total_tokens": total_tokens
        # }
        return_dict = {
            "role": "assistant",
            "timestamp": timestamp,
            "reasoning_content": reasoning_content,
            "content": content,
            "total_tokens": total_tokens
        }
        if enable_search:
            return_dict["search_results"] = search_resutls
        return return_dict
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print(f"错误信息：{response.text}")
        return None, None

def get_clean_history(history):
    clean_history = []
    for message in history:
        clean_history.append({'role':message["role"],'content':message["content"]})
    return clean_history
