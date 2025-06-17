# Baseball Analytics Capstone Project

## Project Overview

This is a comprehensive data analysis pipeline that scrapes baseball history data, stores it in a database, and presents insights through an interactive dashboard. The project demonstrates web scraping, data processing, database management, and data visualization skills.

## Project Structure

```
baseball-analytics-capstone/
├── scraper.py              # Web scraping program
├── database_import.py      # Database import program  
├── database_query.py       # Command-line query interface
├── dashboard.py            # Interactive dashboard
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── data/
│   ├── raw/               # Scraped CSV files
│   │   ├── events.csv
│   │   ├── players.csv
│   │   └── statistics.csv
│   └── processed/         # SQLite database
│       └── baseball.db
└── baseball_env/          # Virtual environment
```

## Features

### 1. Web Scraping (scraper.py)
- **Source**: Baseball-Reference.com
- **Compliance**: Follows robots.txt rules (3-second crawl delay)
- **Data Collection**:
  - 10 historical events (2020-2024)
  - 7 career leaders and statistics  
  - Team performance data
- **Output**: 3 CSV files in `data/raw/`

### 2. Database Import (database_import.py)
- **Database**: SQLite with 3 tables (events, players, statistics)
- **Data Cleaning**: Handles missing values, duplicates, and validation
- **Performance**: Creates indexes for fast queries
- **Error Handling**: Comprehensive logging and validation

### 3. Database Query CLI (database_query.py)
- **Features**: Interactive command-line interface
- **Queries**: Supports JOIN operations and filtering
- **Commands**: Events by year, players by team, custom SQL
- **Output**: Formatted tables with summaries

### 4. Interactive Dashboard (dashboard.py)
- **Framework**: Streamlit
- **Visualizations**: 3+ interactive charts
- **Features**: Dropdowns, sliders, dynamic filtering
- **Deployment**: Ready for Streamlit.io or Render

## Installation

### Prerequisites
- Python 3.9+
- Chrome browser (for web scraping)

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd baseball-analytics-capstone
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv baseball_env
   source baseball_env/bin/activate  # Mac/Linux
   # or
   baseball_env\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Scrape Data
```bash
python3 scraper.py
```
**Results:**
- Scrapes baseball data from Baseball-Reference.com
- Follows robots.txt compliance (3-second delay)
- Creates CSV files in `data/raw/`

### Step 2: Import to Database
```bash
python3 database_import.py
```
**Results:**
- Creates SQLite database at `data/processed/baseball.db`
- Imports and cleans all CSV data
- Creates performance indexes

### Step 3: Query Database
```bash
python3 database_query.py --interactive
```
**Available Commands:**
- `events <year>` - Get events for specific year
- `players <team>` - Get players for team
- `join` - Join events with statistics
- `summary` - Show yearly summary
- `custom` - Execute custom SQL

### Step 4: Launch Dashboard
```bash
streamlit run dashboard.py
```
**Features:**
- Interactive visualizations
- Year and category filters
- Real-time data updates

## Data Sources

### Scraped Data Results
- **Events**: 10 records (MLB seasons, World Series 2020-2024)
- **Players**: 7 career leaders (batting, pitching statistics)
- **Statistics**: Team performance data
- **Source**: Baseball-Reference.com (with robots.txt compliance)

### Database Schema

#### Events Table
- `year` (INTEGER): Year of event
- `event_type` (TEXT): Type of event (season_summary, world_series)
- `description` (TEXT): Event description
- `value` (TEXT): Associated value
- `category` (TEXT): Event category

#### Players Table
- `player_name` (TEXT): Player name
- `stat_value` (TEXT): Statistical value
- `stat_type` (TEXT): Type of statistic
- `team` (TEXT): Associated team
- `category` (TEXT): Player category

#### Statistics Table
- `year` (INTEGER): Season year
- `team` (TEXT): Team name
- `games_played` (INTEGER): Games in season
- `wins` (INTEGER): Team wins
- `losses` (INTEGER): Team losses
- `league` (TEXT): League (MLB)

## Technical Specifications

### Web Scraping Compliance
- **Robots.txt**: Fully compliant with Baseball-Reference.com rules
- **Crawl Delay**: 3 seconds between requests
- **User Agent**: Standard browser identification
- **Error Handling**: Graceful failures with sample data fallback

### Data Processing
- **Validation**: Year ranges, data types, missing values
- **Cleaning**: Duplicate removal, standardization
- **Performance**: Database indexes for fast queries

### Visualization
- **Charts**: Time series, bar charts, scatter plots
- **Interactivity**: Filters, sliders, dynamic updates
- **Responsive**: Works on desktop and mobile

## Dependencies

### Core Libraries
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `sqlite3` - Database operations (built-in)

### Web Scraping
- `selenium` - Web browser automation
- `webdriver-manager` - Chrome driver management

### Visualization
- `streamlit` - Dashboard framework
- `plotly` - Interactive charts
- `matplotlib` - Static plots
- `seaborn` - Statistical visualization

### Deployment
- `gunicorn` - Web server for production

## Project Highlights

### Web Scraping Excellence
- Ethical scraping with robots.txt compliance
- Robust error handling and fallback data
- Proper delays and browser automation

### Data Pipeline
- Complete ETL process (Extract, Transform, Load)
- Data validation and cleaning
- Efficient database design

### Interactive Analysis
- Command-line interface for ad-hoc queries
- Web dashboard for visual exploration
- Real-time data filtering and updates

### Production Ready
- Comprehensive error handling
- Logging and monitoring
- Deployment configuration

## Future Enhancements

- [ ] Add more data sources (FanGraphs, ESPN)
- [ ] Implement machine learning predictions
- [ ] Add user authentication
- [ ] Real-time data updates
- [ ] Advanced statistical analysis

## License

This project is for educational purposes. Please respect the terms of service of data sources.

## Contact

For questions about this project, please open an issue in the repository.

---

**Note**: This project demonstrates ethical web scraping practices and follows all robots.txt guidelines. Data is used for educational analysis only.