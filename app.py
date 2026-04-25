import streamlit as st
from dotenv import load_dotenv

# LOAD ENV TRƯỚC
load_dotenv()

from database import init_db

from modules import (
    auth,
    dashboard,
    employees,
    departments,
    positions,
    attendance,
    statistics,
    ai_chat,
    ai_cv,
    ai_analysis
)

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="HR AI Assistant",
    page_icon="👩‍💼",
    layout="wide"
)

# ================= STYLE =================

st.markdown("""
<style>

.main{
background-color:#f5f7fb;
}

.stButton>button{
border-radius:8px;
height:40px;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ================= INIT DB =================

@st.cache_resource
def init_database():
    init_db()

init_database()

# ================= TITLE =================

st.title("👩‍💼 HR AI Assistant - Giáp Thanh Tuyền")
st.caption("Hệ thống quản lý nhân sự tích hợp AI")

# ================= SESSION =================

if "login" not in st.session_state:
    st.session_state.login = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# ================= LOGIN PAGE =================

if not st.session_state.login:
    auth.login_page()
    st.stop()

# ================= SIDEBAR =================

st.sidebar.title("📊 HR Menu")

# 👉 HIỂN THỊ USER
st.sidebar.markdown(f"""
👤 **User:** {st.session_state.username}  
🔑 **Role:** {st.session_state.role}
""")

# ================= LOGOUT =================

if st.sidebar.button("🚪 Logout"):

    st.session_state.login = False
    st.session_state.role = None
    st.session_state.username = None

    if "messages" in st.session_state:
        st.session_state.messages = []

    st.success("Đăng xuất thành công")
    st.rerun()

# ================= MENU THEO ROLE =================

role = st.session_state.role

menu_options = ["🏠 Dashboard"]

# ===== ADMIN =====
if role == "admin":
    menu_options += [
        "📋 Quản lý nhân viên",
        "🏢 Quản lý phòng ban",
        "📌 Quản lý chức vụ",
        "🕒 Chấm công",
        "📊 Thống kê",
        "🤖 AI Chatbot HR",
        "📄 AI Sàng lọc CV",
        "🧠 AI Phân tích nhân sự"
    ]

# ===== HR =====
elif role == "hr":
    menu_options += [
        "📋 Quản lý nhân viên",
        "🕒 Chấm công",
        "📊 Thống kê",
        "🤖 AI Chatbot HR"
    ]

# ===== USER =====
else:
    menu_options += [
        "🕒 Chấm công",
        "🤖 AI Chatbot HR"
    ]

menu = st.sidebar.radio("Chọn chức năng", menu_options)

# ================= ROUTER =================

if menu == "🏠 Dashboard":
    dashboard.show()

elif menu == "📋 Quản lý nhân viên":
    employees.show()

elif menu == "🏢 Quản lý phòng ban":
    departments.show()

elif menu == "📌 Quản lý chức vụ":
    positions.show()

elif menu == "🕒 Chấm công":
    attendance.show()

elif menu == "📊 Thống kê":
    statistics.show()

elif menu == "🤖 AI Chatbot HR":
    ai_chat.show()

elif menu == "📄 AI Sàng lọc CV":
    ai_cv.show()

elif menu == "🧠 AI Phân tích nhân sự":
    ai_analysis.show()

# ================= FOOTER =================

st.sidebar.success("✅ Hệ thống hoạt động tốt")