"""Streamlit deployment entry point, using the same retrieval core as Gradio."""

from __future__ import annotations

import streamlit as st

# The package uses a src/ layout; this also supports running directly from a
# clean Streamlit Community Cloud checkout before an editable install exists.
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from people.qa import answer_question


st.set_page_config(page_title="PEOPLE｜百家姓名人問答", page_icon="📚")
st.title("PEOPLE｜百家姓名人問答")
st.caption("輸入姓氏或人物名稱，從人物資料集即時查找相關人物與生平。")

with st.form("people_question_form"):
    question = st.text_input("你的問題", placeholder="例如：李姓有哪些人物？或請介紹李白")
    submitted = st.form_submit_button("查詢", type="primary")

if submitted:
    with st.spinner("正在搜尋人物資料…"):
        st.markdown(answer_question(question))

with st.expander("範例問題"):
    st.markdown("- 李姓有哪些人物？\n- 請介紹李白\n- 哪位人物曾推動航天事業？")
