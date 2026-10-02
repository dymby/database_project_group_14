# Schema v1 (week 3) -> v2 (week 5)

Each change was triggered by a concrete problem when loading the real data. "Old schema test" = the real value was inserted into the week 3 schema in a test database.

| # | Problem in real data | Old schema behaviour | Change in v2 |
|---|---|---|---|
| 1 | Postcodes like `1015 NR` | `Postalcode INTEGER` silently **accepted** text (SQLite type affinity) - the column type was wrong from the start (mock data already used `"5611 AB"`) | `Postalcode TEXT` with `CHECK (GLOB 'NNNN AA')` |
| 2 | Postcode always determines street and city | `Street` and `City_CityID` stored per address -> **3NF violation** (see `normalization_report.md`) | new table `Postcode(Postalcode PK, Street, City_CityID)`; `address` references it |
| 3 | House numbers with letter/addition (`12A`, `12 1L`) | only `Number INTEGER`, information lost | added `Letter`, `Addition` |
| 4 | Same address could be entered twice | no uniqueness | `UNIQUE INDEX (Postalcode, Number, Letter, Addition)` |
| 5 | Airbnb hosts have no age | `People.Age NOT NULL` -> **rejected** | `Age` nullable, `CHECK (Age IS NULL OR Age BETWEEN 0 AND 120)` |
| 6 | 238 listings have no host name | `First_Name NOT NULL` -> **rejected** | `First_Name` nullable |
| 7 | Dwellings of 1 m2 and 1205 m2 | `size_sqm > 0` **accepted** both | `CHECK (size_sqm BETWEEN 5 AND 1000)` |
| 8 | Need to trace rows back to the source / avoid double loading | no source ids | `address.bag_address_id UNIQUE`, `People.source_host_id UNIQUE` |
| 9 | Airbnb listings have no street address but do have neighbourhood, price/night, room type | no place to store them | new tables `Neighbourhood` and `Listing` |
| 10 | Inconsistent city spelling risk | `City.Name` not unique | `City.Name UNIQUE` |
| 11 | Contract dates | no check on order | `CHECK (expiration_date > start_date)` |
| 12 | Kaggle houses have a street and city but no postcode | `Postalcode NOT NULL` -> **rejected** | `address.Postalcode` nullable; `address.Street` + `address.City_CityID` filled **only** when the postcode is unknown (`CHECK`: exactly one of the two forms). View `address_full` gives street and city for every address |
| 13 | Kaggle gives the lot size (up to 120,615 m2), not the floor area | would be mixed into `size_sqm` and break change 7 | new column `House.lot_size_sqm`; `size_sqm` nullable; `CHECK` that at least one is given |
| 14 | Change 4 did not work: SQLite treats two `NULL` letters as different, so `12` could be inserted twice | duplicates **accepted** | unique indexes on `IFNULL(Letter,'')`, `IFNULL(Addition,'')`, one for addresses with and one for addresses without postcode |
| 15 | A house number arrived as raw bytes from pandas and was **accepted** (type affinity again, as in change 1) | wrong type stored silently | `CHECK (typeof(Number) = 'integer')`, same for `lot_size_sqm` |
| 16 | Deleting rows | `House -> address` and `People -> address` had no rule; `ON UPDATE SET NULL` cut the link when a key changed | explicit rule on every foreign key, see below |

## What happens when a row is deleted

| Delete of... | Effect | Rule |
|---|---|---|
| `People` | their `Renter`/`Landlord` row is deleted too; their `Listing`s stay, with `Landlord_PeopleID = NULL` | `CASCADE`, then `SET NULL` |
| `Contract` | houses stay, `contract_contractID = NULL` | `SET NULL` |
| `address` that has a `House` | refused (delete the house first) | `RESTRICT` |
| `address` where people live | people stay, `address_addressID = NULL` | `SET NULL` |
| `City` in use, `Postcode` in use, `Neighbourhood` with listings | refused | `RESTRICT` |

Every foreign key is `ON UPDATE CASCADE`. All of this is tested in `tests/test_database.py`.

SQLite only enforces these rules on a connection that ran `PRAGMA foreign_keys = ON` (`src/db.py` and all our scripts do). After deleting through another tool, `python database/check_db.py` reports any orphaned rows.
