import streamlit as st

from database import init_db

from modules import auth
from modules import dashboard
from modules import employees
from modules import departments
from modules import positions
from modules import attendance
from modules import statistics
from modules import search
from modules import export_excel
from modules import ai_chat
from modules import ai_analysis


# =============================
# PAGE CONFIG
# =============================

st.set_page_config(
    page_title="SanCo HR System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================
# CUSTOM CSS
# =============================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

h1, h2, h3 {
    color: #38bdf8;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    height: 40px;
}

.stButton>button:hover {
    background-color: #1d4ed8;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# =============================
# INIT DATABASE
# =============================

if "db_init" not in st.session_state:
    init_db()
    st.session_state.db_init = True


# =============================
# SESSION LOGIN
# =============================

if "login" not in st.session_state:
    st.session_state.login = False

if "role" not in st.session_state:
    st.session_state.role = "user"

if "username" not in st.session_state:
    st.session_state.username = ""


# =============================
# LOGIN PAGE
# =============================

if not st.session_state.login:

    st.title("🔐 Đăng nhập hệ thống")
    auth.show()


# =============================
# MAIN SYSTEM
# =============================

else:

    st.title("🏢 HỆ THỐNG QUẢN LÝ NHÂN VIÊN SANCO")

    st.markdown("---")

    # =============================
    # SIDEBAR
    # =============================

    st.sidebar.title("🏢 SANCO HR SYSTEM")

    st.sidebar.success(
        f"👤 {st.session_state.username} ({st.session_state.role})"
    )

    role = st.session_state.role

    # =============================
    # MENU ADMIN
    # =============================

    if role == "admin":

        menu_items = {
            "📊 Dashboard": dashboard.show,
            "👨‍💼 Nhân viên": employees.show,
            "🏢 Phòng ban": departments.show,
            "📌 Vị trí": positions.show,
            "🕒 Chấm công": attendance.show,
            "📈 Thống kê": statistics.show,
            "🔎 Tìm kiếm": search.show,
            "📥 Xuất Excel": export_excel.show,
            "🤖 AI Chat HR": ai_chat.show,
            "🧠 AI Phân tích": ai_analysis.show
        }

    # =============================
    # MENU USER
    # =============================

    else:

        menu_items = {
            "📊 Dashboard": dashboard.show,
            "👨‍💼 Nhân viên": employees.show,
            "🕒 Chấm công": attendance.show,
            "🔎 Tìm kiếm": search.show,
            "🤖 AI Chat HR": ai_chat.show
        }

    # =============================
    # MENU SELECT
    # =============================

    menu = st.sidebar.radio(
        "📋 Chức năng",
        list(menu_items.keys())
    )

    # =============================
    # ROUTER
    # =============================

    menu_items[menu]()

    # =============================
    # LOGOUT
    # =============================

    st.sidebar.divider()

    if st.sidebar.button("🚪 Đăng xuất"):

        st.session_state.login = False
        st.session_state.role = "user"
        st.session_state.username = ""

        st.rerun()