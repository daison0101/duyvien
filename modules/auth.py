import streamlit as st
import sqlalchemy as sa
import bcrypt
from database import engine, users, employees


def show():

    st.subheader("🔐 Đăng nhập hệ thống")

    username = st.text_input("Tài khoản")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập"):

        with engine.connect() as conn:

            query = sa.select(users).where(users.c.username == username)
            result = conn.execute(query).fetchone()

        if result:

            stored_password = result.password.encode()

            if bcrypt.checkpw(password.encode(), stored_password):

                st.session_state.login = True
                st.session_state.username = username
                st.session_state.role = result.role
                st.session_state.employee_id = result.employee_id

                st.success("Đăng nhập thành công")
                st.rerun()

            else:
                st.error("❌ Sai mật khẩu")

        else:
            st.error("❌ Tài khoản không tồn tại")

    st.divider()

    # =============================
    # REGISTER
    # =============================

    st.subheader("📝 Đăng ký tài khoản")

    # 🔥 HIỂN THỊ THÔNG BÁO SAU RERUN
    if "register_success" in st.session_state:
        st.success("Tạo tài khoản thành công")
        del st.session_state.register_success

    new_user = st.text_input("Username mới")
    new_pass = st.text_input("Password mới", type="password")

    # =============================
    # LẤY DANH SÁCH NHÂN VIÊN CHƯA CÓ TÀI KHOẢN
    # =============================

    with engine.connect() as conn:

        used_ids = conn.execute(
            sa.select(users.c.employee_id).where(users.c.employee_id != None)
        ).fetchall()

        used_ids = [row[0] for row in used_ids if row[0] is not None]

        if used_ids:
            emp_list = conn.execute(
                sa.select(employees).where(~employees.c.id.in_(used_ids))
            ).fetchall()
        else:
            emp_list = conn.execute(
                sa.select(employees)
            ).fetchall()

    # 🔥 TẠO DROPDOWN
    emp_options = {
        f"{emp.id} - {emp.name}": emp.id for emp in emp_list
    }

    # 🔥 CHECK HẾT NHÂN VIÊN
    if not emp_options:
        st.warning("⚠ Tất cả nhân viên đã có tài khoản")
        return

    selected_emp = st.selectbox("Chọn nhân viên", list(emp_options.keys()))

    # =============================
    # TẠO TÀI KHOẢN
    # =============================

    if st.button("Tạo tài khoản"):

        if new_user.strip() == "" or new_pass.strip() == "":
            st.warning("Vui lòng nhập đầy đủ thông tin")
            return

        employee_id = emp_options[selected_emp]

        with engine.connect() as conn:

            check = conn.execute(
                sa.select(users).where(users.c.username == new_user)
            ).fetchone()

        if check:
            st.error("Username đã tồn tại")
            return

        hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())

        with engine.begin() as conn:

            conn.execute(
                users.insert().values(
                    username=new_user,
                    password=hashed.decode(),
                    role="user",
                    employee_id=employee_id
                )
            )

        # 🔥 GIỮ THÔNG BÁO SAU RERUN
        st.session_state.register_success = True
        st.rerun()