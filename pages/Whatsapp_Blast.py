import streamlit as st
import pandas as pd
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

# Fetch data from Supabase
@st.cache_data(ttl=300)
def fetch_data(table: str, brand: str, limit: int = None, _cache_version: int = 0):
    """Fetch data from Supabase table"""
    try:
        supabase = get_supabase()
        query = supabase.table(table).select("*").eq("brand", brand).order("date", desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching data from {table}: {e}")
        return pd.DataFrame()

# Cache version for force refresh
cache_v = st.session_state.get("cache_version", 0)

# --- Page Header ---
st.title("💬 Whatsapp Blast")
st.markdown("Generate printable summaries for WhatsApp marketing campaigns")

# --- Printable Summary Section ---
st.markdown("---")
st.subheader("🧾 Printable Summary")

LATEST_N = 4

for brand in BRANDS:
    st.markdown(f"*{brand}*")
    block = []
    separator = "-" * 20
    block.append(separator)
    block.append(brand)
    block.append(separator)
    
    # Google Analytics
    ga = fetch_data("ga_traffic", brand, LATEST_N, _cache_version=cache_v)
    
    if not ga.empty:
        ga = ga.sort_values("end_date")
        block.append("*Google Analytics*:")
        for _, r in ga.iterrows():
            start = pd.to_datetime(r['start_date']).strftime("%d/%m/%Y")
            end = pd.to_datetime(r['end_date']).strftime("%d/%m/%Y")
            block.append(f"{start}–{end}: {int(r['users'])}")
    
    # Google Ads
    ads = fetch_data("ads_metrics", brand, LATEST_N, _cache_version=cache_v)
    
    if not ads.empty:
        ads = ads.sort_values("date")
        block.append("")
        block.append("*Google Ads*:")
        for _, r in ads.iterrows():
            d = pd.to_datetime(r['date']).strftime("%d/%m/%Y")
            block.append(f"{d}: [{int(r['clicks'])},{int(r['impressions'])}]")
    
    # Agent Postings
    posts = fetch_data("agent_postings", brand, LATEST_N, _cache_version=cache_v)
    
    if not posts.empty:
        posts = posts.sort_values("date")
        block.append("")
        block.append("*Agent Postings*:")
        for _, r in posts.iterrows():
            d = pd.to_datetime(r['date']).strftime("%d/%m/%Y")
            block.append(f"{d}: {int(r['total_listings'])} "
                       f"[{int(r['sale_listings'])},{int(r['rent_listings'])},{int(r['auction_listings'])}]")
    
    # Google Index
    idx = fetch_data("google_index", brand, LATEST_N, _cache_version=cache_v)
    
    if not idx.empty:
        idx = idx.sort_values("date")
        block.append("")
        block.append("*Google Index*:")
        for _, r in idx.iterrows():
            d = pd.to_datetime(r['date']).strftime("%d/%m/%Y")
            block.append(f"{d}: {int(r['indexed'])}")
    
    # Semrush Rank
    rk = fetch_data("semrush_rank", brand, 1, _cache_version=cache_v)
    
    if not rk.empty:
        r = rk.iloc[0]
        block.append("")
        block.append(f"*SEMRUSH Rank*: {format_compact(int(r['rank']))}")
    
    st.code("\n".join(block))
