# Database project - group 14

Our project focuses on creating a database for tackling the housing crisis, trying to match up houses and people based on their location, maximum rent and contract (start and end) dates.

## Stack

- Python 3.10+
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
setup or server install required.

## Project structure

```
database/
  mock.db          # the actual database — committed directly, don't gitignore it
  schema.sql        # human-readable table definitions (reference / rebuild fallback)
  seed_data.sql      # human-readable mock data (reference / rebuild fallback)
  build_db.py       # regenerates mock.db from the .sql files if needed
notebooks/          # exploration / analysis — one notebook per person or task
src/
  db.py             # shared DB connection helper — import this, don't write your own
tests/
docs/
  SETUP.md          # detailed setup + troubleshooting
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

See `docs/SETUP.md` for troubleshooting and `CONTRIBUTING.md` for the
branching/PR workflow.