import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from utils.supabase_helpers import fetch_table, ensure_login

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
ensure_login()

st.title("📊 Dashboard — FTT Metrics")

BRANDS = ["FindHouse", "CheckValue"]
COLORS = {"FindHouse": "#FF4800", "CheckValue": "#48cae4"}

today = date.today()
start = today - timedelta(days=60)
brands = st.multiselect("🎯 Select Brands", BRANDS, default=BRANDS)
st.caption(f"Showing data from {start} to {today}")

# Fetch data from Supabase
ga = fetch_table("ga_traffic")
ads = fetch_table("ads_metrics")
posts = fetch_table("agent_postings")
idx = fetch_table("google_index")
rk = fetch_table("semrush_rank")

# Filter by brand & date
def filter_range(df, date_col):
    if df.empty: return df
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.date
    df = df[(df[date_col] >= start) & (df[date_col] <= today) & (df["brand"].isin(brands))]
    # SORT BY DATE AND BRAND
    return df.sort_values([date_col, "brand"]).reset_index(drop=True)

ga = filter_range(ga, "end_date")
ads = filter_range(ads, "date")
posts = filter_range(posts, "date")
idx = filter_range(idx, "date")
rk = filter_range(rk, "date")

# KPIs
c1, c2, c3, c4 = st.columns(4)
if not ga.empty:
    last = ga.groupby("brand")["users"].last()
    c1.metric("Users", " | ".join([f"{b}: {int(v):,}" for b, v in last.items()]))
if not ads.empty:
    clicks = ads.groupby("brand")["clicks"].sum()
    c2.metric("Clicks", " | ".join([f"{b}: {int(v):,}" for b, v in clicks.items()]))
if not posts.empty:
    total = posts.groupby("brand")["total_listings"].last()
    c3.metric("Listings", " | ".join([f"{b}: {int(v):,}" for b, v in total.items()]))
if not idx.empty:
    last_i = idx.groupby("brand")["indexed"].last()
    c4.metric("Indexed Pages", " | ".join([f"{b}: {int(v):,}" for b, v in last_i.items()]))

# Chart helper
def chart(df, x, y, title):
    if df.empty: return
    fig = px.line(df, x=x, y=y, color="brand", title=title,
                  color_discrete_map=COLORS)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 Trends")

chart(ga, "end_date", "users", "Google Analytics • Users")
chart(ads, "date", "clicks", "Google Ads • Clicks")
chart(ads, "date", "impressions", "Google Ads • Impressions")
chart(posts, "date", "total_listings", "Agent Postings • Total Listings")
chart(idx, "date", "indexed", "Google Index • Indexed Pages")
chart(rk, "date", "rank", "Semrush Rank (Lower = Better)")
