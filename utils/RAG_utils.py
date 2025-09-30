from glob import glob
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# from langchain_community.vectorstores import FAISS
# 通过RAG实现记忆


# class RAG:
#     def __init__(self):
#         documents = self.load_diary()
#         # self.embeddings_model = load_embedding_model()
#         self.all_splits = self.split_documents(documents)
#         # self.retriever = self.get_retriever(self.all_splits, self.embeddings_model)
#
#     # 将所有日记加载到documents
#     def load_diary(self):
#         # 定义目录路径和文件匹配模式
#         directory_path = "./diaries"  # 替换为你的文本文件目录
#         glob_pattern = "*.txt"  # 匹配所有 .txt 文件，可根据需要修改（如 "**/*.txt" 递归子目录）
#
#         # 创建 DirectoryLoader，使用 TextLoader 加载每个文件
#         loader = DirectoryLoader(
#             path=directory_path,
#             glob=glob_pattern,
#             loader_cls=TextLoader,  # 指定单个文件加载器为 TextLoader
#             loader_kwargs={"encoding": "utf-8"}  # 可选：指定文件编码（解决中文乱码等问题）
#         )
#
#         # 加载所有文件并返回文档列表
#         documents = loader.load()
#
#         # 查看加载结果（例如打印文档数量和内容预览）
#         print(f"成功加载 {len(documents)} 个文件")
#         # for doc in documents[:2]:  # 打印前2个文档的信息
#         #     print(f"\n文件路径: {doc.metadata['source']}")
#         #     print(f"内容预览: {doc.page_content[:100]}...")  # 打印前100字符
#         return documents
#
#     def split_documents(self, documents):
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=300,
#             chunk_overlap=20,
#             separators=[",", "\n\n", "\n", "。", "！", "？", "，", "、", ""]
#         )
#         all_splits = text_splitter.split_documents(documents)
#         return all_splits
#
#     def get_retriever(self, all_splits, embeddings_model):
#         db = FAISS.from_documents(all_splits, embeddings_model)
#         retriever = db.as_retriever()
#         return retriever
#
#     def Faiss_search(self, query, max_results=3):
#         docs = self.retriever.invoke(query)
#         print(f"检索到{len(docs)}条记忆：")
#         print(docs)
#
#         return [doc.page_content for doc in docs[:max_results]]

def get_diary_path():
    # 获取所有日记文件路径
    diary_files = glob("./diaries/*.txt")
    print(f"找到{len(diary_files)}个日记文件")
    return diary_files
def read_diary(diary_path):
    with open(diary_path, "r", encoding="utf-8") as f:
        content = f.read()
        # 解析JSON字符串
        diary_data = json.loads(content)
        timestamp = int(diary_data["timestamp"])
        content = Document(page_content=diary_data["content"], metadata={})
    return {"timestamp": timestamp, "content": content}
def load_all_diaries():
    diary_files = get_diary_path()
    all_diaries = []
    for diary_file in diary_files:
        diary_data = read_diary(diary_file)
        splits = split_content(diary_data["content"])
        for split in splits:
            all_diaries.append({"timestamp": diary_data["timestamp"], "text": split.page_content})
    return all_diaries

def split_content(content):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=20,
        separators=[",", "\n\n", "\n", "。", "！", "？", "，", "、", ""]
    )
    all_splits = text_splitter.split_documents([content])
    return all_splits

if __name__ == "__main__":
    print(load_all_diaries())