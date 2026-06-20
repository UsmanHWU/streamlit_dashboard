"""
Streamlit Dashboard — Improved Version
---------------------------------------
Improvements over original:
- Sidebar controls instead of inline widgets (cleaner layout)
- Real date-indexed time series data (not random row indices)
- Rolling average with configurable window size
- Summary statistics panel
- Proper chart labels, titles, and formatting
- Error handling for edge cases
- Modular structure with functions
"""

import streamlit as st
import pandas as pd
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="User Activity Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Constants ──────────────────────────────────────────────────────────────────
ALL_USERS = ["Alice", "Bob", "Charly"]
NUM_DAYS = 60  # days of simulated data
SEED = 42


# ── Data generation ────────────────────────────────────────────────────────────
@st.cache_data
def generate_data(users: list[str], n_days: int, seed: int) -> pd.DataFrame:
    """Generate reproducible synthetic daily activity data."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_days, freq="D")
    data = pd.DataFrame(
        rng.integers(10, 200, size=(n_days, len(users))),
        index=dates,
        columns=users,
    )
    data.index.name = "Date"
    return data


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Controls")

    selected_users = st.multiselect(
        "Select users",
        options=ALL_USERS,
        default=ALL_USERS,
        help="Choose one or more users to display.",
    )

    show_rolling = st.toggle("Show rolling average", value=True)

    window_size = st.slider(
        "Rolling window (days)",
        min_value=3,
        max_value=30,
        value=7,
        disabled=not show_rolling,
    )

    st.divider()
    st.caption("Data: 60 days of synthetic activity (seed=42)")


# ── Guard: must have at least one user selected ────────────────────────────────
if not selected_users:
    st.warning("Select at least one user from the sidebar to get started.")
    st.stop()


# ── Load & filter data ─────────────────────────────────────────────────────────
raw_data = generate_data(ALL_USERS, NUM_DAYS, SEED)[selected_users]

if show_rolling:
    display_data = raw_data.rolling(window_size, min_periods=1).mean().round(1)
    chart_label = f"{window_size}-day rolling average"
else:
    display_data = raw_data
    chart_label = "Daily activity"


# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📊 User Activity Dashboard")
st.caption(f"Showing **{chart_label}** for {', '.join(selected_users)}")

# ── Summary stats ──────────────────────────────────────────────────────────────
st.subheader("Summary", divider="gray")

cols = st.columns(len(selected_users))
for col, user in zip(cols, selected_users):
    mean_val = raw_data[user].mean()
    latest_val = raw_data[user].iloc[-1]
    delta = latest_val - raw_data[user].iloc[-8]  # vs 1 week ago
    col.metric(
        label=user,
        value=f"{latest_val:.0f}",
        delta=f"{delta:+.0f} vs last week",
        help=f"60-day average: {mean_val:.1f}",
    )

# ── Tabs: Chart / Raw data ─────────────────────────────────────────────────────
tab_chart, tab_data, tab_stats = st.tabs(["📈 Chart", "🗃️ Raw Data", "📋 Statistics"])

with tab_chart:
    st.line_chart(
        display_data,
        height=350,
        use_container_width=True,
    )
    st.caption(f"*{chart_label.capitalize()} — last {NUM_DAYS} days*")

with tab_data:
    # Show most recent first; format index as readable date string
    display_df = raw_data.sort_index(ascending=False).copy()
    display_df.index = display_df.index.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True, height=400)

with tab_stats:
    stats = raw_data.describe().round(1)
    st.dataframe(stats, use_container_width=True)
