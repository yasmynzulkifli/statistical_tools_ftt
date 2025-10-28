# 🏠 FTT Metrics Dashboard (Supabase + Streamlit)

A multi-page analytics dashboard for **FindTeam Technology** — tracking key digital metrics across **Google Analytics**, **Google Ads**, **Agent Postings**, **Google Index**, and **Semrush Rank** — all stored in **Supabase** and visualized in **Streamlit**.

---

## 🚀 Features

✅ **Multi-page Streamlit app**
- **Dashboard:** charts & KPIs  
- **Overview:** tabular view of all data  
- **Data Entry:** manual input + CSV upload  

✅ **Supabase Integration**
- All data stored in cloud tables  
- Duplicate check before import  
- Option to “Keep Database” or “Overwrite”  

✅ **Authentication**
- Simple user login via `.streamlit/secrets.toml`  

✅ **Fully deployable on Streamlit Cloud**
- Persistent database  
- No local storage needed  

---

## 📁 Folder Structure

```
ftt_supabase_app/
│
├── app.py                        # main entry
├── utils/
│   └── supabase_helpers.py       # Supabase + login + importer logic
└── pages/
    ├── 1_Dashboard.py            # charts + KPIs
    ├── 2_Overview.py             # all tables
    └── 3_Data_Entry.py           # manual entry + CSV upload
```

---

## ⚙️ Requirements

- Python 3.10+
- Packages:
  ```bash
  pip install streamlit pandas plotly supabase
  ```

## ▶️ Run Locally

```bash
streamlit run app.py
```

Then open the local URL (usually `http://localhost:8501`).

---

## ☁️ Deploy on Streamlit Cloud

1. Push this folder to a **GitHub repo** (e.g. `ftt_supabase_app`)  
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**  
3. Select the repo & branch, set `app.py` as the main file  
4. Add the contents of your `.streamlit/secrets.toml` to **Secrets** in Streamlit Cloud  

Done! 🎉

---

## 🧠 Notes

- All uploads and manual entries are written directly to Supabase  
- Duplicates are checked using `brand + date` keys  
- CSV upload allows live editing before import  
- Login credentials are stored safely in `secrets.toml`  
- You can add new data sources easily by following the pattern in `3_Data_Entry.py`

---

## 👨‍💻 Maintainer

**FindTeam Technology — Growth Team**  
Developer: *Nur Yasmyn Zulkifli*  
