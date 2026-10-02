# Normalization check with real data (week 5 addition to the week 2 report)

This extends section 5 ("Normal Form") of [`Erd_report.pdf`](Erd_report.pdf), which concluded that the design was in 3NF. Testing that conclusion against real data showed it was **too optimistic**: one transitive dependency was missed.

Notation: `A -> B` means A functionally determines B.

## Result in one line
The real data exposed **one 3NF violation** (in `address`) and two smaller 1NF/atomicity issues. The 3NF violation is fixed in schema v2; the other two are accepted and documented.

## 0. What the week 2 report claimed, and what it missed
Section 5.3 of the week 2 report argued that `address` is in 3NF because the city *name* is not stored in `address`; only `CityID` is, so `addressID -> CityID -> CityName` is avoided. That reasoning is correct as far as it goes.

What it missed is a second transitive dependency through a **non-key attribute that was kept inside the table**: `Postalcode`. The week 2 analysis treated `Postalcode`, `Street` and `number` as independent attributes of the address, but in reality the postcode determines the street. Mock data could not reveal this, because each of the 10 mock addresses had a unique postcode, so every functional dependency looked trivially satisfied. With 499 real addresses spread over only 25 postcodes, the dependency becomes visible and testable.

**Lesson for the report:** a normal-form check on invented data is close to vacuous. A dependency only shows up once several rows share a determinant value.

## 1. 3NF violation found: `address` (schema v1)
Schema v1: `address(addressID PK, Postalcode, Street, Number, City_CityID)`

Dependencies that hold in the real BAG data (checked on all 499 addresses):
- `addressID -> Postalcode, Number, ...` (PK)
- **`Postalcode -> Street, City`** - every one of the 25 postcodes maps to exactly one street (checked by an assertion in `load_data.py`); in the Netherlands a full 6-character postcode lies in one street of one place.

`Postalcode` is not a key of `address` and `Street`, `City` are not part of a key, so `addressID -> Postalcode -> Street` is a **transitive dependency: 3NF violated** (2NF and 1NF are fine because the key is a single column).

Symptom in the data: the 348 dwellings in *Eerste Atjehstraat* would repeat the street name and city 348 times, and one typo would make the same postcode belong to two streets (update anomaly).

Fix (schema v2): decompose into
- `Postcode(Postalcode PK, Street, City_CityID)`
- `address(addressID PK, Postalcode FK, Number, Letter, Addition)`

Addition for the Kaggle data (no postcode): `address` also has `Street` and `City_CityID`, but a `CHECK` allows them only when `Postalcode` is `NULL`. So in every row the street is stored in exactly one place, and the dependency `Postalcode -> Street` can never appear inside `address`. For those rows `Street -> City` does not hold either (the same street name exists in several cities), so no new transitive dependency is introduced.

Both tables now have only dependencies on their key. Assumption: postcode -> street holds for the whole Netherlands. Rare exceptions exist in reality; if the group wants to be strict, use (Postalcode, Number) as the determinant instead.

## 2. Other tables
| Table | Non-trivial dependencies | 3NF? |
|---|---|---|
| `City` | `CityID -> Name` | yes |
| `Neighbourhood` | `NeighbourhoodID -> Name, City` | yes (neighbourhood -> city is stored once, not per listing) |
| `People` | `PeopleID -> everything`; `source_host_id -> First_Name` (candidate key, UNIQUE) | yes: `source_host_id` is a candidate key, so this is not a violation (BCNF also OK) |
| `Renter`, `Landlord` | PK only | yes |
| `Contract`, `House` | `PK -> other columns` (`size_sqm` and `lot_size_sqm` are independent measurements) | yes |
| `Listing` | `ListingID -> all`; host attributes were kept in `People`, not repeated per listing | yes |

Insertion in normalized form: the Airbnb file repeats host id and host name on every listing row (e.g. 9,104 hosts over 10,465 listings; a host with 24 listings appears 24 times). The loader inserts each host once into `People` and each neighbourhood once into `Neighbourhood`; `Listing` only stores the foreign keys. The raw file itself was **not** in 3NF (`host_id -> host_name`, `neighbourhood -> ...`, `calculated_host_listings_count` is derived from the other rows) - that derived column is deliberately not loaded.

## 3. Accepted, not decomposed
- **Atomicity (1NF), host names**: about 209 host names contain several people or a business (`Edwin & Ann`). `First_Name` therefore is not always a single first name. Not splittable reliably; documented.
- **Geographic redundancy**: `(latitude, longitude)` determines the neighbourhood in reality, so `Listing.Neighbourhood` is derivable from the coordinates. This is a dependency on non-key attributes, but it needs geometry (polygons), not a plain functional dependency we can enforce in SQL. Kept; the neighbourhood column is what the source provides.
- `Addition` sometimes combines floor and side (`1L`), which is not fully atomic; kept as provided by the BAG.
