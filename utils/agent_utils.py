from tavily import TavilyClient
import os

# 使用TavilySearch进行网上检索
def tavily_search(query, max_results=2):
    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    response = client.search(query=query,max_results=max_results)
    print(response)
    return response

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