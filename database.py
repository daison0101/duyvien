import sqlalchemy as sa
import pandas as pd
import streamlit as st
import os

# =============================
# DATABASE CONFIG
# =============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL chưa được cấu hình")

engine = sa.create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

metadata = sa.MetaData()

# ================= USERS =================
# 🔥 1 USER ↔ 1 EMPLOYEE

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(50), unique=True, nullable=False),
    sa.Column("password", sa.String(200), nullable=False),
    sa.Column("role", sa.String(20), default="user"),

    sa.Column(
        "employee_id",
        sa.Integer,
        sa.ForeignKey("employees.id"),
        unique=True  # đảm bảo 1-1
    )
)

# ================= DEPARTMENTS =================

departments_table = sa.Table(
    "departments",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("ten_phong", sa.String(100), unique=True),
    sa.Column("mo_ta", sa.String(255))
)

# ================= POSITIONS =================

positions_table = sa.Table(
    "positions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("ten_chuc_vu", sa.String(100), unique=True),
    sa.Column("mo_ta", sa.String(255))
)

# ================= EMPLOYEES =================

employees_table = sa.Table(
    "employees",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("ho_ten", sa.String(150), nullable=False),
    sa.Column("email", sa.String(150), unique=True),
    sa.Column("dien_thoai", sa.String(20)),

    sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id")),
    sa.Column("position_id", sa.Integer, sa.ForeignKey("positions.id")),

    sa.Column("ngay_vao_lam", sa.String(50)),

    # ⚠️ giữ lại để tránh crash code cũ
    sa.Column("user_id", sa.Integer)
)

# ================= ATTENDANCE =================

attendance_table = sa.Table(
    "attendance",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("employee_id", sa.Integer, sa.ForeignKey("employees.id")),
    sa.Column("ngay", sa.String(50)),
    sa.Column("check_in", sa.String(20)),
    sa.Column("check_out", sa.String(20))
)

# ================= AUTO ADD COLUMN =================

def add_column_if_not_exists(table_name, column_name, column_type):

    with engine.connect() as conn:

        # ✅ FIX CHO POSTGRESQL
        result = conn.execute(sa.text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table
            AND table_schema = 'public'
        """), {"table": table_name})

        columns = [row[0] for row in result]

        if column_name not in columns:
            conn.execute(sa.text(
                f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}'
            ))
            conn.commit()

# ================= INIT DATABASE =================

def init_db():

    # tạo bảng
    metadata.create_all(engine)

    # 🔥 đảm bảo có employee_id
    add_column_if_not_exists("users", "employee_id", "INTEGER")

# ================= CACHE FUNCTIONS =================

@st.cache_data
def get_employees():

    query = """
    SELECT 
        e.id,
        e.ho_ten,
        e.email,
        e.dien_thoai,
        u.username,
        d.ten_phong,
        p.ten_chuc_vu,
        e.ngay_vao_lam
    FROM employees e
    LEFT JOIN users u ON u.employee_id = e.id
    LEFT JOIN departments d ON e.department_id = d.id
    LEFT JOIN positions p ON e.position_id = p.id
    ORDER BY e.id
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


@st.cache_data
def get_departments():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(departments_table), conn)


@st.cache_data
def get_positions():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(positions_table), conn)


@st.cache_data
def get_attendance():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(attendance_table), conn)