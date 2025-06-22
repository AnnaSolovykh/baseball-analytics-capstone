# Baseball Analytics Capstone Project

## Project Overview

This is a comprehensive data analysis pipeline that scrapes baseball history data, stores it in a database, and presents insights through an interactive dashboard. The project demonstrates web scraping, data processing, database management, and data visualization skills.

## Project Structure

```
baseball-analytics-capstone/
├── scrapers/                  # Web scraping programs
│   ├── award_winners_scraper.py
│   ├── baseball_brothers.py
│   └── yearly_stats.py
├── dashboard.py               # Streamlit dashboard
├── database_import.py         # Imports CSVs to SQLite
├── database_query.py          # Command-line SQL interface
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── data/
│   ├── raw/
│   │   ├── mvp_awards.csv
│   │   ├── baseball_brothers_sets.csv
│   │   └── me_awards_list.csv
│   └── baseball.db            # SQLite database
└── baseball_env/              # Virtual environment
```

## Features

### 1. Web Scraping (`scrapers/`)

* Sources data from baseball award and stats pages
* Includes scrapers for:

  * MVP Award history
  * Notable family members (e.g., brothers)
  * Yearly team statistics
* Saves cleaned CSVs to `data/raw/`

### 2. Database Import (`database_import.py`)

* Loads and normalizes all raw CSVs into SQLite
* Handles missing values and type conversion
* Automatically creates database tables and replaces data
* Stores data in `data/baseball.db`

### 3. Query CLI (`database_query.py`)

```bash
python3 database_query.py
```

**Features:**

* Runs a set of predefined SQL queries with readable output
* Provides an interactive SQL prompt for custom queries
* Use `exit` or `quit` to leave the interface

### 4. Interactive Dashboard (`dashboard.py`)

* Built with Streamlit and Plotly
* Includes filters by year, league, award type, family count
* Sections:

  * MVP Analysis
  * Family Connections
  * Awards Overview
* Responsive and ready for deployment

## Installation

### Requirements

* Python 3.9+
* Google Chrome (for Selenium)

### Setup

```bash
git clone <repository-url>
cd baseball-analytics-capstone

python3 -m venv baseball_env
source baseball_env/bin/activate      # macOS/Linux
# or
baseball_env\Scripts\activate         # Windows

pip install -r requirements.txt
```

## Usage

### Step 1: Scrape data

```bash
python3 scrapers/award_winners_scraper.py
python3 scrapers/baseball_brothers.py
python3 scrapers/yearly_stats.py
```

### Step 2: Import data into SQLite

```bash
python3 database_import.py
```

### Step 3: Explore via CLI

```bash
python3 database_query.py
```

### Step 4: Launch dashboard

```bash
streamlit run dashboard.py
```

## Data Sources

* Award history and stats scraped from Baseball Almanac and other public sources
* Family relationships collected from curated online databases
* Statistics for MVP and team achievements across leagues

## Database Schema

### Table: `mvp_awards`

| Column            | Type | Description                |
| ----------------- | ---- | -------------------------- |
| `year`            | TEXT | Year of the award          |
| `player_name`     | TEXT | Name of the MVP player     |
| `league`          | TEXT | League (e.g., A.L., N.L.)  |
| `team`            | TEXT | Team name                  |
| `position`        | TEXT | Player's position          |
| `source_url`      | TEXT | URL of original data       |
| `extraction_date` | TEXT | Date when data was scraped |

### Table: `baseball_brothers_sets`

| Column            | Type    | Description                   |
| ----------------- | ------- | ----------------------------- |
| `set_number`      | INTEGER | Unique ID of brother set      |
| `brothers_count`  | INTEGER | Number of brothers in the set |
| `brothers_names`  | TEXT    | Comma-separated list of names |
| `source_url`      | TEXT    | URL of original data          |
| `extraction_date` | TEXT    | Date when data was scraped    |

### Table: `me_awards_list`

| Column            | Type | Description                          |
| ----------------- | ---- | ------------------------------------ |
| `award`           | TEXT | Name of the award                    |
| `years`           | TEXT | Year range of award (e.g. 2010–2014) |
| `link`            | TEXT | Link to details                      |
| `source_url`      | TEXT | URL of original data                 |
| `extraction_date` | TEXT | Date when data was scraped           |

## Dependencies

* pandas
* numpy
* selenium
* webdriver-manager
* plotly
* streamlit
* sqlite3 (built-in)

## License

This project is for educational purposes only. It respects all data source terms and usage policies. No commercial redistribution.

Created as part of the *Code The Dream* Python class.
