from datetime import datetime

import streamlit as st
import json
import os  # 新增：导入os模块处理文件名
from utils import memory_utils

"""
1. 读取对话历史，并进行总结，输出精炼记忆
"""
def show():
    st.title("💭Make a life：Memory")

    # 新增：初始化日记内容状态，确保始终存在
    if "diary_content" not in st.session_state:
        st.session_state["diary_content"] = {"content": "", "reasoning_content": ""}
    # 新增：初始化更新结果状态
    if "update_result" not in st.session_state:
        st.session_state["update_result"] = ""
    if "raw_content" not in st.session_state:
        st.session_state["raw_content"] = None

    # 导入文件上传
    uploaded_file = st.file_uploader(
        "上传对话历史",
        type=["json"],
        help="从JSON文件导入对话历史"
    )
    if st.button("导入对话历史"):
        if uploaded_file is not None:
            try:
                # 读取并解析JSON文件
                import_data = json.load(uploaded_file)
                # 验证导入的数据结构
                if "history" in import_data:
                    st.session_state["history"] = import_data["history"]
                    # 新增：保存导入的文件名到session状态
                    st.session_state["imported_filename"] = uploaded_file.name
                    st.success("对话历史导入成功！")
                    st.rerun()
                else:
                    st.error("导入失败！请检查文件格式是否正确。")
            except Exception as e:
                st.error(f"导入失败：{str(e)}")
        else:
            st.warning("请先上传对话历史json文件。")

    # 修改：仅当存在导入文件名和历史记录时才显示日记功能
    if "imported_filename" in st.session_state and "history" in st.session_state and st.session_state["history"]:
        st.subheader("AI 日记生成")
        if st.button("生成日记"):
            with st.spinner("AI正在撰写日记..."):
                # 调用memory_utils.write_diary生成日记
                diary_response = memory_utils.write_diary(st.session_state["history"])
                st.session_state["diary_content"] = diary_response

        # 显示日记内容
        if "diary_content" in st.session_state and st.session_state["diary_content"]:
            st.subheader("生成的日记")
            # 显示思考过程
            if st.session_state["diary_content"].get("reasoning_content"):
                with st.expander("思考过程", expanded=True):
                    st.info(st.session_state["diary_content"]["reasoning_content"])
            st.text_area("日记内容", st.session_state["diary_content"]["content"], height=300)

            # 修改：使用导入的文件名作为日记文件名（替换为txt扩展名）
            base_filename = os.path.splitext(st.session_state["imported_filename"])[0]
            diary_filename = f"diary_{base_filename}.txt"

            # 修改：导出日记内容为纯文本，并使用匹配的文件名
            if st.download_button(
                label="导出日记",
                data=json.dumps(st.session_state["diary_content"], ensure_ascii=False, indent=2),
                file_name=diary_filename,
                mime="text/plain"
            ):
                st.success("日记导出成功！")

    # 新增：AI自我更新功能
    st.subheader("AI自我更新")
    uploaded_config = st.file_uploader("上传设定JSON文件", type=["json"])

    if uploaded_config is not None:
        try:
            # 解析上传的JSON配置文件
            config_data = json.load(uploaded_config)
            st.session_state["original_filename"] = uploaded_config.name

            if st.button("执行自我更新"):
                with st.spinner("AI正在自我更新..."):
                    # 调用self_update函数，传入配置和历史记录
                    update_result = memory_utils.self_update(st.session_state["history"],config_data,st.session_state["diary_content"]["content"])
                    st.session_state["update_result"] = update_result
                    # 显示更新结果（确保是JSON格式）
                    # 新增：清理可能存在的JSON代码块标记
                    raw_content = st.session_state["update_result"]["content"].strip()
                    # 移除开头的```json标记（如果存在）
                    if raw_content.startswith("```json"):
                        raw_content = raw_content[len("```json"):].strip()
                    # 移除结尾的```标记（如果存在）
                    if raw_content.endswith("```"):
                        raw_content = raw_content[:-len("```")].strip()
                    st.session_state["raw_content"] = json.loads(raw_content)
            # 显示推理过程
            if "reasoning_content" in st.session_state["update_result"]:
                with st.expander("更新推理过程", expanded=False):
                    st.info(st.session_state["update_result"]["reasoning_content"])

            if st.session_state["raw_content"]:
                st.json(st.session_state["raw_content"])
                # 新增：保存新设定按钮（原始文件名+时间戳）
                # 获取原始文件名并生成带时间戳的新文件名
                original_filename = st.session_state["original_filename"]
                base_name, ext = os.path.splitext(original_filename)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{base_name}_{timestamp}{ext}"

                # 保存新设定为JSON文件
                st.download_button(
                    label="保存新设定",
                    data=json.dumps(st.session_state["raw_content"], ensure_ascii=False, indent=2),
                    file_name=new_filename,
                    mime="application/json"
                )

        except json.JSONDecodeError:
            st.error("上传的文件不是有效的JSON格式！")

    else:
        # 修改：提示信息更新为需要上传文件
        st.info("请先上传并导入对话历史文件以生成日记")

