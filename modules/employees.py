import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, employees, departments, positions


@st.cache_data
def load_data():
    with engine.connect() as conn:
        emp = pd.read_sql(sa.select(employees), conn)
        dep = pd.read_sql(sa.select(departments), conn)
        pos = pd.read_sql(sa.select(positions), conn)

    return emp, dep, pos


def show():
    st.header("👨‍💼 Quản lý nhân viên")

    # 🔥 THÔNG BÁO SAU RERUN
    if "emp_add" in st.session_state:
        st.success("Thêm nhân viên thành công")
        del st.session_state.emp_add

    if "emp_update" in st.session_state:
        st.success("Cập nhật thành công")
        del st.session_state.emp_update

    if "emp_delete" in st.session_state:
        st.success("Đã xoá nhân viên")
        del st.session_state.emp_delete

    emp, dep, pos = load_data()

    role = st.session_state.get("role", "user")
    current_emp_id = st.session_state.get("employee_id")

    # =============================
    # 🔥 PHÂN QUYỀN
    # =============================
    if role != "admin":
        emp = emp[emp["id"] == current_emp_id]

    # =============================
    # HIỂN THỊ DANH SÁCH
    # =============================
    if not emp.empty:

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

        emp_show = emp[
            [
                "id",
                "employee_code",
                "name",
                "gender",
                "phone",
                "name_dep",
                "name_pos",
                "salary",
                "status"
            ]
        ]

        emp_show.columns = [
            "ID",
            "Mã NV",
            "Tên nhân viên",
            "Giới tính",
            "SĐT",
            "Phòng ban",
            "Chức vụ",
            "Lương",
            "Trạng thái"
        ]

        st.dataframe(emp_show, use_container_width=True)

    else:
        st.info("Không có dữ liệu nhân viên")

    # =============================
    # XEM CHI TIẾT
    # =============================
    st.divider()
    st.subheader("🔍 Xem chi tiết nhân viên")

    if not emp.empty:

        selected_id = st.selectbox(
            "Chọn nhân viên",
            emp["id"],
            key="view_emp",
            format_func=lambda x: f"ID {x} - {emp[emp['id']==x]['name'].values[0]}"
        )

        emp_detail = emp[emp["id"] == selected_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**👤 Tên:** {emp_detail['name']}")
            st.write(f"**🆔 Mã NV:** {emp_detail.get('employee_code','')}")
            st.write(f"**🎂 Ngày sinh:** {emp_detail.get('dob','')}")
            st.write(f"**⚧ Giới tính:** {emp_detail.get('gender','')}")
            st.write(f"**📍 Địa chỉ:** {emp_detail.get('address','')}")

        with col2:
            st.write(f"**📧 Email:** {emp_detail.get('email','')}")
            st.write(f"**📱 SĐT:** {emp_detail.get('phone','')}")
            st.write(f"**🏢 Phòng ban:** {emp_detail.get('name_dep','')}")
            st.write(f"**💼 Vị trí:** {emp_detail.get('name_pos','')}")
            st.write(f"**💰 Lương:** {emp_detail.get('salary','')}")
            st.write(f"**📅 Ngày vào:** {emp_detail.get('join_date','')}")
            st.write(f"**📌 Trạng thái:** {emp_detail.get('status','')}")

    # =============================
    # USER STOP
    # =============================
    if role != "admin":
        st.warning("Bạn chỉ có quyền xem thông tin của mình")
        return

    st.divider()

    # =============================
    # ➕ THÊM NHÂN VIÊN
    # =============================
    st.subheader("➕ Thêm nhân viên")

    if dep.empty or pos.empty:
        st.error("⚠ Cần tạo phòng ban và vị trí trước")
        return

    with st.form("add_employee"):

        col1, col2 = st.columns(2)

        with col1:
            code = st.text_input("Mã NV")
            name = st.text_input("Tên nhân viên")
            dob = st.date_input("Ngày sinh")
            gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"], key="add_gender")
            address = st.text_input("Địa chỉ")

        with col2:
            email = st.text_input("Email")
            phone = st.text_input("SĐT")
            salary = st.number_input("Lương", min_value=0)
            join_date = st.date_input("Ngày vào công ty")
            status = st.selectbox("Trạng thái", ["Đang làm", "Nghỉ việc"], key="add_status")

        dep_option = st.selectbox("Phòng ban", dep["name"].tolist(), key="add_dep")
        pos_option = st.selectbox("Vị trí", pos["name"].tolist(), key="add_pos")

        submit = st.form_submit_button("💾 Thêm nhân viên")

        if submit:

            if name.strip() == "":
                st.warning("Vui lòng nhập tên nhân viên")
                return

            dep_id = dep[dep["name"] == dep_option]["id"].values[0]
            pos_id = pos[pos["name"] == pos_option]["id"].values[0]

            with engine.begin() as conn:
                conn.execute(
                    employees.insert().values(
                        employee_code=code,
                        name=name,
                        dob=dob,
                        gender=gender,
                        address=address,
                        email=email,
                        phone=phone,
                        department_id=int(dep_id),
                        position_id=int(pos_id),
                        salary=salary,
                        join_date=join_date,
                        status=status
                    )
                )

            st.session_state.emp_add = True
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # =============================
    # ✏️ SỬA NHÂN VIÊN
    # =============================
    st.subheader("✏️ Sửa nhân viên")

    if not emp.empty:

        emp_id = st.selectbox(
            "Chọn nhân viên",
            emp["id"].tolist(),
            key="edit_emp"
        )

        emp_row = emp[emp["id"] == emp_id].iloc[0]

        with st.form("edit_employee"):

            name = st.text_input("Tên", emp_row["name"])
            code = st.text_input("Mã NV", emp_row.get("employee_code",""))
            email = st.text_input("Email", emp_row["email"])
            phone = st.text_input("SĐT", emp_row["phone"])
            address = st.text_input("Địa chỉ", emp_row.get("address",""))

            salary = st.number_input(
                "Lương",
                value=float(emp_row["salary"]) if pd.notna(emp_row["salary"]) else 0
            )

            status = st.selectbox("Trạng thái", ["Đang làm", "Nghỉ việc"], key="edit_status")

            dep_option = st.selectbox("Phòng ban", dep["name"].tolist(), key="edit_dep")
            pos_option = st.selectbox("Vị trí", pos["name"].tolist(), key="edit_pos")

            submit_edit = st.form_submit_button("💾 Cập nhật")

            if submit_edit:

                dep_id = dep[dep["name"] == dep_option]["id"].values[0]
                pos_id = pos[pos["name"] == pos_option]["id"].values[0]

                with engine.begin() as conn:
                    conn.execute(
                        sa.update(employees)
                        .where(employees.c.id == int(emp_id))
                        .values(
                            employee_code=code,
                            name=name,
                            email=email,
                            phone=phone,
                            address=address,
                            department_id=int(dep_id),
                            position_id=int(pos_id),
                            salary=salary,
                            status=status
                        )
                    )

                st.session_state.emp_update = True
                st.cache_data.clear()
                st.rerun()

    st.divider()

    # =============================
    # 🗑 XOÁ NHÂN VIÊN
    # =============================
    st.subheader("🗑 Xoá nhân viên")

    if not emp.empty:

        emp_delete = st.selectbox(
            "Chọn nhân viên",
            emp["id"].tolist(),
            key="delete_emp_select"
        )

        if st.button("Xoá nhân viên"):

            with engine.begin() as conn:
                conn.execute(
                    sa.delete(employees).where(
                        employees.c.id == int(emp_delete)
                    )
                )

            st.session_state.emp_delete = True
            st.cache_data.clear()
            st.rerun()