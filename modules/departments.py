import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, departments


def show():

    # =============================
    # CHECK PERMISSION
    # =============================
    if st.session_state.role != "admin":
        st.error("❌ Bạn không có quyền truy cập chức năng này")
        st.stop()

    st.header("🏢 Quản lý phòng ban")

    # =============================
    # 🔥 HIỂN THỊ THÔNG BÁO SAU RERUN
    # =============================
    if "dep_add" in st.session_state:
        st.success("Thêm phòng ban thành công")
        del st.session_state.dep_add

    if "dep_update" in st.session_state:
        st.success("Cập nhật phòng ban thành công")
        del st.session_state.dep_update

    if "dep_delete" in st.session_state:
        st.success("Đã xóa phòng ban")
        del st.session_state.dep_delete

    # =============================
    # LOAD DATA
    # =============================
    with engine.connect() as conn:
        df = pd.read_sql(sa.select(departments), conn)

    # =============================
    # HIỂN THỊ DANH SÁCH
    # =============================
    if not df.empty:

        df_show = df.copy()

        df_show.columns = [
            "ID phòng ban",
            "Tên phòng ban",
            "Mô tả"
        ]

        st.dataframe(df_show, use_container_width=True)

    else:
        st.info("Chưa có phòng ban")

    st.divider()

    # =============================
    # ➕ THÊM PHÒNG BAN
    # =============================
    st.subheader("➕ Thêm phòng ban")

    name = st.text_input("Tên phòng ban")
    description = st.text_input("Mô tả")

    if st.button("💾 Thêm phòng ban"):

        if name.strip() == "":
            st.warning("Vui lòng nhập tên phòng ban")
            return

        with engine.connect() as conn:
            check = conn.execute(
                sa.select(departments).where(
                    departments.c.name == name
                )
            ).fetchone()

        if check:
            st.error("Phòng ban đã tồn tại")
            return

        with engine.begin() as conn:
            conn.execute(
                departments.insert().values(
                    name=name,
                    description=description
                )
            )

        st.session_state.dep_add = True
        st.rerun()

    st.divider()

    # =============================
    # ✏️ SỬA PHÒNG BAN
    # =============================
    if not df.empty:

        st.subheader("✏️ Sửa phòng ban")

        dep_id_edit = st.selectbox(
            "Chọn phòng ban cần sửa",
            df["id"],
            key="edit_dep"
        )

        dep_row = df[df["id"] == dep_id_edit].iloc[0]

        new_name = st.text_input(
            "Tên phòng ban mới",
            value=dep_row["name"]
        )

        new_description = st.text_input(
            "Mô tả mới",
            value=dep_row["description"]
        )

        if st.button("💾 Cập nhật phòng ban"):

            if new_name.strip() == "":
                st.warning("Tên phòng ban không được để trống")
                return

            with engine.begin() as conn:
                conn.execute(
                    sa.update(departments)
                    .where(departments.c.id == dep_id_edit)
                    .values(
                        name=new_name,
                        description=new_description
                    )
                )

            st.session_state.dep_update = True
            st.rerun()

    st.divider()

    # =============================
    # ❌ XOÁ PHÒNG BAN
    # =============================
    if not df.empty:

        st.subheader("❌ Xóa phòng ban")

        dep_id = st.selectbox(
            "Chọn phòng ban",
            df["id"],
            key="delete_dep"
        )

        if st.button("🗑 Xóa phòng ban"):

            with engine.connect() as conn:
                result = conn.execute(
                    sa.text(
                        "SELECT COUNT(*) FROM employees WHERE department_id = :id"
                    ),
                    {"id": dep_id}
                ).scalar()

            if result > 0:
                st.error("Không thể xóa vì phòng ban này đang có nhân viên")
                return

            with engine.begin() as conn:
                conn.execute(
                    sa.delete(departments).where(
                        departments.c.id == dep_id
                    )
                )

            st.session_state.dep_delete = True
            st.rerun()