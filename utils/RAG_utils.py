from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# 通过RAG实现记忆

def load_embedding_model():
    # 使用原始字符串指定本地模型路径
    model_path = r"D:\AI_models\Qwen\Qwen3-Embedding-0___6B"

    # 设置模型参数，确保正确加载本地模型
    # model_kwargs = {
    #     "device": "cpu",  # 根据设备情况选择使用 GPU 或 CPU
    #     "trust_remote_code": True  # 允许加载远程代码
    # }

    # 初始化 HuggingFaceEmbeddings
    embeddings_model = HuggingFaceEmbeddings(
        model_name=model_path,
        # model_kwargs=model_kwargs
    )
    return embeddings_model


class RAG:
    def __init__(self):
        documents = self.load_diary()
        self.embeddings_model = load_embedding_model()
        self.all_splits = self.split_documents(documents)
        self.retriever = self.get_retriever(self.all_splits, self.embeddings_model)

    # 将所有日记加载到documents
    def load_diary(self):
        # 定义目录路径和文件匹配模式
        directory_path = "./diaries"  # 替换为你的文本文件目录
        glob_pattern = "*.txt"  # 匹配所有 .txt 文件，可根据需要修改（如 "**/*.txt" 递归子目录）

        # 创建 DirectoryLoader，使用 TextLoader 加载每个文件
        loader = DirectoryLoader(
            path=directory_path,
            glob=glob_pattern,
            loader_cls=TextLoader,  # 指定单个文件加载器为 TextLoader
            loader_kwargs={"encoding": "utf-8"}  # 可选：指定文件编码（解决中文乱码等问题）
        )

        # 加载所有文件并返回文档列表
        documents = loader.load()

        # 查看加载结果（例如打印文档数量和内容预览）
        print(f"成功加载 {len(documents)} 个文件")
        # for doc in documents[:2]:  # 打印前2个文档的信息
        #     print(f"\n文件路径: {doc.metadata['source']}")
        #     print(f"内容预览: {doc.page_content[:100]}...")  # 打印前100字符
        return documents

    def split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=20,
            separators=[",", "\n\n", "\n", "。", "！", "？", "，", "、", ""]
        )
        all_splits = text_splitter.split_documents(documents)
        return all_splits

    def get_retriever(self, all_splits, embeddings_model):
        db = FAISS.from_documents(all_splits, embeddings_model)
        retriever = db.as_retriever()
        return retriever

    def Faiss_search(self, query, max_results=3):
        docs = self.retriever.invoke(query)
        print(f"检索到{len(docs)}条记忆：")
        print(docs)

        return [doc.page_content for doc in docs[:max_results]]

if __name__ == "__main__":
    rag = RAG()
    results=rag.Faiss_search("爱丽丝与A的故事")
    print(results)