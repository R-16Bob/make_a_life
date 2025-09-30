# 用于操作milvus数据库
from pymilvus import MilvusClient

class MilvusDB:
    def __init__(self):
        # 连接milvus数据库，默认数据库为aoi_memories
        self.client = MilvusClient("http://localhost:19530")
        self.db_name = "aoi_memories"
        self.client.use_database(db_name=self.db_name)

    def insert_data(self, collection_name, data):
        print(self.client.insert(collection_name=collection_name, data=data))

    def search_data(self, collection_name, query, max_results=3):
        search_res = self.client.search(
            collection_name=collection_name,
            data=query,
            limit=max_results,
            output_fields=["id", "text", "timestamp"]
        )
        print("检索结果")
        print(search_res)
        return [res['entity']['text'] for res in search_res[0]]

if __name__ == "__main__":
    db = MilvusDB()
    # 插入日记数据
    # from RAG_utils import load_all_diaries
    # data = load_all_diaries()
    # print(data)
    # print(type(data[0]["text"]))
    # db.insert_data(collection_name="diaries", data=data)
    # 搜索测试
    res = db.search_data(collection_name="diaries", query=['朋友A'])
    print(res)

