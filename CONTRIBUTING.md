# Contributing
 
## Branches
 
- `main` is always working. Never commit directly to `main`.
- One branch per task: `feature/short-description`
  (e.g. `feature/eda-notebook`, `feature/add-orders-table`)
- Delete your branch after it's merged.
## Workflow
 
1. `git pull origin main` before starting anything new.
2. `git checkout -b feature/your-thing`
3. Commit in small logical chunks with clear messages
   (`fix: correct region filter in query` not `stuff`).
4. Push your branch, open a Pull Request into `main`.
5. At least one other teammate looks at it before merging — even just a
   skim. Catching a broken notebook before it hits `main` beats catching
   it during a live demo.
6. Merge, delete the branch.
## The database file — read this before touching it
 
`database/mock.db` is committed directly to the repo as a binary file.
**Git cannot merge .db files.** If two people change the schema or data
on separate branches at the same time, whoever merges second will get a
conflict that has to be resolved by hand — usually by picking one version
and manually redoing the other person's changes.
 
Rule: **if you're changing the schema or seed data, say so in the team
chat first.** Don't start editing `schema.sql` / `seed_data.sql` /
`mock.db` if someone else might be doing the same thing right now.
 
If you do change the schema or seed data:
1. Edit `database/schema.sql` and/or `database/seed_data.sql` (the
   human-readable source of truth).
2. Run `python database/build_db.py` to regenerate `mock.db` from them.
3. Commit all three files together in the same commit.
## Notebooks
 
- Run `nbstripout --install` once, locally (see README) — this strips
  cell outputs and execution counts before every commit, which avoids
  most of the noisy/fake merge conflicts notebooks cause.
- Prefer one notebook per person or per task over multiple people editing
  the same notebook on parallel branches — same binary-merge problem as
  the database, just for `.ipynb` instead of `.db`.
- Reusable logic (functions you'll use in more than one notebook) belongs
  in `src/`, not copy-pasted across notebooks.
