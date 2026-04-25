import streamlit as st
import pandas as pd
import sqlalchemy as sa
import plotly.express as px
from database import engine, employees, departments, positions


def show():

    st.header("📊 Thống kê nhân sự")

    # =============================
    # LOAD DATA
    # =============================

    with engine.connect() as conn:

        emp = pd.read_sql(sa.select(employees), conn)
        dep = pd.read_sql(sa.select(departments), conn)
        pos = pd.read_sql(sa.select(positions), conn)

    if emp.empty:
        st.warning("Chưa có dữ liệu nhân viên")
        return

    # =============================
    # JOIN DATA
    # =============================

    emp = emp.merge(
        dep,
        left_on="department_id",
        right_on="id",
        how="left",
        suffixes=("", "_dep")
    )

    emp = emp.merge(
        pos,
        left_on="position_id",
        right_on="id",
        how="left",
        suffixes=("", "_pos")
    )

    emp["salary"] = emp["salary"].fillna(0)

    emp = emp.rename(columns={
        "name": "Tên nhân viên",
        "email": "Email",
        "phone": "SĐT",
        "salary": "Lương",
        "name_dep": "Phòng ban",
        "name_pos": "Vị trí"
    })

    # =============================
    # DASHBOARD SUMMARY
    # =============================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👨‍💼 Tổng nhân viên", len(emp))
    col2.metric("🏢 Tổng phòng ban", emp["Phòng ban"].nunique())
    col3.metric("💼 Tổng vị trí", emp["Vị trí"].nunique())
    col4.metric("💰 Lương trung bình", f"{int(emp['Lương'].mean()):,}")

    st.divider()

    col1, col2 = st.columns(2)

    # =============================
    # NHÂN VIÊN THEO PHÒNG BAN
    # =============================

    dep_chart = emp.groupby("Phòng ban").size().reset_index(name="Số nhân viên")

    fig1 = px.bar(
        dep_chart,
        x="Phòng ban",
        y="Số nhân viên",
        title="Nhân viên theo phòng ban",
        color="Phòng ban"
    )

    col1.plotly_chart(fig1, use_container_width=True)

    # =============================
    # NHÂN VIÊN THEO VỊ TRÍ
    # =============================

    pos_chart = emp.groupby("Vị trí").size().reset_index(name="Số nhân viên")

    fig2 = px.pie(
        pos_chart,
        names="Vị trí",
        values="Số nhân viên",
        title="Nhân viên theo vị trí"
    )

    col2.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # =============================
    # PHÂN BỐ LƯƠNG
    # =============================

    fig3 = px.histogram(
        emp,
        x="Lương",
        nbins=20,
        title="Phân bố lương nhân viên"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # =============================
    # TOP LƯƠNG
    # =============================

    st.subheader("💰 Top nhân viên lương cao")

    top_salary = emp.sort_values(
        by="Lương",
        ascending=False
    ).head(10)

    st.dataframe(
        top_salary[
            [
                "Tên nhân viên",
                "Phòng ban",
                "Vị trí",
                "Lương"
            ]
        ],
        use_container_width=True
    )