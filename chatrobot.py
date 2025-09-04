import streamlit as st
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.request_utils import get_chat_response,get_clean_history

st.title("💭Make a life：ChatRobot")

# 初始化会话状态
if "history" not in st.session_state:
    st.session_state["history"] = [{
        "role": "assistant",
        "content": "我是你的AI助手，有什么可以帮你的吗？",
        "timestamp":datetime.now().strftime("%Y%m%d_%H%M%S")}]

# 显示聊天记录和思考过程
for i, message in enumerate(st.session_state["history"]):
    # 显示搜索结果
    if message.get("search_results"):
        with st.expander("搜索结果", expanded=False):
            # 遍历搜索结果列表
            for idx, result in enumerate(message["search_results"], 1):
                st.markdown(f"#### 搜索结果 {idx}: [{result['title']}]({result['url']})")
                st.caption(f"相关性分数: {result['score']}")
                st.markdown(result["content"])  # 使用Markdown渲染内容
                st.divider()  # 结果间分隔线
    # 显示思考过程
    if message.get("reasoning_content"):
        with st.expander("思考过程", expanded=False):
            st.info(message["reasoning_content"])
    # 显示消息
    st.chat_message(message["role"]).write(message["content"])
    # 只对AI的回答显示token消耗，且确保有对应的token记录
    if message["role"] == "assistant":
        if message.get("token_cost"):
            token_info = message["token_cost"]
            st.caption("tokens消耗: {}, 推理时间: {}秒".format(token_info["total_tokens"],token_info["time_cost"]))

# 聊天组件
prompt = st.chat_input("给AI发送消息")
model = st.selectbox("模型选择", ["Qwen3-8B", "deepseek-R1-Distillation"])
enable_search = st.toggle("联网搜索", value=False)

if prompt:
    # 新增用户消息
    st.session_state["history"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # LLM推理
    with st.spinner("AI思考中..."):
        # AI回答
        start_time = datetime.now()
        # 处理clen_history
        clean_history = get_clean_history(st.session_state["history"])
        response = get_chat_response(clean_history, model, enable_search)
        end_time = datetime.now()
        # 计算推理时间
        think_time = round((end_time - start_time).total_seconds(),2)
        response["time_cost"]=think_time
        # 更新历史
        st.session_state["history"].append(response)
        # 显示search_results
        if response.get("search_results"):
            with st.expander("搜索结果", expanded=True):
                # 遍历搜索结果列表
                for idx, result in enumerate(response["search_results"], 1):
                    st.markdown(f"#### 搜索结果 {idx}: [{result['title']}]({result['url']})")
                    st.caption(f"相关性分数: {result['score']}")
                    st.markdown(result["content"])  # 使用Markdown渲染内容
                    st.divider()  # 结果间分隔线
        # 显示思考过程
        if response.get("reasoning_content"):
            with st.expander("思考过程", expanded=True):
                st.info(response["reasoning_content"])
        # 显示回答
        st.chat_message("assistant").write(response["content"])
        # 显示token消耗
        st.caption("tokens消耗: {}, 推理时间: {}秒".format(response["total_tokens"],think_time))



# # 新增：对话历史导出功能
# col1, col2, col3 = st.columns(3)  # 创建两列布局放置导出和导入按钮
# with col1:
#     if st.button("清除对话历史"):
#         # 清空会话记录，重置messages
#         st.session_state["history"] = [{"role": "assistant", "content": "我是你的AI助手，有什么可以帮你的吗？"}]
#         st.session_state["think_history"] = [None]
#         st.session_state["token_cost"] = [None]
#         st.rerun()
#
# # 对话历史导出
# with col2:
#     # 生成带时间戳的默认文件名
#     default_filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
#     # 将对话历史和思考过程合并为一个字典
#     export_data = {
#         "history": st.session_state["history"],
#         "think_history": st.session_state["think_history"],
#         "token_cost": st.session_state["token_cost"]
#     }
#     # 转换为JSON字符串
#     json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
#     # 导出按钮
#     st.download_button(
#         label="导出对话历史",
#         data=json_data,
#         file_name=default_filename,
#         mime="application/json",
#         help="将当前对话历史导出为JSON文件"
#     )
# # 导入文件上传
# uploaded_file = st.file_uploader(
#     "上传对话历史",
#     type=["json"],
#     help="从JSON文件导入对话历史"
# )
#
# # 导入对话历史
# with col3:
#     if st.button("导入对话历史"):
#         if uploaded_file is not None:
#             try:
#                 # 读取并解析JSON文件
#                 import_data = json.load(uploaded_file)
#                 # 验证导入的数据结构
#                 if "history" in import_data and "think_history" in import_data:
#                     st.session_state["history"] = import_data["history"]
#                     st.session_state["think_history"] = import_data["think_history"]
#                     st.session_state["token_cost"] = import_data["token_cost"]
#                     st.success("对话历史导入成功！")
#                     st.rerun()
#                 else:
#                     st.error("导入失败！请检查文件格式是否正确。")
#             except Exception as e:
#                 st.error(f"导入失败：{str(e)}")
#         else:
#             st.warning("请先上传对话历史json文件。")


