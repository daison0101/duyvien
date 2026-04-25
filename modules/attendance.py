import streamlit as st
import pandas as pd
import sqlalchemy as sa
from datetime import date
from database import engine, attendance, employees


def show():
    st.header("🕒 Chấm công nhân viên")

    role = st.session_state.get("role", "user")
    current_emp_id = st.session_state.get("employee_id")

    # =============================
    # 🔥 HIỂN THỊ THÔNG BÁO SAU RERUN
    # =============================
    if "attendance_success" in st.session_state:
        st.success("Đã lưu chấm công")
        del st.session_state.attendance_success

    if "update_success" in st.session_state:
        st.success("Cập nhật thành công")
        del st.session_state.update_success

    if "delete_success" in st.session_state:
        st.success("Xóa thành công")
        del st.session_state.delete_success

    # =============================
    # LOAD NHÂN VIÊN
    # =============================
    with engine.connect() as conn:
        emp = pd.read_sql(sa.select(employees), conn)

    if emp.empty:
        st.warning("Chưa có nhân viên")
        return

    # =============================
    # 🔥 PHÂN QUYỀN
    # =============================
    if role == "admin":
        emp_options = {
            f"{row['id']} - {row['name']}": row["id"]
            for _, row in emp.iterrows()
        }
    else:
        emp = emp[emp["id"] == current_emp_id]

        if emp.empty:
            st.error("Không tìm thấy thông tin nhân viên")
            return

        emp_options = {
            f"{row['id']} - {row['name']}": row["id"]
            for _, row in emp.iterrows()
        }

    # =============================
    # ➕ CHẤM CÔNG
    # =============================
    st.subheader("➕ Chấm công")

    col1, col2 = st.columns(2)

    with col1:
        selected_emp = st.selectbox("Chọn nhân viên", list(emp_options.keys()))
        checkin = st.time_input("Giờ vào")

    with col2:
        checkout = st.time_input("Giờ ra")

    if st.button("💾 Lưu chấm công"):

        emp_id = emp_options[selected_emp]

        with engine.begin() as conn:
            conn.execute(
                attendance.insert().values(
                    employee_id=int(emp_id),
                    date=date.today(),
                    checkin=str(checkin),
                    checkout=str(checkout)
                )
            )

        # 🔥 FIX: dùng session_state thay vì success trực tiếp
        st.session_state.attendance_success = True
        st.rerun()

    st.divider()

    # =============================
    # 📋 LỊCH SỬ CHẤM CÔNG
    # =============================
    st.subheader("📋 Lịch sử chấm công")

    with engine.connect() as conn:
        df = pd.read_sql(sa.select(attendance), conn)

    if df.empty:
        st.info("Chưa có dữ liệu chấm công")
        return

    # USER chỉ xem mình
    if role != "admin":
        df = df[df["employee_id"] == current_emp_id]

    # JOIN lấy tên
    df = df.merge(
        emp,
        left_on="employee_id",
        right_on="id",
        how="left",
        suffixes=("", "_emp")
    )

    # =============================
    # 🔐 ADMIN: SỬA / XOÁ
    # =============================
    if role == "admin":

        st.info("🔐 Admin có quyền sửa và xóa chấm công")

        record_id = st.selectbox("Chọn ID chấm công", df["id"])

        selected_row = df[df["id"] == record_id].iloc[0]

        new_checkin = st.time_input(
            "Sửa giờ vào",
            pd.to_datetime(selected_row["checkin"]).time()
        )

        new_checkout = st.time_input(
            "Sửa giờ ra",
            pd.to_datetime(selected_row["checkout"]).time()
        )

        col_edit, col_delete = st.columns(2)

        with col_edit:
            if st.button("✏️ Cập nhật"):
                with engine.begin() as conn:
                    conn.execute(
                        attendance.update()
                        .where(attendance.c.id == record_id)
                        .values(
                            checkin=str(new_checkin),
                            checkout=str(new_checkout)
                        )
                    )

                st.session_state.update_success = True
                st.rerun()

        with col_delete:
            if st.button("🗑️ Xóa"):
                with engine.begin() as conn:
                    conn.execute(
                        attendance.delete()
                        .where(attendance.c.id == record_id)
                    )

                st.session_state.delete_success = True
                st.rerun()

    else:
        st.info("👤 Bạn chỉ có quyền chấm công và xem dữ liệu của mình")

    # =============================
    # HIỂN THỊ BẢNG
    # =============================
    df_show = df[[
        "id",
        "name",
        "date",
        "checkin",
        "checkout"
    ]]

    df_show.columns = [
        "ID",
        "Tên nhân viên",
        "Ngày",
        "Giờ vào",
        "Giờ ra"
    ]

    st.dataframe(df_show, use_container_width=True)