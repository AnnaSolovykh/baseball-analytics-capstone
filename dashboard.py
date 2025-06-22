import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

conn = sqlite3.connect("data/baseball.db")

mvp_awards = pd.read_sql("SELECT * FROM mvp_awards", conn)

# Clean and normalize columns
mvp_awards["year"] = pd.to_numeric(mvp_awards["year"], errors="coerce")
mvp_awards = mvp_awards.dropna(subset=["year"])
mvp_awards["year"] = mvp_awards["year"].astype(int)

# Normalize league: extract only "A.L." or "N.L." → "AL"/"NL"
mvp_awards["league"] = mvp_awards["league"].str.extract(r"([AN]\.?L\.?)", expand=False)
mvp_awards["league"] = mvp_awards["league"].str.replace(".", "", regex=False)

# Sidebar filters
st.sidebar.title("Filters")

min_year = int(mvp_awards["year"].min())
max_year = int(mvp_awards["year"].max())
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

leagues = mvp_awards["league"].dropna().unique().tolist()
selected_leagues = st.sidebar.multiselect("Select League(s)", leagues, default=leagues)

# Filter data
filtered_df = mvp_awards[
    (mvp_awards["year"] >= year_range[0]) &
    (mvp_awards["year"] <= year_range[1]) &
    (mvp_awards["league"].isin(selected_leagues))
]

# Title
st.title("🏆 Baseball MVP Awards Dashboard")

# Chart 1: Awards per year
fig1 = px.histogram(filtered_df, x="year", title="MVP Awards per Year")
st.plotly_chart(fig1)

# Chart 2: Top 15 teams
team_counts = filtered_df["team"].value_counts().reset_index()
team_counts.columns = ["team", "team_award_count"]
fig2 = px.bar(team_counts.head(15), x="team", y="team_award_count", title="Top 15 Teams by MVP Awards")
st.plotly_chart(fig2)

# Chart 3: Top 15 players
player_counts = filtered_df["player_name"].value_counts().reset_index()
player_counts.columns = ["player_name", "award_count"]
fig3 = px.bar(player_counts.head(15), x="player_name", y="award_count", title="Top 15 MVP Award Winners")
st.plotly_chart(fig3)

conn.close()
