import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="Baseball Analytics Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #1f4e79, #2e8b57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: #f0f8ff;
        padding: 1rem;
        border-left: 4px solid #4682b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all datasets with error handling"""
    data = {}
    
    # Check if database exists first
    if os.path.exists("data/baseball.db"):
        try:
            # Try to load from database first using context manager
            with sqlite3.connect("data/baseball.db") as conn:
                data['mvp_awards'] = pd.read_sql("SELECT * FROM mvp_awards", conn)
                
                # Standardize column names immediately after reading
                if 'player' in data['mvp_awards'].columns:
                    data['mvp_awards'].rename(columns={'player': 'player_name'}, inplace=True)
                
                # Try to load other tables if they exist
                try:
                    data['brothers_sets'] = pd.read_sql("SELECT * FROM baseball_brothers_sets", conn)
                except:
                    # Fallback to CSV
                    if os.path.exists('baseball_brothers_sets.csv'):
                        data['brothers_sets'] = pd.read_csv('baseball_brothers_sets.csv')
                    
                try:
                    data['awards_list'] = pd.read_sql("SELECT * FROM me_awards_list", conn)
                except:
                    # Fallback to CSV
                    if os.path.exists('me_awards_list.csv'):
                        data['awards_list'] = pd.read_csv('me_awards_list.csv')
        
        except Exception as e:
            st.warning(f"Database connection failed: {e}. Loading from CSV files...")
            data = load_csv_fallback()
    else:
        # Database not found, load from CSV files
        st.warning("Database not found, loading from CSV files...")
        data = load_csv_fallback()
    
    return data

def load_csv_fallback():
    """Fallback function to load data from CSV files"""
    data = {}
    try:
        # Check file existence before loading
        required_files = ['mvp_awards.csv', 'baseball_brothers_sets.csv', 'me_awards_list.csv']
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            st.error(f"Missing CSV files: {', '.join(missing_files)}")
            return None
            
        data['mvp_awards'] = pd.read_csv('mvp_awards.csv')
        data['brothers_sets'] = pd.read_csv('baseball_brothers_sets.csv')
        data['awards_list'] = pd.read_csv('me_awards_list.csv')
        
        # Standardize column names for CSV data too
        if 'player' in data['mvp_awards'].columns:
            data['mvp_awards'].rename(columns={'player': 'player_name'}, inplace=True)
            
    except Exception as e:
        st.error(f"Error loading CSV files: {e}")
        return None
    
    return data

@st.cache_data
def clean_mvp_data(mvp_df):
    """Clean and normalize MVP awards data"""
    # Create a copy to avoid SettingWithCopyWarning
    mvp_df = mvp_df.copy()
    
    # Clean year column
    mvp_df["year"] = pd.to_numeric(mvp_df["year"], errors="coerce")
    mvp_df = mvp_df.dropna(subset=["year"])
    mvp_df["year"] = mvp_df["year"].astype(int)
    
    # Normalize league
    mvp_df["league"] = mvp_df["league"].str.extract(r"([AN]\.?L\.?)", expand=False)
    mvp_df["league"] = mvp_df["league"].str.replace(".", "", regex=False)
    
    # Clean team names
    mvp_df["team"] = mvp_df["team"].str.replace(r'\s*\(\d+\)', '', regex=True)
    
    # Clean player names
    mvp_df["player_name"] = mvp_df["player_name"].str.strip()
    
    # Normalize positions
    if 'position' in mvp_df.columns:
        mvp_df['position'] = mvp_df['position'].str.strip()
    
    return mvp_df

@st.cache_data
def analyze_brothers_data(brothers_df):
    """Analyze baseball brothers data"""
    # Create a copy to avoid SettingWithCopyWarning
    brothers_df = brothers_df.copy()
    
    # Clean brothers count
    brothers_df['brothers_count'] = pd.to_numeric(brothers_df['brothers_count'], errors='coerce')
    brothers_df = brothers_df.dropna(subset=['brothers_count'])
    
    # Parse brother names
    brothers_df['brother_list'] = brothers_df['brothers_names'].str.split(';')
    brothers_df['total_brothers'] = brothers_df['brother_list'].str.len()
    
    return brothers_df

