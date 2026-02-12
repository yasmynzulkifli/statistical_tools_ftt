import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_helpers import ensure_login, get_supabase

st.set_page_config(
    page_title="Whatsapp Blast",
    page_icon="💬",
    layout="wide"
)

# --- Login ---
ensure_login()

# --- Import required variables ---
BRANDS = ["FindHouse", "CheckValue"]

# Helper function to format large numbers
def format_compact(num):
    """Format large numbers in compact notation (e.g., 1.5M)"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

# Fetch data from Supabase - REMOVED @st.cache_data to always get fresh data
def fetch_data(table: str, brand: str, limit: int = None, order_by: str = "date"):
    """Fetch data from Supabase table"""
    try:
        supabase = get_supabase()
        query = supabase.table(table).select("*").eq("brand", brand).order(order_by, desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching data from {table}: {e}")
        return pd.DataFrame()

# --- Page Header ---
st.title("💬 Whatsapp Blast")
st.markdown("Generate printable summaries for WhatsApp marketing campaigns")

# --- Refresh Button ---
col1, col2, col3 = st.columns([2, 1, 1])
with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col3:
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# --- Printable Summary Section ---
st.markdown("---")
st.subheader("🧾 Printable Summary")

LATEST_N = 4

# Loading indicator
with st.spinner("Loading latest data..."):
    for brand in BRANDS:
        st.markdown(f"**{brand}**")
        block = []
        separator = "-" * 20
        block.append(separator)
        block.append(brand)
        block.append(separator)
        
        # Google Analytics - uses end_date for ordering
        ga = fetch_data("ga_traffic", brand, LATEST_N, order_by="end_date")
        
        if not ga.empty:
            ga = ga.sort_values("end_date")
            block.append("*Google Analytics*:")
            for _, r in ga.iterrows():
                start = pd.to_datetime(r['start_date']).strftime("%d/%m/%Y")
                end = pd.to_datetime(r['end_date']).strftime("%d/%m/%Y")
                block.append(f"{start}–{end}: {int(r['users'])}")
        
        # Google Ads - uses date
        ads = fetch_data("ads_metrics", brand, LATEST_N, order_by="date")
        
        if not ads.empty:
            ads = ads.sort_values("date")
            block.append("")
            block.append("*Google Ads*:")
            for _, r in ads.iterrows():
                d = pd.to_datetime(r['date']).strftime("%d/%m/%Y")
                block.append(f"{d}: [{int(r['clicks'])},{int(r['impressions'])}]")
        
        # Agent Postings - uses date
        posts = fetch_data("agent_postings", brand, LATEST_N, order_by="date")
        
        if not posts.empty:
            posts = posts.sort_values("date")
            block.append("")
            block.append("*Agent Postings*:")
            for _, r in posts.iterrows():
                d = pd.to_datetime(r['date']).strftime("%d/%m/%Y")
                block.append(f"{d}: {int(r['total_listings'])} "
                           f"[{int(r['sale_listings'])},{int(r['rent_listings'])},{int(r['auction_listings'])}]")
        
        # Google Index - uses date
        idx = fetch_data("google_index", brand, LATEST_N, order_by="date")
        
        if not idx.empty:
            idx = idx.sort_values("date")
            block.append("")
            block.append("*Google Index*:")
            for _, r in idx.iterrows():
                d = pd.to_datetime(r['date']).strftime("%d/%m/%Y")
                block.append(f"{d}: {int(r['indexed'])}")
        
        # REMOVED: Semrush Rank section
        
        st.code("\n".join(block))

st.markdown("---")
st.info("💡 **Tip:** Click the 'Refresh Data' button above to load the latest data from the database.")
