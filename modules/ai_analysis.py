import streamlit as st
import pandas as pd
import sqlalchemy as sa
import os
from google import genai
from database import engine, employees, departments, positions

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def show():

    st.header("🧠 AI Phân tích nhân sự")

    # ==========================
    # LOAD DATA
    # ==========================

    with engine.connect() as conn:

        emp = pd.read_sql(sa.select(employees), conn)
        dep = pd.read_sql(sa.select(departments), conn)
        pos = pd.read_sql(sa.select(positions), conn)

    if emp.empty:
        st.warning("Chưa có dữ liệu nhân viên")
        return

    # ==========================
    # JOIN DATA
    # ==========================

    emp = emp.merge(dep, left_on="department_id", right_on="id", how="left")
    emp = emp.merge(pos, left_on="position_id", right_on="id", how="left")

    emp = emp.rename(columns={
        "name_x": "Tên nhân viên",
        "salary": "Lương",
        "name_y": "Phòng ban",
        "name": "Vị trí"
    })

    # chỉ lấy dữ liệu cần thiết
    emp_data = emp[
        [
            "Tên nhân viên",
            "Phòng ban",
            "Vị trí",
            "Lương"
        ]
    ].head(200)

    # ==========================
    # BUTTON AI
    # ==========================

    if st.button("🤖 Phân tích nhân sự bằng AI"):

        prompt = f"""
Bạn là chuyên gia quản trị nhân sự của công ty SanCo.

Dựa vào dữ liệu nhân viên bên dưới hãy phân tích.

YÊU CẦU:
- Trả lời bằng tiếng Việt
- Trình bày rõ ràng
- Viết dạng báo cáo

DỮ LIỆU:

{emp_data.to_string(index=False)}

HÃY PHÂN TÍCH:

1. Tổng quan nhân sự
2. Phòng ban có nhiều nhân viên nhất
3. Phòng ban có ít nhân viên nhất
4. Phân tích mức lương
5. Đề xuất cải thiện quản lý nhân sự
"""

        # ==========================
        # AI PROCESS
        # ==========================

        with st.spinner("AI đang phân tích dữ liệu nhân sự..."):

            try:

                response = client.models.generate_content(
                    model="models/gemini-3-flash-preview",
                    contents=prompt
                )

                result = response.text

            except Exception as e:

                result = f"Lỗi AI: {str(e)}"

        # ==========================
        # HIỂN THỊ BÁO CÁO
        # ==========================

        st.subheader("📊 Báo cáo phân tích nhân sự")

        st.markdown(result)