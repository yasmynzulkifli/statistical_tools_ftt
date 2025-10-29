# ---- CSV UPLOAD IMPORTER (keep, with small hardening) ----
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

    # Parse dates + integers
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    st.caption("Edit cells before importing:")
    edited = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

    # For duplicate check, pass exactly the conflict columns
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
            # Keep DB values: only insert rows that do NOT exist
            if has_dups:
                # Build a set of existing composite keys for fast membership checks
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
