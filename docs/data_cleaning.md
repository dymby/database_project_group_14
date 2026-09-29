# Week 5 - Data cleaning and transformation

All steps are implemented in `database/load_real_data.py` (run through `python database/build_db.py --yes`).
Counts below come from the actual run.

## 1. How is missing data reported?
| Dataset | Field | Reporting | Count | Treatment |
|---|---|---|---|---|
| Airbnb | `price` | empty cell | 3,994 of 10,465 | stored as `NULL` in `Listing.price_per_night` (never 0); AVG/COUNT ignore it |
| Airbnb | `host_id` | empty cell | 96 | listing kept, `Landlord_PeopleID = NULL` |
| Airbnb | `host_name` | empty cell | 238 rows (96 of them also lack a `host_id`); 37 loaded hosts have no name | `People.First_Name = NULL` (column made nullable) |
| Airbnb | `neighbourhood_group`, `license` | entirely empty / 319 empty | 10,465 / 319 | not loaded |
| Airbnb | `last_review` | empty cell | 1,033 | `NULL` |
| BAG | `postcode` | empty cell | 1 address | address dropped (postcode is required and is the key to street and city) |
| BAG | `huisletter`, `huisnummertoevoeging` | empty cell | 397 / 149 empty of 499 loaded addresses | `NULL` = house number has no letter/addition |
| BAG | many columns (`eindGeldigheid`, `statusCode`, ...) | 100% empty | - | not loaded |
| BAG | `oppervlakte` | not missing, but placeholder-like values 1 m2 (x2) and 1205 m2 (x1) | 3 | treated as invalid, dwelling not loaded; `CHECK (size_sqm BETWEEN 5 AND 1000)` |

## 2. How are dates formatted?
- Airbnb `last_review`: ISO `YYYY-MM-DD`, parsed and re-emitted as ISO text in a `DATE` column.
- BAG `registratiedatum`, `beginGeldigheid`: ISO with time (`2010-11-04T21:57:01`). Not needed by our schema, so not loaded.
- BAG contains the placeholder date `1005-01-01` (244 of 500 addresses) for records without a known start of validity - it is not a real date. We do not use it.
- Our own `Contract` dates are ISO `YYYY-MM-DD` text (SQLite has no date type). The mock data was quoted with double quotes, which SQLite accepts as a fallback but standard SQL does not; changed to single quotes.

## 3. Are there duplicate records?
- Airbnb: 0 duplicate listing `id`s, 0 fully duplicated rows. 9,104 distinct hosts appear in 10,465 listings, so the host is repeated (correctly) and is stored **once** in `People`, referenced by `Listing`.
- BAG: 0 duplicate address ids, 0 duplicate (postcode, number, letter, addition). Added `UNIQUE INDEX ux_address_unique` so the same address can never be inserted twice.
- 46 dwellings refer to an address id that is not in our 500-address sample (dropped - a dwelling without an address cannot be stored in `House`).

## 4. Inconsistent naming conventions
| Issue | Example | Fix |
|---|---|---|
| Postcode format differs between sources | BAG `1015NR`, mock data `5611 AB` | normalised to `NNNN AA` with a space; `CHECK (Postalcode GLOB ...)` |
| Column naming style | BAG `heeftHoofdadresId` (camelCase Dutch), Airbnb `host_name` (snake_case English), our schema `Street`, `address` (mixed case) | mapped explicitly in the loader; schema names left as-is (mixed style already existed - see future work) |
| IDs with leading zeros | BAG `0363200000006110` | kept as text (`bag_address_id`); reading as integer would silently drop the zero |
| IDs stored as floats | Airbnb `host_id` read as `124245.0` | cast to text without `.0` (`source_host_id`) |
| Host names contain several people / businesses | `Edwin & Ann`, `SWEETS Hotel` (about 209 rows) | stored unchanged in `First_Name`, `Last_Name = NULL`; cannot be split reliably |
| Whitespace | 3 listing names with leading/trailing spaces | stripped |
| Neighbourhood names | Consistent (22 distinct, e.g. `De Pijp - Rivierenbuurt`) | none needed; stored once in `Neighbourhood` |
| Currency/unit | Airbnb `price` has no unit column | assumed EUR per night (Amsterdam file); stored as integer, rounded |

## 5. Other transformations
- BAG address + dwelling are joined on `heeftHoofdadresId = nummeraanduiding.identificatie`.
- Street name is not in the address table (only an id): resolved through the `openbareruimten` lookup.
- Airbnb nightly prices are **not** converted to a monthly rent and **not** put into `Contract.amount`: a nightly short-stay price is not comparable to a monthly rental contract.
- Price outliers (max 11,412 EUR/night) are kept; they are extreme but not impossible (large villas/boats).

## 6. Violations of the week 3 schema found while integrating (fixed in schema v2)
Verified by inserting the real values into the old schema (see `docs/schema_changes.md`).
