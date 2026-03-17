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

# ---------- Date Filter Init ----------
if "date_range" not in st.session_state:
    st.session_state.date_range = (date.today() - timedelta(days=60), date.today())

def _preset_dates(preset: str):
    today = date.today()
    if preset == "Last 7 Days":
        return (today - timedelta(days=7), today)
    if preset == "Last 30 Days":
        return (today - timedelta(days=30), today)
    if preset == "Last 60 Days":
        return (today - timedelta(days=60), today)
    if preset == "Last 90 Days":
        return (today - timedelta(days=90), today)
    if preset == "Year to Date":
        return (date(today.year, 1, 1), today)
    return None

# ---------- Date Filter UI ----------
with st.expander("📆 Date Filters", expanded=False):
    start_default, end_default = st.session_state.date_range
    dr = st.date_input(
        "Select date range",
        value=(start_default, end_default),
        max_value=date.today(),
        format="YYYY-MM-DD",
        key="date_range_input",
    )

    if isinstance(dr, (list, tuple)) and len(dr) == 2:
        s, e = dr
        if s > e:
            s, e = e, s
        e = min(e, date.today())
        st.session_state.date_range = (s, e)
    else:
        st.warning("Please select both a start and end date.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    preset = st.selectbox(
        "Quick filter",
        ["— Select —", "Last 7 Days", "Last 30 Days", "Last 60 Days", "Last 90 Days", "Year to Date"],
        help="Choose a preset to auto-fill the range above.",
        key="date_quick_preset"
    )

    if preset != "— Select —":
        new_range = _preset_dates(preset)
        if new_range and new_range != st.session_state.date_range:
            st.session_state.date_range = new_range
            st.rerun()

# ---------- Use Date Range ----------
start, end = st.session_state.date_range

# Brand Filter
brands = st.multiselect("🎯 Select Brands", BRANDS, default=BRANDS)
st.caption(f"Showing data from {start} to {end}")

# Fetch data from Supabase
ga    = fetch_table("ga_traffic")
ads   = fetch_table("ads_metrics")
posts = fetch_table("agent_postings")
idx   = fetch_table("google_index")
rk    = fetch_table("semrush_rank")
br    = fetch_table("bounce_rate")

# Filter by brand & date
def filter_range(df, date_col):
    if df.empty:
        return df
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.date
    df = df[(df[date_col] >= start) & (df[date_col] <= end) & (df["brand"].isin(brands))]
    return df.sort_values([date_col, "brand"]).reset_index(drop=True)

ga    = filter_range(ga,    "end_date")
ads   = filter_range(ads,   "date")
posts = filter_range(posts, "date")
idx   = filter_range(idx,   "date")
rk    = filter_range(rk,    "date")

# Bounce rate: filter by week_start falling within selected range
def filter_bounce(df):
    if df.empty:
        return df
    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce").dt.date
    df["week_end"]   = pd.to_datetime(df["week_end"],   errors="coerce").dt.date
    df = df[(df["week_start"] >= start) & (df["week_start"] <= end) & (df["brand"].isin(brands))]
    df = df.sort_values(["week_start", "brand"]).reset_index(drop=True)
    # Create a readable week label for the x-axis
    df["week_label"] = df.apply(
        lambda r: f"{r['week_start'].strftime('%d/%m')}–{r['week_end'].strftime('%d/%m/%Y')}",
        axis=1
    )
    return df

br = filter_bounce(br)

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

# Bounce rate KPI (latest week per brand)
if not br.empty:
    last_br = br.sort_values("week_start").groupby("brand").last()["bounce_rate"]
    br_str = " | ".join([f"{b}: {v:.1f}%" for b, v in last_br.items()])
    st.metric("📉 Bounce Rate (Latest Week)", br_str)

# Chart helper
def chart(df, x, y, title, y_suffix=""):
    if df.empty:
        return
    fig = px.line(df, x=x, y=y, color="brand", title=title,
                  color_discrete_map=COLORS, markers=True)
    if y_suffix == "%":
        fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 Trends")

chart(ga,    "end_date",   "users",       "Google Analytics • Users")
chart(ads,   "date",       "clicks",      "Google Ads • Clicks")
chart(ads,   "date",       "impressions", "Google Ads • Impressions")
chart(posts, "date",       "total_listings", "Agent Postings • Total Listings")
chart(idx,   "date",       "indexed",     "Google Index • Indexed Pages")
chart(rk,    "date",       "rank",        "Semrush Rank (Lower = Better)")

# Bounce rate chart — weekly x-axis with labelled week ranges
if not br.empty:
    fig_br = px.line(
        br, x="week_label", y="bounce_rate", color="brand",
        title="Bounce Rate • Weekly Average (%)",
        color_discrete_map=COLORS, markers=True
    )
    fig_br.update_yaxes(ticksuffix="%", title="Bounce Rate (%)")
    fig_br.update_xaxes(title="Week")
    st.plotly_chart(fig_br, use_container_width=True)
else:
    st.info("📉 No bounce rate data available for the selected date range.")
