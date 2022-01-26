import streamlit as st
st.set_page_config(
     page_title='test',
     layout="wide",
     page_icon='🅿',
     initial_sidebar_state="collapsed"#“auto”或“expanded”或“collapsed”
)
if 'str1' not in st.session_state:
    st.session_state.str1 = ''
title = st.text_area('test',height=500)
def increment_counter(title):
    exec(title)
increment = st.button('exec', on_click=increment_counter,
    args=(title, ))

