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
