from langchain.document_loaders import DirectoryLoader, TextLoader
# 通过RAG实现记忆

# 将所有日记加载到documents
def load_diary():
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

if __name__ == "__main__":
    documents = load_diary()
    print(documents)
