print("Welcome to the World of Warcraft API Data Loader!")
print("1: Complete pipeline run (fetch all data and load into DuckDB)")
print("2: Update auction house items (fetch and load into DuckDB)")
print("3: Create/Update Test Database (creates or updates a database with a smaller subset of data for testing purposes")
print("4: Exit")
choice = input("Please enter your choice (1-4): ")

match choice:
    case "1":
        print("Running complete pipeline...")
    case "2":
        print("Updating auction house items...")
    case "3":
        print("Creating/updating test database...")
    case "4":
        print("Exiting the program.")
        exit(0)