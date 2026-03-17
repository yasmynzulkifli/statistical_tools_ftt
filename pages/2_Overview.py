import streamlit as st
from utils.supabase_helpers import fetch_table, ensure_login

st.set_page_config(page_title="Overview", page_icon="📋", layout="wide")
ensure_login()

st.title("📋 Overview — All Data Tables")

def show_table(title, table, order=None):
    st.subheader(title)
    df = fetch_table(table, order=order)
    if df.empty:
        st.info("No data found.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

show_table("Google Analytics",  "ga_traffic",     order="end_date desc")
show_table("Google Ads",        "ads_metrics",     order="date desc")
show_table("Agent Postings",    "agent_postings",  order="date desc")
show_table("Google Index",      "google_index",    order="date desc")
show_table("Semrush Rank",      "semrush_rank",    order="date desc")
show_table("📉 Bounce Rate",    "bounce_rate",     order="week_start desc")
