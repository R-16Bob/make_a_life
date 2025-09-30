import json

from tavily import TavilyClient
import os


# 使用TavilySearch进行网上检索
def tavily_search(query, max_results=2):
    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    response = client.search(query=query,max_results=max_results)
    print(response)
    return response

def recall(collection_name, query, max_results=3):
    print(f"正在回忆{query}相关记忆...")
    import streamlit as st
    results = st.session_state["db"].search_data(collection_name="diaries", query=[query], max_results=max_results)
    return results

# 调用工具
def call_tools(name,arguments):
    allowed = {'tavily_search':tavily_search, 'recall':recall}
    print(f"尝试调用工具：{name}，参数：{arguments}")
    if name in allowed:
        arguments = json.loads(arguments)
        return allowed[name](**(arguments))
    else:
        raise ValueError(f"Unknown tool {name}")

recall_tool = {
    'type':'function',
    'function':{
        'name':'recall',
        'description': '用于从历史记忆中检索相关内容，当需要回忆对话历史时调用',
        'parameters':{
            'type':'object',
            'properties':{
                'collection_name':{
                    'type':'str',
                    'description':'记忆库名称，默认为"diaries"，即你的日记本'
                },
                'query':{
                    'type':'str',
                    'description':'检索内容，应该为关键词或者一句简短的话'
                },
                'max_results':{
                    'type':'int',
                    'description':"最大检索结果，为可选参数，默认为3。"
                }
            },
            'required':['collection_name','query']
        }
    }}
# 我发现让LLM生成检索参数还不如直接用Prompt检索再让LLM根据检索内容生成回答，因此这个东西废弃了。
tavily_tool = {
    'type':'function',
    'function':{
        'name':'tavily_search',
        'description':'用于根据检索关键词或句子搜索互联网相关内容，当需要互联网上的知识时调用。',
        'parameters':{
            'type':'object',
            'properties':{
                'query':{
                    'type':'str',
                    'description':'检索内容，应该为关键词或者一句简短的话'
                },
                'max_results':{
                    'type':'int',
                    'description':"最大检索结果，为可选参数，默认为2。"
                }
            },
            'required':['query']
        }
    }
}

if __name__ == "__main__":
    res = tavily_search("Z-library即将只支持付费会员访问，这是真的吗？")
    print(res)