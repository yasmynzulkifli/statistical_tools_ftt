import streamlit as st
import pandas as pd
import time
from datetime import date
from supabase import create_client

# ---- SUPABASE CONNECTION ----
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# ---- AUTHENTICATION ----
def login_page():
    st.title("🔐 FTT Metrics Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        users = st.secrets["auth"]["users"]
        if username in users and password == users[username]:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Welcome back!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Invalid credentials")

def ensure_login():
    if not st.session_state.get("logged_in"):
        login_page()
        st.stop()

# ---- SUPABASE BASIC OPERATIONS ----
def fetch_table(table, order=None, limit=1000):
    sb = get_supabase()
    q = sb.table(table).select("*").limit(limit)
    if order: q = q.order(order)
    res = q.execute()
    return pd.DataFrame(res.data)

def upsert_rows(table, rows, conflict_cols):
    sb = get_supabase()
    sb.table(table).upsert(rows, on_conflict=conflict_cols).execute()

def query_duplicates(table, keys_df, conflict_cols):
    sb = get_supabase()
    dups = []
    for _, r in keys_df.iterrows():
        f = sb.table(table).select("*")
        for c in conflict_cols:
            f = f.eq(c, str(r[c]))
        res = f.execute()
        if res.data:
            dups.append(res.data[0])
    return pd.DataFrame(dups)

# ---- CSV UPLOAD IMPORTER ----
def upload_edit_import_csv_supabase(title, key, expected_cols, date_cols,
                                    int_cols, table_name, conflict_cols, row_builder):
    st.subheader(title)
    up = st.file_uploader(f"Upload {table_name} CSV", type=["csv"], key=f"{key}_upload")
    if up is None: return
    try:
        df = pd.read_csv(up)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return

    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        return

    df = df[expected_cols]
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    st.caption("Edit cells before importing:")
    edited = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

    dups = query_duplicates(table_name, edited[conflict_cols], conflict_cols)
    has_dups = not dups.empty

    if has_dups:
        st.warning(f"{len(dups)} duplicate rows detected.")
        st.dataframe(dups, hide_index=True, use_container_width=True)
        choice = st.radio("Duplicates found – choose action:",
                          ["Keep database values (skip)", "Overwrite existing"],
                          key=f"{key}_dup_choice")
        mode = "keep" if "Keep" in choice else "overwrite"
    else:
        mode = "overwrite"

    if st.button("📥 Import to Supabase", key=f"{key}_import"):
        rows = [row_builder(r) for _, r in edited.iterrows()]
        if mode == "overwrite":
            upsert_rows(table_name, rows, conflict_cols)
            st.success(f"Imported {len(rows)} rows (duplicates overwritten).")
        else:
            new_rows = [r for i, r in enumerate(rows)
                        if edited.iloc[i][conflict_cols].to_dict() not in dups.to_dict(orient="records")]
            if new_rows:
                upsert_rows(table_name, new_rows, conflict_cols)
            st.success(f"Imported {len(new_rows)} new rows (duplicates skipped).")
        st.toast("Done ✅")
        time.sleep(0.5)
        st.rerun()
