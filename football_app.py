import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Football EDA Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("filtered_football_data.csv")
        return df
    except Exception as e:
        st.error(f"⚠️ Couldn’t load data: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data available—check your CSV path/name.")
    st.stop()

st.sidebar.header("Filter Options")
teams = st.sidebar.multiselect(
    "Select Teams", options=df["Team"].unique(), default=df["Team"].unique()[:5]
)
season_min, season_max = int(df["Season"].min()), int(df["Season"].max())
season_range = st.sidebar.slider("Season Range", season_min, season_max, (season_min, season_max))
metric_display = st.sidebar.selectbox(
    "Metric to Plot",
    ["Offensive Plays", "Offensive Yards", "Total Touchdowns", "Turnovers Lost"]
)
plot_type = st.sidebar.radio("Plot Type", ["Line Chart", "Bar Chart"])

metric_map = {
    "Offensive Plays": "Off.Plays",
    "Offensive Yards":  "Off.Yards",
    "Total Touchdowns":"Total.TDs",
    "Turnovers Lost":   "Turnovers Lost"
}
metric = metric_map[metric_display]

with st.expander("📖 How to use this dashboard"):
    st.write("""
    1. Filter teams, seasons, metric & chart type in the sidebar.  
    2. **Overview** tab shows your selected metric averaged by season.  
    3. **Team Analysis** tab shows that metric for one team over time.
    """)

overview_tab, team_tab = st.tabs(["Overview", "Team Analysis"])

with overview_tab:
    st.subheader(f"{metric_display} by Season")
    df_over = (
        df[df["Team"].isin(teams) & 
           df["Season"].between(*season_range)]
        .groupby("Season")[metric]
        .mean()
        .reset_index()
    )
    fig = (
        px.line(df_over, x="Season", y=metric, markers=True, title=f"{metric_display} Over Seasons")
        if plot_type=="Line Chart"
        else px.bar(df_over, x="Season", y=metric, title=f"{metric_display} Over Seasons")
    )
    st.plotly_chart(fig, use_container_width=True)

with team_tab:
    st.subheader(f"{metric_display} for a Single Team")
    chosen_team = st.selectbox("Pick a Team", options=teams)
    df_team = df[
        (df["Team"] == chosen_team) &
        df["Season"].between(*season_range)
    ]
    fig2 = px.line(
        df_team.sort_values("Season"), x="Season", y=metric, markers=True,
        title=f"{chosen_team}: {metric_display} Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)
