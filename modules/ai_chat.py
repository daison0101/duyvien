import streamlit as st
import pandas as pd
import sqlalchemy as sa
import os
from google import genai
from database import engine, employees, departments, positions

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def show():

    st.header("🤖 AI Chat HR")

    # =============================
    # LƯU LỊCH SỬ CHAT
    # =============================

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # =============================
    # HIỂN THỊ CHAT
    # =============================

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # =============================
    # INPUT
    # =============================

    question = st.chat_input("Hỏi về nhân sự...")

    if question:

        # hiển thị user message
        st.chat_message("user").write(question)

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        # =============================
        # LOAD DATA
        # =============================

        with engine.connect() as conn:

            emp = pd.read_sql(sa.select(employees), conn)
            dep = pd.read_sql(sa.select(departments), conn)
            pos = pd.read_sql(sa.select(positions), conn)

        if not emp.empty:
            emp = emp.merge(dep, left_on="department_id", right_on="id", how="left")
            emp = emp.merge(pos, left_on="position_id", right_on="id", how="left")

        emp = emp.rename(columns={
            "name_x": "Tên nhân viên",
            "salary": "Lương",
            "name_y": "Phòng ban",
            "name": "Vị trí"
        })

        emp_data = emp[[
            "Tên nhân viên",
            "Phòng ban",
            "Vị trí",
            "Lương"
        ]].head(100)

        # =============================
        # PROMPT AI
        # =============================

        prompt = f"""
Bạn là trợ lý AI quản lý nhân sự của công ty SanCo.

NHIỆM VỤ:
- Trả lời câu hỏi liên quan đến nhân sự.
- Trả lời ngắn gọn.
- Sử dụng dữ liệu bên dưới.

DỮ LIỆU NHÂN VIÊN:

{emp_data.to_string(index=False)}

CÂU HỎI:
{question}

TRẢ LỜI:
"""

        # =============================
        # AI TRẢ LỜI
        # =============================

        with st.spinner("AI đang phân tích dữ liệu..."):

            try:

                response = client.models.generate_content(
                    model="models/gemini-3-flash-preview",
                    contents=prompt
                )

                answer = response.text

            except Exception as e:

                answer = f"Lỗi AI: {str(e)}"

        # =============================
        # HIỂN THỊ AI
        # =============================

        st.chat_message("assistant").write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })