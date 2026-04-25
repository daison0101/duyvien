import streamlit as st
import pandas as pd
import plotly.express as px
import sqlalchemy as sa
from database import engine, employees, departments, positions

def show():

    st.header("📊 Dashboard quản lý nhân sự")

    conn = engine.connect()

    emp = pd.read_sql(sa.select(employees), conn)
    dep = pd.read_sql(sa.select(departments), conn)
    pos = pd.read_sql(sa.select(positions), conn)

    # ===== METRICS =====

    col1, col2, col3 = st.columns(3)

    col1.metric("👨‍💼 Tổng nhân viên", len(emp))
    col2.metric("🏢 Tổng phòng ban", len(dep))
    col3.metric("💼 Tổng vị trí", len(pos))

    st.divider()

    # ===== BIỂU ĐỒ LƯƠNG =====

    if not emp.empty:

        fig1 = px.histogram(
            emp,
            x="salary",
            nbins=20,
            title="Phân bố lương nhân viên"
        )

        st.plotly_chart(fig1, use_container_width=True)

    # ===== NHÂN VIÊN THEO PHÒNG BAN =====

    if not emp.empty:

        dep_count = emp.groupby("department_id").size().reset_index(name="Số lượng")

        fig2 = px.pie(
            dep_count,
            names="department_id",
            values="Số lượng",
            title="Nhân viên theo phòng ban"
        )

        st.plotly_chart(fig2, use_container_width=True)