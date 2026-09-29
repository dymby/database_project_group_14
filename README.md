# Database project - group 14

Our project focuses on creating a database for tackling the housing crisis, trying to match up houses and people based on their location, maximum rent and contract (start and end) dates.

**Repository:** https://github.com/dymby/database_project_group_14

```bash
python database/build_db.py --yes   # rebuild mock.db: schema + mock data + real data
python database/run_queries.py      # run all example queries
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
(You can still use browser Jupyter if you prefer — see `docs/SETUP.md` for both.)

That's it — `database/mock.db` is already in the repo, no separate database
setup or server install required. The real-world data is already loaded into it.

## Project structure

```
data/raw/           # the real-world datasets 
database/
  mock.db           # the actual database 
  schema.sql        # table definitions (v2: updated in week 5 after testing with real data)
  seed_data.sql     # mock data from weeks 3-4
  load_real_data.py # cleans + inserts the two real-world datasets in normalized form
  build_db.py       # rebuilds mock.db: schema + seed data + real data
  queries.sql       # example queries (Q1-Q4 week 3, Q5-Q9 week 5)
  run_queries.py    # runs every query in queries.sql and prints the row counts
docs/
  societal_problem.pdf  # week 1 deliverable
  erd_report.pdf        # week 2 deliverable (ERD + normal forms), unchanged
  week2_addendum.md           # corrections to week 2 found while testing real data
  erd_v2.md                   # ERD of the current schema (renders on GitHub)
  data_sources.md         # source, date, license of each raw dataset
  data_cleaning.md        # missing data, date formats, duplicates, naming conventions
  schema_changes.md       # every schema/constraint change and what triggered it
  normalization_report.md # 3NF check on the real data 
  week5_review.md         # query results, limitations, future work
notebooks/          # exploration / analysis — one notebook per person or task
src/
  db.py          
```


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

See `CONTRIBUTING.md` for the
branching/PR workflow.
