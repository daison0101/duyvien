import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, positions


def show():

    # =============================
    # CHECK PERMISSION
    # =============================
    if st.session_state.role != "admin":
        st.error("❌ Bạn không có quyền truy cập chức năng này")
        st.stop()

    st.header("💼 Quản lý vị trí công việc")

    # =============================
    # 🔥 HIỂN THỊ THÔNG BÁO SAU RERUN
    # =============================
    if "pos_add" in st.session_state:
        st.success("Thêm vị trí thành công")
        del st.session_state.pos_add

    if "pos_update" in st.session_state:
        st.success("Cập nhật vị trí thành công")
        del st.session_state.pos_update

    if "pos_delete" in st.session_state:
        st.success("Đã xóa vị trí")
        del st.session_state.pos_delete

    # =============================
    # LOAD DATA
    # =============================
    with engine.connect() as conn:
        df = pd.read_sql(sa.select(positions), conn)

    # =============================
    # HIỂN THỊ DANH SÁCH
    # =============================
    if not df.empty:

        df_show = df.copy()

        df_show.columns = [
            "ID vị trí",
            "Tên vị trí",
            "Mô tả"
        ]

        st.dataframe(df_show, use_container_width=True)

    else:
        st.info("Chưa có vị trí")

    st.divider()

    # =============================
    # ➕ THÊM VỊ TRÍ
    # =============================
    st.subheader("➕ Thêm vị trí")

    name = st.text_input("Tên vị trí")
    description = st.text_input("Mô tả")

    if st.button("💾 Thêm vị trí"):

        if name.strip() == "":
            st.warning("Vui lòng nhập tên vị trí")
            return

        with engine.connect() as conn:
            check = conn.execute(
                sa.select(positions).where(
                    positions.c.name == name
                )
            ).fetchone()

        if check:
            st.error("Vị trí đã tồn tại")
            return

        with engine.begin() as conn:
            conn.execute(
                positions.insert().values(
                    name=name,
                    description=description
                )
            )

        st.session_state.pos_add = True
        st.rerun()

    st.divider()

    # =============================
    # ✏️ SỬA VỊ TRÍ
    # =============================
    if not df.empty:

        st.subheader("✏️ Sửa vị trí")

        pos_id_edit = st.selectbox(
            "Chọn vị trí cần sửa",
            df["id"],
            key="edit_pos"
        )

        pos_row = df[df["id"] == pos_id_edit].iloc[0]

        new_name = st.text_input(
            "Tên vị trí mới",
            value=pos_row["name"]
        )

        new_description = st.text_input(
            "Mô tả mới",
            value=pos_row["description"]
        )

        if st.button("💾 Cập nhật vị trí"):

            if new_name.strip() == "":
                st.warning("Tên vị trí không được để trống")
                return

            with engine.begin() as conn:
                conn.execute(
                    sa.update(positions)
                    .where(positions.c.id == pos_id_edit)
                    .values(
                        name=new_name,
                        description=new_description
                    )
                )

            st.session_state.pos_update = True
            st.rerun()

    st.divider()

    # =============================
    # ❌ XOÁ VỊ TRÍ
    # =============================
    if not df.empty:

        st.subheader("❌ Xóa vị trí")

        pos_id = st.selectbox(
            "Chọn vị trí",
            df["id"],
            key="delete_pos"
        )

        if st.button("🗑 Xóa vị trí"):

            with engine.connect() as conn:
                result = conn.execute(
                    sa.text(
                        "SELECT COUNT(*) FROM employees WHERE position_id = :id"
                    ),
                    {"id": pos_id}
                ).scalar()

            if result > 0:
                st.error("Không thể xóa vì vị trí này đang có nhân viên")
                return

            with engine.begin() as conn:
                conn.execute(
                    sa.delete(positions).where(
                        positions.c.id == pos_id
                    )
                )

            st.session_state.pos_delete = True
            st.rerun()