import streamlit as st
import pandas as pd
import altair as alt

# --- Page setup ---
st.set_page_config(page_title="StatsBomb Touch & OBV Analysis", layout="wide")

st.title("⚽ StatsBomb Touch & OBV Analysis Dashboard")
st.markdown("""
Explore player performance across competitions using **Touches per 90** and **OBV metrics**.  
Use the filters on the sidebar to select competitions, positions, teams, ages, and usage.
""")

# --- Load data ---
@st.cache_data
def load_data():
    return pd.read_excel("touch_analysis.xlsx")

df = load_data()

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    
    competitions = st.multiselect(
        "Select Competitions", sorted(df["Competition"].dropna().unique()), default=None
    )
    positions = st.multiselect(
        "Select Positions", sorted(df["Position"].dropna().unique()), default=None
    )
    teams = st.multiselect(
        "Select Teams", sorted(df["Team"].dropna().unique()), default=None
    )

    # Age filter
    min_age = int(df["Age"].min())
    max_age = int(df["Age"].max())
    age_range = st.slider("Select Age Range", min_age, max_age, (min_age, max_age))

    # Usage filter
    min_usage = int(df["Usage"].min())
    max_usage = int(df["Usage"].max())
    usage_range = st.slider("Select Usage Range (%)", min_usage, max_usage, (20, max_usage))

# --- Apply filters ---
filtered = df.copy()

if competitions:
    filtered = filtered[filtered["Competition"].isin(competitions)]
if positions:
    filtered = filtered[filtered["Position"].isin(positions)]
if teams:
    filtered = filtered[filtered["Team"].isin(teams)]

filtered = filtered[
    (filtered["Age"].between(age_range[0], age_range[1])) &
    (filtered["Usage"].between(usage_range[0], usage_range[1]))
]

# --- Key metrics ---
st.subheader("Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Players", len(filtered))
col2.metric("Avg Touches per 90", round(filtered["Touches per 90"].mean(), 1))
col3.metric("Avg OBV", round(filtered["OBV"].mean(), 3))

# --- Main data table ---
st.subheader("Player Data")
st.dataframe(
    filtered[
        [
            "Player Name", "Team", "Competition", "Position", "Age", "Usage",
            "Touches per 90", "OBV Rank", "Pass OBV Rank",
            "Dribble & Carry OBV Rank", "Shot OBV Rank"
        ]
    ].sort_values("Touches per 90", ascending=False),
    use_container_width=True,
)

# --- Chart: Touches per 90 vs OBV ---
st.subheader("Touches per 90 vs OBV Rank")

chart = (
    alt.Chart(filtered)
    .mark_circle(size=80, opacity=0.7)
    .encode(
        x=alt.X("Touches per 90", title="Touches per 90"),
        y=alt.Y("OBV Rank", title="OBV Rank (0–100)"),
        color="Position",
        tooltip=[
            "Player Name", "Team", "Competition", "Position",
            "Touches per 90", "OBV", "OBV Rank"
        ],
    )
    .interactive()
)

st.altair_chart(chart, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit and StatsBomb data.")
