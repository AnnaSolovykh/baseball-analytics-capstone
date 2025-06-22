from pathlib import Path
import sqlite3

db_path = Path("data/baseball.db")

# Predefined successful SQL queries
predefined_queries = [
    # Filtered query for a specific player
    (
        "MVPs for Mike Trout",
        "SELECT year, player_name, team, position FROM mvp_awards WHERE player_name LIKE '%Mike Trout%';"
    ),
    # MVPs from American League sorted by year
    (
        "MVPs in American League (A.L.)",
        "SELECT year, player_name, team FROM mvp_awards WHERE league LIKE 'A.L.%' ORDER BY year DESC;"
    ),
    # Aggregation: number of awards by team
    (
        "Total MVP awards by team",
        "SELECT team, COUNT(*) AS total_awards FROM mvp_awards GROUP BY team ORDER BY total_awards DESC;"
    ),
    # JOIN by year with me_awards_list
    (
        "Join MVP awards with general awards (by year)",
        "SELECT m.year, m.player_name, a.award FROM mvp_awards m "
        "JOIN me_awards_list a ON CAST(SUBSTR(a.years, 1, 4) AS INTEGER) <= m.year "
        "AND m.year <= CAST(SUBSTR(a.years, -4) AS INTEGER) LIMIT 10;"
    ),
    # JOIN by name with cleaned player names and baseball brothers
    (
        "Join MVPs with brother sets (by cleaned name)",
        "SELECT m.year, TRIM(SUBSTR(m.player_name, 1, INSTR(m.player_name, '(') - 1)) AS cleaned_name, "
        "b.set_number, b.brothers_names FROM mvp_awards m "
        "JOIN baseball_brothers_sets b ON b.brothers_names LIKE '%' || "
        "TRIM(SUBSTR(m.player_name, 1, INSTR(m.player_name, '(') - 1)) || '%' LIMIT 10;"
    ),
]

# Run and display predefined queries
def run_predefined_queries(conn):
    print("Running predefined example queries:\n")
    for title, query in predefined_queries:
        print(f"{title}")
        try:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            print(" | ".join(col_names))
            print("-" * 80)
            for row in rows:
                print(" | ".join(str(x) for x in row))
            print()
        except Exception as e:
            print(f"Failed to run query: {e}\n")


# Interactive SQL CLI
def run_custom_query_interface(conn):
    print("Type your own SQL query below (type 'exit' to quit).")
    print("Example JOIN:\nSELECT year, player_name, team FROM mvp_awards WHERE league = 'A.L. (20)';\n")
    while True:
        query = input("SQL> ")
        if query.lower() in ["exit", "quit"]:
            break
        try:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            print(" | ".join(col_names))
            print("-" * 80)
            for row in rows:
                print(" | ".join(str(x) for x in row))
        except Exception as e:
            print(f"Query failed: {e}")


# Main execution
if __name__ == "__main__":
    if not db_path.exists():
        print(f"Database not found at {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        print(f"Connected to database at {db_path}\n")
        try:
            run_predefined_queries(conn)
            run_custom_query_interface(conn)
        except KeyboardInterrupt:
            print("\nExited by user (Ctrl+C)")
        finally:
            conn.close()
