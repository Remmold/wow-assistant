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