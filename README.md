# Database project - group 14

Our project focuses on creating a database for tackling the housing crisis, trying to match up houses and people based on their location, maximum rent and contract (start and end) dates.

**Repository:** https://github.com/dymby/database_project_group_14

```bash
python database/build_db.py --yes   # rebuild mock.db: schema + mock data + real data
python database/check_db.py         # check integrity, foreign keys and row counts against the CSV files
python database/run_queries.py      # run all example queries
python -m unittest discover tests   # run the tests
```

## Stack

- Python 3.10+ (pandas for the data cleaning)
- SQLite (database committed directly to the repo as `database/mock.db`)
- Jupyter notebooks for analysis/querying

## Quickstart

```bash
# 1. Clone the repo
git clone <repo-url>
cd <repo-folder>

# 2. Create a virtual environment (recommended, not mandatory)
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Enable nbstripout (strips notebook output before each commit)
nbstripout --install
```

Then open the project folder in **VS Code** and open any `.ipynb` file in
`notebooks/` — with the Jupyter extension installed, it renders and runs
notebook cells directly, no separate `jupyter notebook` browser step needed.

That's it — `database/mock.db` is already in the repo, no separate database
setup or server install required. The real-world data is already loaded into it.

## Project structure

```
data/raw/           # the real-world datasets 
database/
  mock.db           # the actual database 
  schema.sql        # table definitions (v2: updated in week 5 after testing with real data)
  seed_data.sql     # mock data from weeks 3-4
  load_data.py      # cleans + inserts the three real-world datasets in normalized form
  export_real_data.py # writes the loaded real data to real_data.sql
  real_data.sql     # This file is the SQL *result* of that work, so the inserted data can be read, reviewed and replayed without pandas.
  build_db.py       # rebuilds mock.db: schema + seed data + real data
  check_db.py       # read-only check: integrity, foreign keys, row counts against the CSV files
  queries.sql       # example queries (Q1-Q4 week 3, Q5-Q9 week 5)
  run_queries.py    # runs every query in queries.sql and prints the row counts
docs/
  societal_problem.pdf  # week 1 deliverable
  Erd_report.pdf        # week 2 deliverable (ERD + normal forms), unchanged
  ERD Adapted to Real Data.md # ERD of the current schema (renders on GitHub)
  data_sources.md         # source, date, license of each raw dataset
  data_cleaning.md        # missing data, date formats, duplicates, naming conventions
  schema_changes.md       # every schema/constraint change and what triggered it
  normalization_report.md # 3NF check on the real data 
tests/
  test_database.py  # build, cleaning, constraints and delete behaviour
notebooks/          # exploration / analysis — one notebook per person or task (not added yet)
src/
  db.py          
```

## Testing

```bash
python -m unittest discover tests   # 28 tests, a few seconds, needs only pandas
python database/check_db.py         # checks the committed mock.db
```

The tests build a fresh database in a temporary folder, so they never change `mock.db`.
They are in `tests/test_database.py`, in four groups:

| Group | Tests | What it checks |
|---|---|---|
| `BuildTest` | 8 | the build succeeds with the expected row count in every table; loading twice is refused; a failed build keeps the old database; `real_data.sql` gives the same database as `build_db.py`; all 9 queries run |
| `CleaningTest` | 3 | lot size `5.440 m²` is read as 5440; addresses are split into street, number, letter and addition; BAG postcodes get the `NNNN AA` format |
| `ConstraintTest` | 10 | wrong data is rejected: malformed postcode, house size outside 5-1000, age above 120, contract ending before it starts, duplicate city, host or address, unknown room type |
| `DeleteTest` | 7 | the delete rules listed in `docs/schema_changes.md`: what is removed, what is kept and what is refused |

`check_db.py` is read-only and exits with code 1 if something is wrong. It checks the file integrity,
looks for rows that point to a deleted row (foreign keys), prints the row count per table, and compares
the database with the CSV files in `data/raw/`: number of BAG addresses, houses and postcodes, Airbnb
hosts, listings (also those without a price or host) and neighbourhoods, Kaggle addresses, houses and
total lot size.


## A few things worth knowing before you start

- **`mock.db` is a binary file.** Git can't diff or merge it. If you need to
  change the schema or seed data, say so in the team channel first so two
  people don't edit it at the same time — see CONTRIBUTING.md.
- **Don't write your own database connection code.** Import from `src/db.py`
  so everyone connects the same way and paths don't break depending on
  where you launched Jupyter from.
- **Notebooks are for analysis, not shared logic.** Reusable functions go in
  `src/`, notebooks import them. Keeps things testable and stops four
  people's notebooks from quietly diverging.

- **Foreign keys are only enforced on connections that switch them on** (`src/db.py`
  does). If you delete rows through another tool, run `python database/check_db.py`
  afterwards.

See `CONTRIBUTING.md` for the
branching/PR workflow.

## Still missing

- `docs/week5_review.md` (query results, limitations, future work) is referred to by
  `docs/data_sources.md` but was never uploaded.
- Source URL, license and publication date of the Kaggle dataset in `docs/data_sources.md`.
