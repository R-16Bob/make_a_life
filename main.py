import streamlit as st
from my_pages import chatrobot, memory
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'chatrobot'

cols = st.columns(2)
with cols[0]:
    if st.button("💬 前往聊天"):
        st.session_state['current_page'] = 'chatrobot'
with cols[1]:
    if st.button("📄 前往记忆管理"):
        st.session_state['current_page'] = 'memory'
st.markdown('---')

# 动态加载页面
if st.session_state.current_page == 'chatrobot':
    chatrobot.show()
elif st.session_state.current_page == 'memory':
    memory.show()

