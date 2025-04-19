import streamlit as st
import pandas as pd
from datetime import datetime

# --- Data Loading ---
@st.cache_data
def load_standups(path="logs/standup_updates.jsonl"):
    try:
        df = pd.read_json(path, lines=True)
    except Exception:
        st.error(f"Could not load data from {path}")
        return pd.DataFrame()
    # Ensure timestamp column exists
    if "timestamp" not in df.columns:
        st.warning("No timestamp column found. Make sure /submit emits it.")
        return pd.DataFrame()
    # Parse timestamp into datetime and drop invalid entries
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors='coerce')
    df = df.dropna(subset=["timestamp"]).copy()
    # Extract date for grouping
    df["date"] = df["timestamp"].dt.date
    return df

# --- App layout ---
st.title("📊 Standup Dashboard")

df = load_standups()
if df.empty:
    st.info("No standup entries available.")
    st.stop()

# Sidebar: Date selection
dates = sorted(df["date"].unique(), reverse=True)
selected_date = st.sidebar.selectbox("Select date", dates)

# Filter by date
filtered = df[df["date"] == selected_date]
st.header(f"Standup Updates for {selected_date}")

# Display each entry
for _, row in filtered.iterrows():
    st.subheader(f"👤 {row['user']}")
    st.markdown(f"**Yesterday:** {row['yesterday']}")
    st.markdown(f"**Today:** {row['today']}")
    st.markdown(f"**Blockers:** {row['blockers']}")
    st.markdown("---")

# Optional: Summary stats
st.sidebar.markdown("---")
st.sidebar.subheader("Stats")
st.sidebar.write(f"Total submissions: {len(filtered)}")

# Run with:
# streamlit run dashboard.py