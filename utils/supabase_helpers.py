import streamlit as st
import pandas as pd
import time
from datetime import date, datetime
from supabase import create_client
from postgrest.exceptions import APIError

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
def _to_jsonable(row: dict) -> dict:
    """Convert Python/pandas values to JSON-safe ones for Supabase."""
    out = {}
    for k, v in row.items():
        # NaN -> None
        if isinstance(v, float) and v != v:
            out[k] = None
            continue
        # pandas Timestamp -> datetime/date
        if isinstance(v, pd.Timestamp):
            v = v.to_pydatetime()
        # date/datetime -> ISO string
        if isinstance(v, (date, datetime)):
            v = (v.date() if isinstance(v, datetime) else v).isoformat()
        out[k] = v
    return out

def fetch_table(table, order=None, limit=1000):
    sb = get_supabase()
    q = sb.table(table).select("*").limit(limit)
    if order:
        q = q.order(order)
    res = q.execute()
    return pd.DataFrame(res.data)

def upsert_rows(table, rows, conflict_cols):
    """Perform UPSERT (insert or update) with better error handling."""
    sb = get_supabase()

    # Convert list → comma-separated string
    if isinstance(conflict_cols, (list, tuple)):
        conflict_cols = ",".join(conflict_cols)

    clean_rows = [_to_jsonable(r) for r in rows]

    try:
        return sb.table(table).upsert(
            clean_rows,
            on_conflict=conflict_cols,
            returning="minimal"
        ).execute()
    except APIError as e:
        st.error("⚠️ Supabase APIError during UPSERT")
        msg = getattr(e, "message", None) or str(e)
        det = getattr(e, "details", None)
        st.code(msg)
        if det:
            st.caption("Details:")
            st.code(str(det))
        raise

def query_duplicates(table, keys_df, conflict_cols):
    sb = get_supabase()
    dups = []
    if keys_df.empty:
        return pd.DataFrame()
    keys_df = keys_df.copy()
    for c in conflict_cols:
        if "date" in c.lower():
            keys_df[c] = pd.to_datetime(keys_df[c], errors="coerce").dt.date.astype(str)
        else:
            keys_df[c] = keys_df[c].astype(str)
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
    if up is None:
        return
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

    try:
        dups = query_duplicates(table_name, edited[conflict_cols], conflict_cols)
        has_dups = not dups.empty
    except Exception as e:
        has_dups = False
        st.warning(f"Duplicate check skipped due to error: {e}")

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
            if has_dups:
                key_cols = conflict_cols if isinstance(conflict_cols, list) else [c.strip() for c in conflict_cols.split(",")]
                existing = {tuple(str(d[k]) for k in key_cols) for d in dups.to_dict(orient="records")}
                new_rows = []
                for i, r in enumerate(rows):
                    r_clean = _to_jsonable(r)
                    comp_key = tuple(str(r_clean[k]) for k in key_cols)
                    if comp_key not in existing:
                        new_rows.append(r)
                if new_rows:
                    upsert_rows(table_name, new_rows, conflict_cols)
                st.success(f"Imported {len(new_rows)} new rows (duplicates skipped).")
            else:
                st.info("No duplicates detected; nothing to skip.")
        st.toast("Done ✅")
        time.sleep(0.5)
        st.rerun()
