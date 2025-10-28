import streamlit as st
from utils.supabase_helpers import ensure_login

st.set_page_config(
    page_title="FTT Metrics Dashboard",
    page_icon="🏠",
    layout="wide"
)

# --- Login ---
ensure_login()

# --- Sidebar Navigation ---
st.sidebar.title("🏠 FTT Metrics")
st.sidebar.caption(f"Logged in as **{st.session_state.get('username','')}**")

st.sidebar.markdown("---")
st.sidebar.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
st.sidebar.page_link("pages/2_Overview.py", label="📋 Overview")
st.sidebar.page_link("pages/3_Data_Entry.py", label="✍️ Data Entry")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- Welcome page placeholder ---
st.markdown(
    """
    # Welcome to FTT Metrics Dashboard  
    Use the sidebar to navigate between pages.  
    - 📊 **Dashboard:** Visualize key trends  
    - 📋 **Overview:** Review all tables  
    - ✍️ **Data Entry:** Add or import records  
    """
)
