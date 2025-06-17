# InFiNetCode Clean Code Hackaton 2025
## WoW API Dashboard
Short summary to be added.

## Project Description
<details>
<summary>Details about the project - click to expand/collapse</summary>

### Purpose
Purpose text to be added.

### Scenario
Scenario text to be added.

</details>

## User Stories, Acceptence Criterias and Use Cases
<details>
<summary>Expand for details</summary>
    
### User stories
<details>
<summary>Click to expand/collapse</summary>

<ins>User story:</ins>  
View current auction data across realms.   
As an active WoW player,   
I want to find updated information from the Auction-house about various item, their prices, and quantities in different realms.   
So that I can buy or sell items at the lowest/highest price.   
________________________________________________________________________________________________________________________________
<ins>User story:</ins>  
View item demands over time   
As an active WoW player,   
I want to be able to see demand trends of items in the Auction-house,   
So that I can find which items are increasing in demand and farm them to sell for profit.   
________________________________________________________________________________________________________________________________
<ins>User story:</ins>  
View item price trend over time   
As an active WoW player,  
I want to be able to track price trends over time for items in the Auction-house,   
So that I can identify which items are increasing in value and sell them for good profit.   
</details>

### Acceptence criteria
<details>
<summary>Click to expand/collapse</summary>
  
```
Scenario: View price and quantity from a list
    Given that the user is on the Auction-house page
    When the user selects an item from the list  
    Then the system should display the price and quantity for the item  
    And the data should only be shown if the item is available  

Scenario: View price and quantity for different realms
    Given that the user is on the page for a specific item
    When the user clicks on "Show realms"
    Then a list with all realms where the item is available for sale should be displayed
    And each realm should show the item's price and quantity
    
Scenario: Show demand trend for a specific item or pet
    Given that the user is on the page for a specific item  
    When the user selects "Demand trends"  
    Then a diagram should show the demand for the item over a certain period
     
Scenario: Show price trend for a specific item
    Given that the user is on the page for a specific item
    When the user selects "Price trends"
    Then a diagram should show the price increase for the item over a certain period
```
</details>

### Use cases
<details>
<summary>Click to expand/collapse</summary>
    
<ins>Use case ID: UC-01</ins>  
Use case name: View current auctions  
Actor(s): WoW player  
Description: The user should be able to see an updated list of current item auctions in different realms, item prices and quantity  

Preconditions:  
- The system has valid API tokens  
- Auction-house API, Connected Realm API and Item API are available

Main flow:  
1. The user opens the dashboard  
2. The system fetches auction data from the Auction-house API  
3. The system fetches item data, including name, rarity etc. from the item API  
4. The dashboard shows a table with available items  
5. The user selects an item from the list  
6. The system fetches which realms the item is available in  
7. The dashboard displays:
    - A list of current realms where the item is being sold
    - Price, lowest/highest, and quantity per realm
    - Timestamp of the latest update

Alternative flow:  
2a. If the Auction-house API does not respond,  
    - The system displays error message: "Could not fetch auctions, try again later."  
5a. If the item is not for sale in any realm,  
    - The system displays: "There are no auctions for the selected item at the moment."  

Postconditions:
- The user has received an overview of which realms the item is for sale in
- The user has seen current price and quantity data per realm
- The system has shown the most recent data available from the API  
________________________________________________________________________________________________
<ins>Use case ID: UC-02</ins>  
Use case name: View demand and price for an item over time  
Actor(s): WoW player  
Description: The user should be able to see how the price for a specific item has changed over time  

Preconditions:
- The system has valid API tokens
- Historical data is fetched or available via another source
- Auction-house API, Connected Realm API and Item API are available  

Main flow:  
1. The user opens the dashboard
2. The system fetches current auction data from the Auction-house API
3. The system fetches items, price, name, rarity etc.
4. The dashboard displays a table with items
5. The user selects an item from the list
6. The system fetches historical price and demand for the item
7. The user clicks on "View trend"
8. The dashboard shows:
    - A line chart of price development over time
    - A line chart of demand over time
    - The user filters trends per realm  

Alternative flow:  
6a. If no time-based data is available
    - The system displays the message: "No trend data available for this item."  

9a. If the user filters by a realm without available data  
    - The system displays: "There is no data to display for the selected realm."  

Postconditions:
- The user has received a visual view of price and demand development
- The user has been able to filter data per realm
- The system has presented relevant time-based visualizations
</details>
</details>
<br>

## How to run
1. **Clone the repository:**
    ```git bash
    git clone https://github.com/Nemanja1208/InFiNetCode-Hackaton2025-Team1
2. **Navigate to the project root:**
    ```git bash
    cd InFiNetCode-Hackaton2025-Team1
3. **Create virtual environment (with `uv venv`):**
    ```git bash
    uv venv .venv
4. **Activate virtual environment:**
    ```git bash
    .venv\scripts\activate (Windows)
    OR
    source source .venv/bin/activate (MacOS/Linux)
5. **Install dependencies from the `requirements.lock`-file:**
    ```git bash
    uv pip install -r requirements.lock.txt
6. **Run the file `pipeline.py` to run the pipeline**
    > ⚠️ Do note that this process will take some time - the first pipeline-run will fetch **a lot** of data, and could take a bit over an hour.
    (a preview mode is to be added, for faster data fetching)
7. **Run the Streamlit Dashboard with the following command (from project root):**
    ```git bash
    streamlit run app.py
<br>

## Profiles.yml:
> ⚠️ DBT is still not implemented, and it is not yet necessary to add this to your **profiles.yml**.
```yml
wow_api:
  outputs:
    dev:
      type: duckdb
      path: wow_api_data.duckdb
      threads: 1

  target: dev
```

<br>

## Documentation (dbt docs)
Documentation is to be added.

<br>

## Tests
Test to be added.

<br>

## Credits

<a href="https://github.com/Remmold" target="_blank">`Andreas (Remmold)`</a>

<a href="https://github.com/vegetablecloud" target="_blank">`Ludvig (Vegetablecloud)`</a>

<a href="https://github.com/wahdanz1" target="_blank">`Daniel (wahdanz1)`</a>

<a href="https://github.com/aeriesAce" target="_blank">`Elvira (aeriesAce)`</a>
