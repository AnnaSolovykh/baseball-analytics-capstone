#!/usr/bin/env python3
"""
Database Import Program
Imports CSV files into SQLite database with proper data types and error handling
"""

import sqlite3
import pandas as pd
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseImporter:
    def __init__(self, db_path='data/processed/baseball.db'):
        """Initialize database importer"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Create processed data directory
        os.makedirs('data/processed', exist_ok=True)
    
    def connect_to_database(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def create_tables(self):
        """Create tables with proper schema"""
        try:
            # Events table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT,
                    value TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Players table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    stat_value TEXT,
                    stat_type TEXT,
                    team TEXT,
                    category TEXT,
                    rank TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Statistics table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER,
                    team TEXT,
                    category TEXT,
                    games_played INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    league TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("Tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def validate_csv_file(self, filepath):
        """Validate if CSV file exists and is readable"""
        if not os.path.exists(filepath):
            logger.warning(f"File {filepath} does not exist")
            return False
        
        try:
            df = pd.read_csv(filepath)
            if df.empty:
                logger.warning(f"File {filepath} is empty")
                return False
            logger.info(f"File {filepath} validated - {len(df)} rows")
            return True
        except Exception as e:
            logger.error(f"Error validating {filepath}: {e}")
            return False
    
    def clean_events_data(self, df):
        """Clean and prepare events data"""
        try:
            logger.info("Cleaning events data...")
            
            # Remove duplicates
            original_count = len(df)
            df = df.drop_duplicates()
            if len(df) < original_count:
                logger.info(f"Removed {original_count - len(df)} duplicate rows")
            
            # Handle missing values
            df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2023).astype(int)
            df['event_type'] = df['event_type'].fillna('unknown')
            df['description'] = df['description'].fillna('')
            df['value'] = df['value'].fillna('')
            df['category'] = df['category'].fillna('general')
            
            # Validate year range
            df = df[(df['year'] >= 1900) & (df['year'] <= 2025)]
            
            logger.info(f"Events data cleaned - {len(df)} rows ready")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning events data: {e}")
            return df
    
    def clean_players_data(self, df):
        """Clean and prepare players data"""
        try:
            logger.info("Cleaning players data...")
            
            # Remove duplicates
            original_count = len(df)
            df = df.drop_duplicates()
            if len(df) < original_count:
                logger.info(f"Removed {original_count - len(df)} duplicate rows")
            
            # Handle missing values
            df['player_name'] = df['player_name'].fillna('Unknown Player')
            df['stat_value'] = df['stat_value'].fillna('0')
            df['stat_type'] = df['stat_type'].fillna('unknown')
            df['team'] = df['team'].fillna('Unknown Team')
            df['category'] = df['category'].fillna('general')
            df['rank'] = df['rank'].fillna('0')
            
            # Remove empty player names
            df = df[df['player_name'].str.strip() != '']
            
            logger.info(f"Players data cleaned - {len(df)} rows ready")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning players data: {e}")
            return df
    
    def clean_statistics_data(self, df):
        """Clean and prepare statistics data"""
        try:
            logger.info("Cleaning statistics data...")
            
            # Check if file exists and has data
            if df.empty:
                logger.warning("Statistics data is empty, creating sample data")
                # Create sample statistics data
                years = range(2020, 2025)
                sample_data = []
                for year in years:
                    sample_data.append({
                        'year': year,
                        'team': 'MLB Average',
                        'category': 'league_stats',
                        'games_played': 162,
                        'wins': 81,
                        'losses': 81,
                        'league': 'MLB'
                    })
                df = pd.DataFrame(sample_data)
            
            # Remove duplicates
            original_count = len(df)
            df = df.drop_duplicates()
            if len(df) < original_count:
                logger.info(f"Removed {original_count - len(df)} duplicate rows")
            
            # Handle missing values and convert numeric columns
            df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2023).astype(int)
            df['team'] = df['team'].fillna('Unknown Team')
            df['category'] = df['category'].fillna('general')
            df['league'] = df['league'].fillna('MLB')
            
            # Numeric columns
            numeric_columns = ['games_played', 'wins', 'losses']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                else:
                    df[col] = 0
            
            # Validate data ranges
            df = df[(df['year'] >= 1900) & (df['year'] <= 2025)]
            df = df[(df['games_played'] >= 0) & (df['games_played'] <= 200)]
            df = df[(df['wins'] >= 0) & (df['losses'] >= 0)]
            
            logger.info(f"Statistics data cleaned - {len(df)} rows ready")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning statistics data: {e}")
            return df
    
    def import_csv_to_table(self, csv_path, table_name):
        """Import CSV data to specific table"""
        try:
            if not self.validate_csv_file(csv_path):
                logger.warning(f"Skipping {csv_path} - validation failed")
                return False
            
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Read {len(df)} rows from {csv_path}")
            
            # Clean data based on table type
            if table_name == 'events':
                df = self.clean_events_data(df)
            elif table_name == 'players':
                df = self.clean_players_data(df)
            elif table_name == 'statistics':
                df = self.clean_statistics_data(df)
            
            if len(df) == 0:
                logger.warning(f"No data to import for {table_name}")
                return False
            
            # Import data
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            
            # Verify import
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            
            logger.info(f"Successfully imported {count} rows to {table_name} table")
            return True
            
        except Exception as e:
            logger.error(f"Error importing {csv_path} to {table_name}: {e}")
            return False
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_events_year ON events(year)",
                "CREATE INDEX IF NOT EXISTS idx_events_category ON events(category)",
                "CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)",
                "CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name)",
                "CREATE INDEX IF NOT EXISTS idx_players_team ON players(team)",
                "CREATE INDEX IF NOT EXISTS idx_players_category ON players(category)",
                "CREATE INDEX IF NOT EXISTS idx_statistics_year ON statistics(year)",
                "CREATE INDEX IF NOT EXISTS idx_statistics_team ON statistics(team)",
                "CREATE INDEX IF NOT EXISTS idx_statistics_category ON statistics(category)"
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            self.conn.commit()
            logger.info("Indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def display_import_summary(self):
        """Display summary of imported data"""
        try:
            tables = ['events', 'players', 'statistics']
            print("\n" + "="*50)
            print("DATABASE IMPORT SUMMARY")
            print("="*50)
            
            total_records = 0
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"{table.capitalize()}: {count:,} records")
                total_records += count
            
            print(f"Total records: {total_records:,}")
            print(f"Database location: {self.db_path}")
            print("="*50)
            
            # Show sample data from each table
            for table in tables:
                self.cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = self.cursor.fetchall()
                if rows:
                    print(f"\nSample {table} data:")
                    # Get column names
                    self.cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in self.cursor.fetchall()]
                    
                    for row in rows:
                        sample_data = dict(zip(columns[:4], row[:4]))  # First 4 columns
                        print(f"  {sample_data}")
            
            print("\n")
            return True
            
        except Exception as e:
            logger.error(f"Error displaying summary: {e}")
            return False
    
    def run_import(self):
        """Main method to run all import operations"""
        try:
            print("Starting Baseball Database Import...")
            
            if not self.connect_to_database():
                return False
            
            if not self.create_tables():
                return False
            
            # CSV files to import
            csv_files = [
                ('data/raw/events.csv', 'events'),
                ('data/raw/players.csv', 'players'),
                ('data/raw/statistics.csv', 'statistics')
            ]
            
            success_count = 0
            for csv_path, table_name in csv_files:
                logger.info(f"Importing {csv_path} to {table_name}...")
                if self.import_csv_to_table(csv_path, table_name):
                    success_count += 1
                else:
                    logger.warning(f"Failed to import {csv_path}")
            
            if success_count > 0:
                self.create_indexes()
                self.display_import_summary()
                print(f"Database import completed! {success_count}/{len(csv_files)} files imported successfully.")
                return True
            else:
                print("No files were imported successfully.")
                return False
                
        except Exception as e:
            logger.error(f"Error during import process: {e}")
            return False
        finally:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")

def main():
    """Main function"""
    importer = DatabaseImporter()
    success = importer.run_import()
    
    if success:
        print("\nNext step: Run the database query program!")
        print("   python3 database_query.py --interactive")
    else:
        print("\nImport failed. Check the logs above for details.")

if __name__ == "__main__":
    main()