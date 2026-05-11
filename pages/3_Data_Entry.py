import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.supabase_helpers import (
    ensure_login, upsert_rows, upload_edit_import_csv_supabase
)

st.set_page_config(page_title="Data Entry", page_icon="✍️", layout="wide")
ensure_login()

st.title("✍️ Data Entry — Input or Import Data")

BRANDS = ["FindHouse", "CheckValue"]
AGENT_BRANDS = ["FindHouse"]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Google Analytics", "🎯 Google Ads", "🏠 Agent Postings",
    "🔎 Google Index", "📊 Semrush Rank", "📉 Bounce Rate"
])

# ---- GOOGLE ANALYTICS ----
with tab1:
    brand = st.selectbox("Brand", BRANDS, key="ga_b")
    daterange = st.date_input("Start & End Date", [date.today()-timedelta(days=7), date.today()])
    users = st.number_input("Users", min_value=0, key="ga_u")
    if st.button("💾 Save", key="ga_s"):
        start, end = daterange
        row = {"brand": brand, "start_date": str(start), "end_date": str(end), "users": int(users)}
        upsert_rows("ga_traffic", [row], ["brand", "start_date", "end_date"])
        st.success("✅ GA data saved!")

    st.markdown("---")
    upload_edit_import_csv_supabase(
        "Upload Google Analytics CSV", "ga",
        ["brand", "start_date", "end_date", "users"],
        ["start_date", "end_date"], ["users"],
        "ga_traffic", ["brand", "start_date", "end_date"],
        lambda r: {
            "brand": r["brand"], "start_date": str(r["start_date"]),
            "end_date": str(r["end_date"]), "users": int(r["users"])
        }
    )

# ---- GOOGLE ADS ----
with tab2:
    brand = st.selectbox("Brand ", BRANDS, key="ads_b")
    d = st.date_input("Date", key="ads_d")
    clicks = st.number_input("Clicks", min_value=0, key="ads_c")
    imps = st.number_input("Impressions", min_value=0, key="ads_i")
    if st.button("💾 Save", key="ads_s"):
        row = {"brand": brand, "date": str(d), "clicks": int(clicks), "impressions": int(imps)}
        upsert_rows("ads_metrics", [row], ["brand", "date"])
        st.success("✅ Ads data saved!")

    st.markdown("---")
    upload_edit_import_csv_supabase(
        "Upload Google Ads CSV", "ads",
        ["brand", "date", "clicks", "impressions"],
        ["date"], ["clicks", "impressions"],
        "ads_metrics", ["brand", "date"],
        lambda r: {
            "brand": r["brand"], "date": str(r["date"]),
            "clicks": int(r["clicks"]), "impressions": int(r["impressions"])
        }
    )

# ---- AGENT POSTINGS ----
with tab3:
    brand = st.selectbox("Brand  ", AGENT_BRANDS, key="p_b")
    d = st.date_input("Date", key="p_d")
    sale = st.number_input("Sale Listings", min_value=0)
    rent_ = st.number_input("Rent Listings", min_value=0)
    auction = st.number_input("Auction Listings", min_value=0)
    total = int(sale) + int(rent_) + int(auction)
    if st.button("💾 Save", key="p_s"):
        row = {
            "brand": brand, "date": str(d), "total_listings": total,
            "sale_listings": int(sale), "rent_listings": int(rent_),
            "auction_listings": int(auction)
        }
        upsert_rows("agent_postings", [row], ["brand", "date"])
        st.success("✅ Posting data saved!")

    st.markdown("---")
    upload_edit_import_csv_supabase(
        "Upload Agent Postings CSV", "posts",
        ["brand", "date", "total_listings", "sale_listings", "rent_listings", "auction_listings"],
        ["date"],
        ["total_listings", "sale_listings", "rent_listings", "auction_listings"],
        "agent_postings", ["brand", "date"],
        lambda r: {
            "brand": r["brand"], "date": str(r["date"]),
            "total_listings": int(r["total_listings"]),
            "sale_listings": int(r["sale_listings"]),
            "rent_listings": int(r["rent_listings"]),
            "auction_listings": int(r["auction_listings"])
        }
    )

