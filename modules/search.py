import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, employees, departments, positions


def show():

    st.header("🔎 Tìm kiếm nhân viên")

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
    # JOIN BẢNG
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

    emp = emp.rename(columns={
        "name": "Tên nhân viên",
        "name_dep": "Phòng ban",
        "name_pos": "Vị trí",
        "salary": "Lương"
    })

    # =============================
    # XỬ LÝ SLIDER LƯƠNG
    # =============================

    min_salary = int(emp["Lương"].min())
    max_salary = int(emp["Lương"].max())

    if min_salary == max_salary:
        max_salary = min_salary + 1

    # =============================
    # FORM TÌM KIẾM
    # =============================

    col1, col2 = st.columns(2)

    with col1:
        keyword = st.text_input("Tên nhân viên")

        dep_filter = st.selectbox(
            "Phòng ban",
            ["Tất cả"] + list(dep["name"])
        )

    with col2:
        pos_filter = st.selectbox(
            "Vị trí",
            ["Tất cả"] + list(pos["name"])
        )

        salary_filter = st.slider(
            "Khoảng lương",
            min_salary,
            max_salary,
            (min_salary, max_salary)
        )

    # =============================
    # LỌC DỮ LIỆU
    # =============================

    df = emp.copy()

    if keyword:
        df = df[df["Tên nhân viên"].str.contains(keyword, case=False, na=False)]

    if dep_filter != "Tất cả":
        df = df[df["Phòng ban"] == dep_filter]

    if pos_filter != "Tất cả":
        df = df[df["Vị trí"] == pos_filter]

    df = df[
        (df["Lương"] >= salary_filter[0]) &
        (df["Lương"] <= salary_filter[1])
    ]

    # =============================
    # HIỂN THỊ
    # =============================

    st.subheader("Kết quả tìm kiếm")

    if df.empty:
        st.info("Không tìm thấy nhân viên phù hợp")
    else:
        st.dataframe(
            df[
                [
                    "Tên nhân viên",
                    "email",
                    "phone",
                    "Phòng ban",
                    "Vị trí",
                    "Lương"
                ]
            ],
            use_container_width=True
        )