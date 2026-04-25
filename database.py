import os
import sqlalchemy as sa
import bcrypt
from dotenv import load_dotenv

# ==============================
# LOAD ENV
# ==============================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL chưa được cấu hình")

# ==============================
# ENGINE
# ==============================

engine = sa.create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    future=True
)

metadata = sa.MetaData()

# ==============================
# USERS
# ==============================

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(50), unique=True, nullable=False),
    sa.Column("password", sa.String(200), nullable=False),
    sa.Column("role", sa.String(20), default="user"),

    # 🔥 LIÊN KẾT 1-1 VỚI EMPLOYEES
    sa.Column("employee_id", sa.Integer, sa.ForeignKey("employees.id"), unique=True)
)

# ==============================
# DEPARTMENTS
# ==============================

departments = sa.Table(
    "departments",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(100), unique=True, nullable=False),
    sa.Column("description", sa.String(255))
)

# ==============================
# POSITIONS
# ==============================

positions = sa.Table(
    "positions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(100), unique=True, nullable=False),
    sa.Column("description", sa.String(255))
)

# ==============================
# EMPLOYEES
# ==============================

employees = sa.Table(
    "employees",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("employee_code", sa.String(50), unique=True),
    sa.Column("name", sa.String(150), nullable=False),
    sa.Column("dob", sa.Date),
    sa.Column("gender", sa.String(10)),
    sa.Column("address", sa.String(255)),
    sa.Column("phone", sa.String(20)),
    sa.Column("email", sa.String(150), unique=True),
    sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id")),
    sa.Column("position_id", sa.Integer, sa.ForeignKey("positions.id")),
    sa.Column("salary", sa.Float),
    sa.Column("join_date", sa.Date),
    sa.Column("status", sa.String(50)),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now())
)

# ==============================
# ATTENDANCE
# ==============================

attendance = sa.Table(
    "attendance",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("employee_id", sa.Integer, sa.ForeignKey("employees.id")),
    sa.Column("date", sa.Date),
    sa.Column("checkin", sa.String(20)),
    sa.Column("checkout", sa.String(20))
)

# ==============================
# AUTO ADD COLUMN FUNCTION
# ==============================

def add_column_if_not_exists(table_name, column_name, column_type):
    with engine.connect() as conn:
        result = conn.execute(sa.text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table
            AND table_schema = DATABASE()
        """), {"table": table_name})

        columns = [row[0] for row in result]

        if column_name not in columns:
            conn.execute(sa.text(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            ))
            conn.commit()

# ==============================
# INIT DATABASE
# ==============================

def init_db():

    # tạo bảng nếu chưa có
    metadata.create_all(engine)

    # thêm cột nếu thiếu
    add_column_if_not_exists("departments", "description", "VARCHAR(255)")
    add_column_if_not_exists("positions", "description", "VARCHAR(255)")

    # EMPLOYEES
    add_column_if_not_exists("employees", "employee_code", "VARCHAR(50)")
    add_column_if_not_exists("employees", "dob", "DATE")
    add_column_if_not_exists("employees", "gender", "VARCHAR(10)")
    add_column_if_not_exists("employees", "address", "VARCHAR(255)")
    add_column_if_not_exists("employees", "join_date", "DATE")
    add_column_if_not_exists("employees", "status", "VARCHAR(50)")

    # 🔥 USERS - THÊM employee_id
    add_column_if_not_exists("users", "employee_id", "INT")

    # ==============================
    # TẠO ADMIN MẶC ĐỊNH
    # ==============================

    with engine.connect() as conn:

        result = conn.execute(
            sa.select(users).where(users.c.username == "admin")
        ).fetchone()

        if not result:

            hashed_password = bcrypt.hashpw(
                "admin123".encode(),
                bcrypt.gensalt()
            ).decode()

            with engine.begin() as conn2:
                conn2.execute(
                    users.insert().values(
                        username="admin",
                        password=hashed_password,
                        role="admin",
                        employee_id=None  # 🔥 admin không cần liên kết nhân viên
                    )
                )