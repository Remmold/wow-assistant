from wow_api_dlt.pipeline import run_pipeline
import subprocess
import sys 

while True:
    # Display the menu options
    print("\nMenu Options:")
    print("1: Auctions/items related options")
    print("2: Character related options")
    choice = input("Select an option 1-2 ").strip().lower()
    match choice:
        case "1":
            print("Welcome to the World of Warcraft API Data Loader!")
            print("1: Complete pipeline run (fetch all data and load into DuckDB)")
            print("2: Update auction house items and commodities (fetch and load into DuckDB)")
            print("3: Update commodities data (fetch and load into DuckDB)")
            print("4: Update Item data (fetch and load into DuckDB)")
            print("5: Update item_media data (fetch and load into DuckDB)")
            print("6: Update item_details for items (fetch and load into DuckDB)")
            print("7: Update realm data (fetch and load into DuckDB)")
            print("8: Create/Update Test Database (creates or updates a database with a smaller subset of data for testing purposes)")
            print("9: View database with DuckDB UI")
            print("0: Exit")

            choice = input("Please enter your choice (0-9): ")

            match choice:
                case "1":
                    print("Running complete pipeline...")
                    run_pipeline(test_mode=False) 
                case "2":
                    print("Updating auction house items...")
                    run_pipeline(test_mode=False, sources=["auctions","commodities"], scheema="raw_auctions")
                case "3":
                    print("Updating commodities data...")
                    run_pipeline(test_mode=False, sources=["commodities"], scheema="raw_auctions")
                case "4":
                    print("Updating Item data...")
                    run_pipeline(test_mode=False, sources=["items"], scheema="raw_items")
                case "5":
                    print("Updating media data for items...")
                    run_pipeline(test_mode=False, sources=["item_media"], scheema="raw_items")
                case "6":
                    print("Updating Item_details data...")
                    run_pipeline(test_mode=False, sources=["item_details"], scheema="raw_items")
                case "7":
                    print("Updating realm data...")
                    run_pipeline(test_mode=False, sources=["realm_data"], scheema="raw_misc")
                case "8":
                    print("1: Create test database")
                    print("2: Update test database")
                    test_choice = input("Please enter your choice (1-2): ")
                    match test_choice:
                        case "1":
                            print("Creating test database...")
                            run_pipeline(test_mode=True)
                        case "2":
                            print("Updating test database...")
                            run_pipeline(test_mode=True, sources=["auctions", "commodities"], scheema="raw_auctions")
                        case _:
                            print("Invalid choice. Exiting.")
                            sys.exit(1) 
                case "9":
                    print("Attempting to open DuckDB UI for main database...")
                    try:
                        subprocess.Popen(["duckdb", "-ui", "wow_api_dbt/wow_api_data.duckdb"])
                        print("If the browser didn't open, please check your DuckDB version (must be 1.2.1+) and default browser settings.")
                    except FileNotFoundError:
                        print("Error: 'duckdb' command not found. Please ensure DuckDB CLI is installed and in your system's PATH.")
                    except subprocess.CalledProcessError as e:
                        print(f"Error launching DuckDB UI: {e}. Check DuckDB installation and permissions.")
                case "0":
                    print("Exiting the program. Farewell, adventurer!")
                    sys.exit(0)
                case _: # Handles any other invalid input for the main menu
                    print("Invalid choice. Please enter a number between 1 and 8.")
                    sys.exit(1)
        case "2":
            print("Character related options are not implemented yet.")