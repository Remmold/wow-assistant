from wow_api_dlt.pipeline import run_pipeline
import subprocess
import sys 

print("Welcome to the World of Warcraft API Data Loader!")
print("1: Complete pipeline run (fetch all data and load into DuckDB)")
print("2: Update auction house items (fetch and load into DuckDB)")
print("3: Create/Update Test Database (creates or updates a database with a smaller subset of data for testing purposes)")
print("4: View database with DuckDB UI")
print("5: View test database with DuckDB UI")
print("6: Exit")

choice = input("Please enter your choice (1-6): ")

match choice:
    case "1":
        print("Running complete pipeline...")
        run_pipeline(test_mode=False) 
    case "2":
        print("Updating auction house items...")
        run_pipeline(test_mode=False, sources=["auctions"])

    case "3":
        print("1: Create test database")
        print("2: Update test database")
        test_choice = input("Please enter your choice (1-2): ")
        match test_choice:
            case "1":
                print("Creating test database...")
                run_pipeline(test_mode=True)
            case "2":
                print("Updating test database...")
                run_pipeline(test_mode=True, sources=["auctions"])
            case _:
                print("Invalid choice. Exiting.")
                sys.exit(1) 
    case "4":
        print("Attempting to open DuckDB UI for main database...")
        try:
            subprocess.Popen(["duckdb", "-ui", "wow_api_dbt/wow_api_data.duckdb"])
            print("If the browser didn't open, please check your DuckDB version (must be 1.2.1+) and default browser settings.")
        except FileNotFoundError:
            print("Error: 'duckdb' command not found. Please ensure DuckDB CLI is installed and in your system's PATH.")
        except subprocess.CalledProcessError as e:
            print(f"Error launching DuckDB UI: {e}. Check DuckDB installation and permissions.")
    case "5":
        print("Attempting to open DuckDB UI for test database...")
        try:
            
            subprocess.Popen(["duckdb", "-ui", "wow_api_dbt/test_wow_api_data.duckdb"])
            print("If the browser didn't open, please check your DuckDB version (must be 1.2.1+) and default browser settings.")
        except FileNotFoundError:
            print("Error: 'duckdb' command not found. Please ensure DuckDB CLI is installed and in your system's PATH.")
        except subprocess.CalledProcessError as e:
            print(f"Error launching DuckDB UI: {e}. Check DuckDB installation and permissions.")
    case "6":
        print("Exiting the program. Farewell, adventurer!")
        sys.exit(0)
    case _: # Handles any other invalid input for the main menu
        print("Invalid choice. Please enter a number between 1 and 6.")
        sys.exit(1)