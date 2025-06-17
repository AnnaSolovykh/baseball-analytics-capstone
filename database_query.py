#!/usr/bin/env python3
"""
Database Query Program
Command-line interface for querying the baseball database with joins and filters
"""

import sqlite3
import pandas as pd
import argparse
import sys

class DatabaseQueryManager:
    def __init__(self, db_path='data/processed/baseball.db'):
        """Initialize database query manager"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect_to_database(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in self.cursor.description]
            results = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in results]
            
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def display_results(self, results, title="Query Results"):
        """Display query results in a formatted table"""
        if not results:
            print("No results found.")
            return
        
        print(f"\n=== {title} ===")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(results)
        
        # Simple table formatting
        print(df.to_string(index=False))
        print(f"\nTotal records: {len(results)}")
    
    def query_events_by_year(self, year):
        """Query events for a specific year"""
        query = """
            SELECT year, event_type, description, value, category 
            FROM events 
            WHERE year = ? 
            ORDER BY event_type
        """
        
        results = self.execute_query(query, (year,))
        self.display_results(results, f"Events for Year {year}")
        return results
    
    def query_players_by_team(self, team):
        """Query players by team"""
        query = """
            SELECT player_name, stat_value, stat_type, team, category 
            FROM players 
            WHERE team LIKE ? 
            ORDER BY player_name
        """
        
        results = self.execute_query(query, (f"%{team}%",))
        self.display_results(results, f"Players for Team: {team}")
        return results
    
    def query_events_with_players_same_category(self):
        """Join events with players using CROSS JOIN to show relationships"""
        query = """
            SELECT 
                e.year,
                e.event_type,
                e.description as event_description,
                p.player_name,
                p.stat_type,
                p.team
            FROM events e
            CROSS JOIN players p
            WHERE e.year >= 2020
            ORDER BY e.year, p.player_name
            LIMIT 20
        """
        
        results = self.execute_query(query)
        self.display_results(results, "Events with Players (Cross Reference)")
        return results
    
    def query_yearly_summary(self):
        """Get yearly summary with event counts"""
        query = """
            SELECT 
                year,
                COUNT(*) as event_count,
                GROUP_CONCAT(DISTINCT event_type) as event_types,
                GROUP_CONCAT(DISTINCT category) as categories
            FROM events
            GROUP BY year
            ORDER BY year DESC
        """
        
        results = self.execute_query(query)
        self.display_results(results, "Yearly Summary")
        return results
    
    def query_player_stats_summary(self):
        """Get player statistics summary"""
        query = """
            SELECT 
                category,
                COUNT(*) as player_count,
                GROUP_CONCAT(DISTINCT team) as teams,
                GROUP_CONCAT(DISTINCT stat_type) as stat_types
            FROM players
            GROUP BY category
            ORDER BY player_count DESC
        """
        
        results = self.execute_query(query)
        self.display_results(results, "Player Statistics Summary")
        return results
    
    def query_cross_reference(self):
        """Cross-reference events and players by year and category"""
        query = """
            SELECT 
                e.year,
                e.category,
                COUNT(DISTINCT e.id) as event_count,
                COUNT(DISTINCT p.id) as player_count,
                GROUP_CONCAT(DISTINCT e.event_type) as event_types
            FROM events e
            LEFT JOIN players p ON e.category = p.category
            GROUP BY e.year, e.category
            ORDER BY e.year DESC, event_count DESC
        """
        
        results = self.execute_query(query)
        self.display_results(results, "Cross-Reference: Events and Players")
        return results
    
    def custom_query(self, query_text):
        """Execute custom SQL query"""
        try:
            results = self.execute_query(query_text)
            self.display_results(results, "Custom Query Results")
            return results
        except Exception as e:
            print(f"Error executing custom query: {e}")
            return []
    
    def show_available_tables(self):
        """Show available tables and their structure"""
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = self.execute_query(tables_query)
        
        print("\n=== Available Tables ===")
        for table in tables:
            table_name = table['name']
            print(f"\nTable: {table_name}")
            
            # Get table structure
            pragma_query = f"PRAGMA table_info({table_name})"
            columns = self.execute_query(pragma_query)
            
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = self.execute_query(count_query)
            if count_result:
                print(f"  Records: {count_result[0]['count']}")
    
    def interactive_mode(self):
        """Interactive command-line interface"""
        print("\n=== Baseball Database Query Interface ===")
        print("Available commands:")
        print("1. events <year> - Get events for specific year")
        print("2. players <team> - Get players for specific team")
        print("3. join - Join events with players by category")
        print("4. summary - Show yearly summary")
        print("5. player-stats - Show player statistics summary")
        print("6. cross-ref - Cross-reference events and players")
        print("7. custom - Execute custom SQL query")
        print("8. tables - Show available tables")
        print("9. quit - Exit program")
        print("=" * 45)
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command.startswith('events '):
                    year = int(command.split()[1])
                    self.query_events_by_year(year)
                elif command.startswith('players '):
                    team = command.split()[1]
                    self.query_players_by_team(team)
                elif command == 'join':
                    self.query_events_with_players_same_category()
                elif command == 'summary':
                    self.query_yearly_summary()
                elif command == 'player-stats':
                    self.query_player_stats_summary()
                elif command == 'cross-ref':
                    self.query_cross_reference()
                elif command == 'custom':
                    query_text = input("Enter SQL query: ")
                    self.custom_query(query_text)
                elif command == 'tables':
                    self.show_available_tables()
                else:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except (ValueError, IndexError):
                print("Invalid command format. Please try again.")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run_query_program(self, args):
        """Main method to run query program with command line arguments"""
        try:
            if not self.connect_to_database():
                return False
            
            if args.interactive:
                self.interactive_mode()
            elif args.year:
                self.query_events_by_year(args.year)
            elif args.team:
                self.query_players_by_team(args.team)
            elif args.join:
                self.query_events_with_players_same_category()
            elif args.summary:
                self.query_yearly_summary()
            elif args.tables:
                self.show_available_tables()
            else:
                print("No specific query specified. Starting interactive mode...")
                self.interactive_mode()
                
        except Exception as e:
            print(f"Error in query program: {e}")
            return False
        finally:
            if self.conn:
                self.conn.close()
                print("\nDatabase connection closed.")
        
        return True

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Baseball Database Query Program')
    
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='Start interactive mode')
    parser.add_argument('-y', '--year', type=int, 
                       help='Query events for specific year')
    parser.add_argument('-t', '--team', type=str, 
                       help='Query players for specific team')
    parser.add_argument('-j', '--join', action='store_true', 
                       help='Join events with players by category')
    parser.add_argument('-s', '--summary', action='store_true', 
                       help='Show yearly summary')
    parser.add_argument('--tables', action='store_true', 
                       help='Show available tables')
    
    args = parser.parse_args()
    
    query_manager = DatabaseQueryManager()
    query_manager.run_query_program(args)

if __name__ == "__main__":
    main()