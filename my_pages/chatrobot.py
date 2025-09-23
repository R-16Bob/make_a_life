import streamlit as st
import sys
import os
import json
from datetime import datetime

# 添加用于管理初始提示词的目录
INIT_PROMPTS_DIR = "init_prompts"
if not os.path.exists(INIT_PROMPTS_DIR):
    os.makedirs(INIT_PROMPTS_DIR)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.request_utils import get_chat_response,get_clean_history

def show():
    st.title("💬Make a life：ChatRobot")

    # 初始化会话状态
    if "history" not in st.session_state:
        st.session_state["history"] = [{
            "role": "assistant",
            "content": "我是你的AI助手，有什么可以帮你的吗？",
            "timestamp":datetime.now().strftime("%Y%m%d_%H%M%S")}]

    # 新增：配置初始提示词侧边栏
    with st.sidebar:
        st.header("初始提示词设置")
        # 加载并立即清理临时状态
        # temp_role = st.session_state.get("temp_role", None)
        temp_content = st.session_state.get("temp_content", None)
        # # 确定默认角色
        # if temp_role is not None:
        #     default_role = temp_role
        # else:
        #     default_role = st.session_state["history"][0]["role"]

        # st.session_state["index"] = 0 if default_role == "system" else 1

        # 确定默认内容
        if temp_content is not None:
            default_content = temp_content
        else:
            default_content = st.session_state["history"][0]["content"]

        # 角色选择
        if st.session_state.get("init_prompt_role") is None:
            init_role = st.radio(
                "选择初始提示词角色",
                ["system", "assistant"],
                index=0,
            )
        else:
            init_role = st.radio(
                "选择初始提示词角色",
                ["system", "assistant"],
                index=st.session_state["index"]
            )

        # 初始提示词文本框
        init_content = st.text_area(
            "初始提示词内容",
            value=default_content,
            height=200,
            # key="init_prompt_content"
        )

        # 已保存提示词下拉框
        st.subheader("保存的提示词")
        saved_files = [f for f in os.listdir(INIT_PROMPTS_DIR) if f.endswith(".json")]
        selected_file = st.selectbox(
            "选择已保存的提示词",
            [""] + saved_files,  # 列表第一位为空，用于添加自定义提示词
            index=0
        )

        # 加载选中的提示词
        if selected_file:
            if st.button("加载选中的提示词"):
                with open(os.path.join(INIT_PROMPTS_DIR, selected_file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    st.session_state["temp_role"] = data["role"]
                    st.session_state["temp_content"] = data["content"]
                    st.rerun()

        # 保存当前提示词
        save_name = st.text_input("保存名称", "default_prompt")
        col_save, col_apply = st.columns(2)

        with col_save:
            if st.button("保存当前配置"):
                prompt_data = {
                    "role": init_role,
                    "content": init_content
                }
                file_path = os.path.join(INIT_PROMPTS_DIR, f"{save_name}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(prompt_data, f, ensure_ascii=False, indent=2)
                st.success(f"配置已保存到 {file_path}")

        with col_apply:
            if st.button("应用到对话", type="primary"):
                # 更新历史记录中的第一条消息
                st.session_state["history"][0] = {
                    "role": init_role,
                    "content": init_content,
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
                }
                st.success("初始提示词已更新！")
                st.rerun()

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
            if message.get("total_tokens") and message.get("time_cost"):
                st.caption("tokens消耗: {}, 推理时间: {}秒".format(message["total_tokens"],message["time_cost"]))

    # 聊天组件
    prompt = st.chat_input("给AI发送消息")
    model = st.selectbox("模型选择", ["Qwen3-8B", "deepseek-R1-Distillation"], index=1)
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



    # 新增：对话历史导出功能
    col1, col2, col3 = st.columns(3)  # 创建两列布局放置导出和导入按钮
    with col1:
        if st.button("清除对话历史"):
            # 清空会话记录，重置messages
            st.session_state["history"] = [{
                "role": "assistant",
                "content": "我是你的AI助手，有什么可以帮你的吗？",
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")}]
            st.rerun()

    # 对话历史导出
    with col2:
        # 生成带时间戳的默认文件名
        default_filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_data = {
            "history": st.session_state["history"],
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
                    if "history" in import_data:
                        st.session_state["history"] = import_data["history"]
                        st.success("对话历史导入成功！")
                        st.rerun()
                    else:
                        st.error("导入失败！请检查文件格式是否正确。")
                except Exception as e:
                    st.error(f"导入失败：{str(e)}")
            else:
                st.warning("请先上传对话历史json文件。")