# ---- GOOGLE INDEX ----
with tab4:
    brand = st.selectbox("Brand   ", BRANDS, key="idx_b")
    d = st.date_input("Date", key="idx_d")
    indexed = st.number_input("Indexed Pages", min_value=0, key="idx_i")
    if st.button("💾 Save", key="idx_s"):
        row = {"brand": brand, "date": str(d), "indexed": int(indexed)}
        upsert_rows("google_index", [row], ["brand", "date"])
        st.success("✅ Google Index saved!")

    st.markdown("---")
    upload_edit_import_csv_supabase(
        "Upload Google Index CSV", "idx",
        ["brand", "date", "indexed"],
        ["date"], ["indexed"],
        "google_index", ["brand", "date"],
        lambda r: {
            "brand": r["brand"], "date": str(r["date"]),
            "indexed": int(r["indexed"])
        }
    )

# ---- SEMRUSH RANK ----
with tab5:
    brand = st.selectbox("Brand    ", BRANDS, key="rk_b")
    d = st.date_input("Date", key="rk_d")
    rank = st.number_input("Rank (lower=better)", min_value=1, key="rk_r")
    if st.button("💾 Save", key="rk_s"):
        row = {"brand": brand, "date": str(d), "rank": int(rank)}
        upsert_rows("semrush_rank", [row], ["brand", "date"])
        st.success("✅ Semrush Rank saved!")

    st.markdown("---")
    upload_edit_import_csv_supabase(
        "Upload Semrush Rank CSV", "rk",
        ["brand", "date", "rank"],
        ["date"], ["rank"],
        "semrush_rank", ["brand", "date"],
        lambda r: {
            "brand": r["brand"], "date": str(r["date"]),
            "rank": int(r["rank"])
        }
    )

# ---- BOUNCE RATE ----
with tab6:
    st.markdown("##### 📉 Weekly Bounce Rate")
    st.caption("Enter the average bounce rate for a weekly date range (same format as Google Analytics).")

    brand = st.selectbox("Brand     ", BRANDS, key="br_b")

    # GA-style single range picker — identical pattern to Google Analytics tab
    _last_monday = date.today() - timedelta(days=date.today().weekday() + 7)
    _last_sunday  = date.today() - timedelta(days=date.today().weekday() + 1)
    week_range = st.date_input(
        "Start & End Date",
        value=[_last_monday, _last_sunday],
        max_value=date.today(),
        format="YYYY/MM/DD",
        key="br_range"
    )

    bounce = st.number_input(
        "Bounce Rate (%)",
        min_value=0.0, max_value=100.0,
        step=0.1, format="%.2f",
        key="br_val",
        help="Enter as a percentage, e.g. 10 for 10%"
    )

    if st.button("💾 Save", key="br_s"):
        if not isinstance(week_range, (list, tuple)) or len(week_range) != 2:
            st.error("❌ Please select both a start and end date.")
        else:
            week_start, week_end = week_range
            if week_start > week_end:
                st.error("❌ Week Start must be before Week End.")
            else:
                st.caption(
                    f"📅 **{week_start.strftime('%d/%m/%Y')} – {week_end.strftime('%d/%m/%Y')}**"
                    f"  |  Bounce Rate: **{bounce:.1f}%**"
                )
                row = {
                    "brand": brand,
                    "week_start": str(week_start),
                    "week_end": str(week_end),
                    "bounce_rate": float(bounce)
                }
                upsert_rows("bounce_rate", [row], ["brand", "week_start"])
                st.success("✅ Bounce rate saved!")

    st.markdown("---")
    upload_edit_import_csv_supabase(
        "Upload Bounce Rate CSV", "br",
        ["brand", "week_start", "week_end", "bounce_rate"],
        ["week_start", "week_end"], ["bounce_rate"],
        "bounce_rate", ["brand", "week_start"],
        lambda r: {
            "brand": r["brand"],
            "week_start": str(r["week_start"]),
            "week_end": str(r["week_end"]),
            "bounce_rate": float(r["bounce_rate"])
        }
    )