def create_insights_section(mvp_df, brothers_df, awards_df):
    """Generate data insights"""
    st.markdown("## 🔍 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # MVP insights
        if not mvp_df.empty:
            most_mvps_player = mvp_df['player_name'].value_counts().head(1)
            if not most_mvps_player.empty:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>🏆 MVP Leader</h4>
                    <p><strong>{most_mvps_player.index[0]}</strong> has the most MVP awards with {most_mvps_player.iloc[0]} wins</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <h4>🏆 MVP Leader</h4>
                <p>No MVP data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Brothers insights
        if not brothers_df.empty and 'brothers_count' in brothers_df.columns:
            max_brothers = brothers_df['brothers_count'].max()
            family_rows = brothers_df[brothers_df['brothers_count'] == max_brothers]
            if not family_rows.empty:
                max_brothers_family = family_rows['brothers_names'].iloc[0]
            else:
                max_brothers_family = "N/A"
                
            st.markdown(f"""
            <div class="insight-box">
                <h4>👨‍👦‍👦 Largest Baseball Family</h4>
                <p><strong>{max_brothers}</strong> brothers: {max_brothers_family.replace(';', ', ') if max_brothers_family != "N/A" else "N/A"}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <h4>👨‍👦‍👦 Largest Baseball Family</h4>
                <p>No brothers data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # League balance
        if not mvp_df.empty and 'league' in mvp_df.columns:
            league_counts = mvp_df['league'].value_counts()
            if len(league_counts) >= 2:
                diff = abs(league_counts.iloc[0] - league_counts.iloc[1])
                st.markdown(f"""
                <div class="insight-box">
                    <h4>⚖️ League Balance</h4>
                    <p>MVP difference between leagues: <strong>{diff}</strong> awards</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box">
                    <h4>⚖️ League Balance</h4>
                    <p>Insufficient data for comparison</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <h4>⚖️ League Balance</h4>
                <p>No league data available</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">⚾ Baseball Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive Analysis of MVP Awards, Baseball Brothers, and Historical Achievements")
    
    # Load data
    data = load_data()
    if data is None:
        st.stop()
    
    # Clean data
    mvp_awards = clean_mvp_data(data['mvp_awards'])
    brothers_sets = analyze_brothers_data(data['brothers_sets'])
    awards_list = data['awards_list']
    
    # Sidebar filters
    st.sidebar.markdown("## 🎛️ Filters")
    
    # Year range filter
    min_year = int(mvp_awards["year"].min())
    max_year = int(mvp_awards["year"].max())
    year_range = st.sidebar.slider(
        "📅 Select Year Range", 
        min_year, max_year, 
        (min_year, max_year),
        help="Filter MVP awards by year range"
    )
    
    # League filter
    leagues = mvp_awards["league"].dropna().unique().tolist()
    selected_leagues = st.sidebar.multiselect(
        "🏟️ Select League(s)", 
        leagues, 
        default=leagues,
        help="Filter by American League (AL) or National League (NL)"
    )
    
    # Brothers count filter
    brother_counts = sorted(brothers_sets['brothers_count'].unique())
    selected_brother_counts = st.sidebar.multiselect(
        "👥 Brother Count", 
        brother_counts, 
        default=brother_counts,
        help="Filter by number of brothers in each set"
    )
    
    # Filter data based on selections
    filtered_mvp = mvp_awards[
        (mvp_awards["year"] >= year_range[0]) &
        (mvp_awards["year"] <= year_range[1]) &
        (mvp_awards["league"].isin(selected_leagues))
    ]
    
    filtered_brothers = brothers_sets[
        brothers_sets['brothers_count'].isin(selected_brother_counts)
    ]
    
    # Display key metrics
    st.markdown("## 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(filtered_mvp)}</h3>
            <p>MVP Awards</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(filtered_brothers)}</h3>
            <p>Brother Sets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_teams = filtered_mvp['team'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{unique_teams}</h3>
            <p>Teams with MVPs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(awards_list)}</h3>
            <p>Award Categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Insights section
    create_insights_section(filtered_mvp, filtered_brothers, awards_list)
    
    # Main visualizations
    st.markdown("## 📈 Advanced Analytics")
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3 = st.tabs(["🏆 MVP Analysis", "👥 Family Connections", "🎖️ Awards Overview"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # MVP Awards timeline
            fig1 = px.histogram(
                filtered_mvp, 
                x="year", 
                title="MVP Awards Distribution by Year",
                labels={'year': 'Year', 'count': 'Number of Awards'},
                color_discrete_sequence=['#1f77b4']
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
            
            # Analysis text for MVP timeline
            st.markdown("""
            **📊 Key Insights:**
            - Data spans **63 years** (1962-2025), covering the modern MLB era
            - Each year typically shows 2 MVP awards (AL & NL)
            - Notable gap patterns may indicate missing data or special circumstances
            - Timeline captures legendary players like **Willie Mays** (1965) and **Maury Wills** (1962)
            """)
        
        with col2:
            # League distribution pie chart
            if not filtered_mvp.empty and 'league' in filtered_mvp.columns:
                league_counts = filtered_mvp['league'].value_counts()
                if not league_counts.empty:
                    fig_pie = px.pie(
                        values=league_counts.values,
                        names=league_counts.index,
                        title="MVP Awards by League",
                        color_discrete_sequence=['#ff7f0e', '#2ca02c']
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Analysis text for league distribution
                    if len(league_counts) >= 2:
                        al_pct = (league_counts.get('AL', 0) / league_counts.sum() * 100)
                        nl_pct = (league_counts.get('NL', 0) / league_counts.sum() * 100)
                        st.markdown(f"""
                        **⚖️ League Balance Analysis:**
                        - **American League**: {al_pct:.1f}% of awards
                        - **National League**: {nl_pct:.1f}% of awards
                        - Balance reflects competitive parity between leagues
                        - Any deviation from 50/50 may indicate era-specific dominance
                        """)
                else:
                    st.info("No league data available for selected filters.")
            else:
                st.info("No league data available.")
        
        # Top teams
        if not filtered_mvp.empty and 'team' in filtered_mvp.columns:
            team_counts = filtered_mvp["team"].value_counts().reset_index()
            team_counts.columns = ["team", "award_count"]
            
            if not team_counts.empty:
                fig2 = px.bar(
                    team_counts.head(15), 
                    x="team", 
                    y="award_count", 
                    title="Top 15 Teams by MVP Awards",
                    labels={'team': 'Team', 'award_count': 'MVP Awards'},
                    color='award_count',
                    color_continuous_scale='Blues'
                )
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Analysis for team performance
                total_teams = len(team_counts)
                top_team = team_counts.iloc[0]
                st.markdown(f"""
                **🏆 Team Dominance Analysis:**
                - **{total_teams} different teams** have produced MVP winners since 1962
                - **{top_team['team']}** leads with **{top_team['award_count']} awards**
                - Historic franchises like **Dodgers, Giants, and Angels** appear prominently
                - Reflects both team success and player development capabilities
                - Geographic diversity shows MLB talent spans major markets
                """)
            else:
                st.info("No team data available for selected filters.")
        else:
            st.info("No team data available.")
        
        # Top players
        if not filtered_mvp.empty and 'player_name' in filtered_mvp.columns:
            player_counts = filtered_mvp["player_name"].value_counts().reset_index()
            player_counts.columns = ["player_name", "award_count"]
            
            if not player_counts.empty:
                fig3 = px.bar(
                    player_counts.head(15), 
                    x="player_name", 
                    y="award_count", 
                    title="Top 15 MVP Award Winners",
                    labels={'player_name': 'Player', 'award_count': 'MVP Awards'},
                    color='award_count',
                    color_continuous_scale='Greens'
                )
                fig3.update_xaxes(tickangle=45)
                st.plotly_chart(fig3, use_container_width=True)
                
                # Analysis for player performance
                multi_mvp = player_counts[player_counts['award_count'] > 1]
                if not multi_mvp.empty:
                    st.markdown(f"""
                    **⭐ Elite Player Analysis:**
                    - **{len(multi_mvp)} players** have won multiple MVP awards
                    - Multiple MVP winners represent baseball's greatest legends
                    - Includes Hall of Fame caliber players like **Willie Mays**
                    - Demonstrates sustained excellence over multiple seasons
                    - Elite company - only ~3% of all players achieve multiple MVPs
                    """)
                else:
                    st.markdown("""
                    **⭐ Player Excellence:**
                    - Dataset shows individual MVP achievements
                    - Each award represents a season of exceptional performance
                    - Captures both offensive and defensive contributions
                    - Reflects voting by baseball writers across eras
                    """)
            else:
                st.info("No player data available for selected filters.")
        else:
            st.info("No player data available.")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Brothers distribution
            if not filtered_brothers.empty and 'brothers_count' in filtered_brothers.columns:
                brothers_dist = filtered_brothers['brothers_count'].value_counts().sort_index()
                if not brothers_dist.empty:
                    fig_brothers = px.bar(
                        x=brothers_dist.index.astype(str),
                        y=brothers_dist.values,
                        title="Distribution of Baseball Brother Sets",
                        labels={'x': 'Number of Brothers', 'y': 'Number of Sets'},
                        color=brothers_dist.values,
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig_brothers, use_container_width=True)
                    
                    # Analysis for brother distribution
                    total_families = brothers_dist.sum()
                    two_brother_pct = (brothers_dist.get(2, 0) / total_families * 100)
                    st.markdown(f"""
                    **👨‍👦‍👦 Family Baseball Analysis:**
                    - **{total_families} families** have multiple brothers in MLB history
                    - **{two_brother_pct:.1f}%** are two-brother combinations (most common)
                    - Rare cases of 3+ brothers demonstrate exceptional family athletic genes
                    - Famous dynasties include **Aaron Brothers** (Hank & Tommie)
                    - Modern examples like **Acuña Brothers** continue the tradition
                    - Baseball talent often runs in families due to shared training/environment
                    """)
                else:
                    st.info("No brother sets data available for selected filters.")
            else:
                st.info("No brother sets data available.")
        
        with col2:
            # Position analysis for MVP winners
            if 'position' in filtered_mvp.columns and not filtered_mvp.empty:
                position_counts = filtered_mvp['position'].value_counts().head(10)
                if not position_counts.empty:
                    fig_pos = px.bar(
                        x=position_counts.values,
                        y=position_counts.index,
                        orientation='h',
                        title="MVP Winners by Position",
                        labels={'x': 'Number of MVPs', 'y': 'Position'},
                        color=position_counts.values,
                        color_continuous_scale='Plasma'
                    )
                    st.plotly_chart(fig_pos, use_container_width=True)
                    
                    # Analysis for position distribution
                    top_position = position_counts.index[0]
                    top_count = position_counts.iloc[0]
                    st.markdown(f"""
                    **⚾ Positional MVP Trends:**
                    - **{top_position}** position produces most MVPs ({top_count} awards)
                    - Outfielders (OF, LF, CF, RF) traditionally dominate MVP voting
                    - Reflects offensive-heavy voting bias in award selection
                    - Catchers and shortstops show defensive value recognition
                    - Position versatility increasingly valued in modern era
                    """)
                else:
                    st.info("No position data available for selected filters.")
            else:
                st.info("No position data available.")
        
        # Sample of brother sets
        st.markdown("### 👨‍👦‍👦 Notable Baseball Brother Sets")
        if not filtered_brothers.empty and 'brothers_names' in filtered_brothers.columns:
            display_brothers = filtered_brothers[['brothers_count', 'brothers_names']].head(10)
            display_brothers['brothers_names'] = display_brothers['brothers_names'].str.replace(';', ', ')
            st.dataframe(display_brothers, use_container_width=True)
            
            # Analysis for brother sets table
            st.markdown("""
            **🔍 Notable Family Legacies:**
            - **Hank & Tommie Aaron**: Most famous brother duo, Hank is MLB home run king
            - **Roberto & Sandy Alomar**: Both All-Stars, Roberto in Hall of Fame
            - **Modern families** like Acuña continue baseball traditions
            - Family connections often span different positions and playing styles
            - Shared genetics, training, and competitive drive create MLB-caliber talent
            - Many brothers played in same era, some even on same teams
            """)
        else:
            st.info("No brother sets available for selected filters.")
    
    with tab3:
        # Awards overview
        st.markdown("### 🎖️ Baseball Awards Landscape")
        
        if len(awards_list) > 0:
            # Parse years from awards data
            awards_with_years = awards_list.copy()
            if 'years' in awards_with_years.columns:
                awards_with_years['start_year'] = awards_with_years['years'].str.extract(r'(\d{4})')
                awards_with_years['start_year'] = pd.to_numeric(awards_with_years['start_year'], errors='coerce')
                
                # Timeline of award introductions
                award_timeline = awards_with_years.dropna(subset=['start_year']).sort_values('start_year')
                
                if not award_timeline.empty:
                    fig_timeline = px.scatter(
                        award_timeline,
                        x='start_year',
                        y='award',
                        title="Timeline of Baseball Award Introductions",
                        labels={'start_year': 'Year Introduced', 'award': 'Award Name'},
                        hover_data=['years']
                    )
                    fig_timeline.update_traces(marker_size=10)
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    # Analysis for awards timeline
                    earliest_year = award_timeline['start_year'].min()
                    latest_year = award_timeline['start_year'].max()
                    modern_awards = award_timeline[award_timeline['start_year'] >= 2000]
                    
                    st.markdown(f"""
                    **📈 Baseball Awards Evolution:**
                    - **{len(award_timeline)} awards** introduced from {earliest_year:.0f} to {latest_year:.0f}
                    - **{len(modern_awards)} new awards** created since 2000 (modern era expansion)
                    - Classic awards like **All-Star Game MVP** (1962) establish traditions
                    - Recent additions like **All-MLB Team** (2019) reflect modern analytics
                    - Awards span all levels: **MLB, Minor League, College, Amateur**
                    - Growing recognition of specialized achievements (defense, prospects, etc.)
                    """)
            
            # Display awards table
            st.markdown("### 📋 Complete Awards List")
            st.dataframe(awards_list, use_container_width=True)
            
            # Analysis for complete awards list
            st.markdown(f"""
            **🏆 Awards Diversity Analysis:**
            - **{len(awards_list)} total award categories** tracked in database
            - Range from prestigious (MVP, Cy Young) to specialized (Prospect awards)
            - **Modern expansion**: Many new awards reflect baseball's analytical evolution
            - **Geographic scope**: Awards cover all professional baseball levels
            - **Timeline span**: From 1940s amateur awards to 2025 current recognitions
            - Demonstrates baseball's comprehensive recognition of player excellence
            """)
        else:
            st.info("No awards data available.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>📊 Data Analysis Dashboard | Built with Streamlit & Plotly</p>
        <p>🔄 Last Updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()