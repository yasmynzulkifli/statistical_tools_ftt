import streamlit as st
import pandas as pd
from datetime import date
from utils.supabase_helpers import ensure_login

st.set_page_config(
    page_title="FTT Metrics Dashboard",
    page_icon="🏠",
    layout="wide"
)

# --- Login ---
ensure_login()

# --- Import/Define required variables and functions ---
BRANDS = ["FindHouse", "CheckValue"]
AGENT_POSTING_BRANDS = ["FindHouse"]

# --- Template CSV ---
def dl_csv_template(name: str, df: pd.DataFrame):
    """Create a downloadable CSV template button."""
    st.download_button(
        label=f"📥 {name} Template",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{name}_template.csv",
        mime="text/csv",
        use_container_width=True
    )


# --- Sidebar Header ---
st.sidebar.title("🏠 FTT Metrics")
st.sidebar.caption(f"Logged in as **{st.session_state.get('username','')}**")

st.sidebar.markdown("---")

# --- Pages Navigation (moved here, before CSV templates) ---
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/Dashboard.py", label="📊 Dashboard", icon="📊")
st.sidebar.page_link("pages/Overview.py", label="📋 Overview", icon="📋")
st.sidebar.page_link("pages/Data_Entry.py", label="✍️ Data Entry", icon="✍️")

st.sidebar.markdown("---")
with st.sidebar:
    with st.expander("📁 CSV Templates & Format Guide", expanded=False):
        n = len(BRANDS)
        dl_csv_template("ga_traffic", pd.DataFrame({
            "brand": BRANDS, "start_date": [date.today()]*n, "end_date": [date.today()]*n, "users": [1234]*n
        }))
        dl_csv_template("ads_metrics", pd.DataFrame({
            "brand": BRANDS, "date": [date.today()]*n, "clicks": [100]*n, "impressions": [2000]*n
        }))
        dl_csv_template("agent_postings", pd.DataFrame({
            "brand": AGENT_POSTING_BRANDS, "date": [date.today()]*len(AGENT_POSTING_BRANDS),
            "total_listings": [10]*len(AGENT_POSTING_BRANDS),
            "sale_listings": [6]*len(AGENT_POSTING_BRANDS),
            "rent_listings": [3]*len(AGENT_POSTING_BRANDS),
            "auction_listings": [1]*len(AGENT_POSTING_BRANDS)
        }))
        dl_csv_template("google_index", pd.DataFrame({
            "brand": BRANDS, "date": [date.today()]*n, "indexed": [512]*n
        }))
        dl_csv_template("semrush_rank", pd.DataFrame({
            "brand": BRANDS, "date": [date.today()]*n, "rank": [1430000]*n
        }))

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



