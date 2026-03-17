import streamlit as st
import pandas as pd
from utils.supabase_helpers import fetch_table, ensure_login

st.set_page_config(page_title="Overview", page_icon="📋", layout="wide")
ensure_login()

st.title("📋 Overview — All Data Tables")

def show_table(title, table, date_col=None):
    st.subheader(title)
    df = fetch_table(table)
    if df.empty:
        st.info("No data found.")
    else:
        # Sort by date column descending using pandas — avoids Supabase order param issues
        if date_col and date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df.sort_values(date_col, ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

show_table("Google Analytics",  "ga_traffic",     date_col="end_date")
show_table("Google Ads",        "ads_metrics",     date_col="date")
show_table("Agent Postings",    "agent_postings",  date_col="date")
show_table("Google Index",      "google_index",    date_col="date")
show_table("Semrush Rank",      "semrush_rank",    date_col="date")
show_table("📉 Bounce Rate",    "bounce_rate",     date_col="week_start")
