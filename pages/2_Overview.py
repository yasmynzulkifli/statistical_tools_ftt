import streamlit as st
from utils.supabase_helpers import fetch_table, ensure_login

st.set_page_config(page_title="Overview", page_icon="📋", layout="wide")
ensure_login()

st.title("📋 Overview — All Data Tables")

def show_table(title, table):
    st.subheader(title)
    df = fetch_table(table, order="date desc" if "date" in title.lower() else None)
    if df.empty:
        st.info("No data found.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

show_table("Google Analytics", "ga_traffic")
show_table("Google Ads", "ads_metrics")
show_table("Agent Postings", "agent_postings")
show_table("Google Index", "google_index")
show_table("Semrush Rank", "semrush_rank")
