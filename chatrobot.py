import streamlit as st
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from utils.chatRobot_utils import get_chat_response
from utils.request_utils import get_chat_response

st.title("💭Make a life")

if "history" not in st.session_state:
    st.session_state["history"] = [{"role": "assistant", "content": "我是你的AI助手，有什么可以帮你的吗？"}]
if "token_cost" not in st.session_state:
    st.session_state["token_cost"] = [None]
# 新增思考过程存储
if "think_history" not in st.session_state:
    st.session_state["think_history"] = [None]

# 显示聊天记录和思考过程
for i, message in enumerate(st.session_state["history"]):
    think_content = st.session_state["think_history"][i]
    if think_content:
        with st.expander("思考过程", expanded=False):
            st.info(think_content)
    st.chat_message(message["role"]).write(message["content"])
    # 只对AI的回答显示token消耗，且确保有对应的token记录
    if message["role"] == "assistant":
        token_used = st.session_state["token_cost"][i]
        if token_used is not None:
            st.caption(f"tokens消耗: {token_used}")

prompt = st.chat_input("给AI发送消息")
model = st.selectbox("模型选择", ["Qwen3-8B", "deepseek-R1-Distillation"])
# 添加开关组件
# enable_thinking = st.toggle("开启思考功能", value=False)
if prompt:
    # 新增用户消息
    st.session_state["history"].append({"role": "user", "content": prompt})
    st.session_state["think_history"].append(None)
    st.session_state["token_cost"].append(None)
    st.chat_message("user").write(prompt)
    with st.spinner("AI思考中..."):
        # AI回答
        response = get_chat_response(st.session_state["history"], model)
        think_content = response["reasoning_content"]
        clean_response = response["content"]
        token_cost = response["token_cost"]["total_tokens"]
        # 处理思考过程
        st.session_state["think_history"].append(think_content)
        if think_content:
            with st.expander("思考过程", expanded=True):
                st.info(think_content)
        else:
            clean_response = response
            st.session_state["think_history"].append(None)

        st.session_state["history"].append({"role": "assistant", "content": clean_response})
        st.chat_message("assistant").write(clean_response)
        # 记录token消耗
        st.session_state["token_cost"].append(token_cost)
        st.caption(f"tokens消耗: {token_cost}")



# 新增：对话历史导出功能
col1, col2, col3 = st.columns(3)  # 创建两列布局放置导出和导入按钮
with col1:
    if st.button("清除对话历史"):
        # 清空会话记录，重置messages
        st.session_state["history"] = [{"role": "assistant", "content": "我是你的AI助手，有什么可以帮你的吗？"}]
        st.session_state["think_history"] = [None]
        st.session_state["token_cost"] = [None]
        st.rerun()

# 对话历史导出
with col2:
    # 生成带时间戳的默认文件名
    default_filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    # 将对话历史和思考过程合并为一个字典
    export_data = {
        "history": st.session_state["history"],
        "think_history": st.session_state["think_history"],
        "token_cost": st.session_state["token_cost"]
    }
    # 转换为JSON字符串
    json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
    # 导出按钮
    st.download_button(
        label="导出对话历史",
        data=json_data,
        file_name=default_filename,
        mime="application/json",
        help="将当前对话历史导出为JSON文件"
    )
# 导入文件上传
uploaded_file = st.file_uploader(
    "上传对话历史",
    type=["json"],
    help="从JSON文件导入对话历史"
)

# 导入对话历史
with col3:
    if st.button("导入对话历史"):
        if uploaded_file is not None:
            try:
                # 读取并解析JSON文件
                import_data = json.load(uploaded_file)
                # 验证导入的数据结构
                if "history" in import_data and "think_history" in import_data:
                    st.session_state["history"] = import_data["history"]
                    st.session_state["think_history"] = import_data["think_history"]
                    st.session_state["token_cost"] = import_data["token_cost"]
                    st.success("对话历史导入成功！")
                    st.rerun()
                else:
                    st.error("导入失败！请检查文件格式是否正确。")
            except Exception as e:
                st.error(f"导入失败：{str(e)}")
        else:
            st.warning("请先上传对话历史json文件。")


