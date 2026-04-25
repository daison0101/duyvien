import streamlit as st
import pandas as pd
import sqlalchemy as sa
from io import BytesIO
from database import engine, employees, departments, positions


def show():

    st.header("📥 Xuất báo cáo Excel")

    # =========================
    # PHÂN QUYỀN
    # =========================

    if st.session_state.role != "admin":
        st.error("❌ Chỉ Admin mới được xuất báo cáo")
        return

    # =========================
    # LOAD DATA
    # =========================

    with engine.connect() as conn:

        emp = pd.read_sql(sa.select(employees), conn)
        dep = pd.read_sql(sa.select(departments), conn)
        pos = pd.read_sql(sa.select(positions), conn)

    if emp.empty:
        st.warning("Chưa có dữ liệu nhân viên")
        return

    # =========================
    # JOIN BẢNG
    # =========================

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
        "email": "Email",
        "phone": "SĐT",
        "salary": "Lương",
        "name_dep": "Phòng ban",
        "name_pos": "Vị trí"
    })

    emp_show = emp[
        [
            "Tên nhân viên",
            "Email",
            "SĐT",
            "Phòng ban",
            "Vị trí",
            "Lương"
        ]
    ]

    # =========================
    # TẠO FILE EXCEL
    # =========================

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:

        # Sheet danh sách nhân viên
        emp_show.to_excel(
            writer,
            sheet_name="Danh_sach_nhan_vien",
            index=False
        )

        # Sheet thống kê phòng ban
        dep_chart = emp_show.groupby(
            "Phòng ban"
        ).size().reset_index(name="Số nhân viên")

        dep_chart.to_excel(
            writer,
            sheet_name="Thong_ke_phong_ban",
            index=False
        )

        # Sheet top lương
        top_salary = emp_show.sort_values(
            by="Lương",
            ascending=False
        ).head(10)

        top_salary.to_excel(
            writer,
            sheet_name="Top_luong",
            index=False
        )

    buffer.seek(0)

    # =========================
    # DOWNLOAD
    # =========================

    st.download_button(
        label="📥 Tải báo cáo Excel",
        data=buffer,
        file_name="bao_cao_nhan_vien.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )