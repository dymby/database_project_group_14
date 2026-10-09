# Contributing

This describes how the group actually worked on the repo, not an ideal
process. It is based on the commit history.

## Branches

- Almost all work was committed straight to `main`. We did not use pull
  requests or code review on GitHub.
- A feature branch was used once, for the larger schema v2 change
  (`feature/schema-v2`). It was fast-forwarded into `main` without a
  merge commit or a pull request.

## How changes got into the repo

Two ways, depending on the person:

1. **Local git**: `git pull`, make the change, commit, `git push origin main`.
2. **GitHub web interface**: "Add files via upload" to add or replace a
   file, or editing a file (e.g. `README.md`) directly in the browser.

Before pushing or uploading, pull or check the latest `main` first, since
everyone works on the same branch.

## Commit messages

There was no fixed format. Local commits have a short description of the
change; web edits keep GitHub's default message ("Add files via upload",
"Update README.md").

## Splitting the work

- Each weekly assignment was divided between the members, and each member
  committed their own part.
- To avoid editing the same file at the same time, queries were also put in
  personal files (`database/MarcPyioQueries.sql`, `database/RoshikQueries.sql`)
  next to the shared `database/queries.sql`.
- Documentation for each deliverable goes in `docs/` (Markdown, or PDF for
  the week 1 and week 2 reports).
- Raw datasets go in `data/raw/`, with their source described in
  `docs/data_sources.md` and the cleaning steps in `docs/data_cleaning.md`.

## The database file

`database/mock.db` is committed as a binary file, so git cannot merge it.
Schema or data changes were announced in the group chat first, so only one
person changed the database at a time.

When changing the schema, seed data or data loading:

1. Edit `database/schema.sql`, `database/seed_data.sql` and/or
   `database/load_data.py`.
2. Rebuild the database: `python database/build_db.py --yes`
3. Check it: `python database/check_db.py` and
   `python -m unittest discover tests`
4. Commit the source files and the rebuilt `mock.db` together, and record
   the change in `docs/schema_changes.md`.
