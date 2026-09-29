# Week 5 - Real-world data sources

Raw copies are stored unchanged in `data/raw/`. Both datasets are open, need no registration and no payment.

| | Dataset A - Inside Airbnb | Dataset B - Amsterdam BAG |
|---|---|---|
| **What** | Airbnb listings in Amsterdam (host, neighbourhood, room type, nightly price, coordinates) | Basisregistratie Adressen en Gebouwen: addresses and dwellings (postcode, house number, surface area) |
| **Publisher** | Inside Airbnb | Gemeente Amsterdam (open data portal) |
| **Source** | https://insideairbnb.com/get-the-data/ (Amsterdam, `listings.csv`) | https://data.overheid.nl/dataset/cxsrcn9ahipipq - API `https://api.data.amsterdam.nl/v1/bag/{nummeraanduidingen,verblijfsobjecten,openbareruimtes}?_format=csv&_pageSize=500` |
| **Publication date** | Compiled 15 June 2026 | Dataset last modified 4 November 2022 (records themselves carry registration dates from 2007 onwards) |
| **License** | Creative Commons Attribution 4.0 (CC BY 4.0) | CC0 1.0 (public domain dedication) |
| **Raw files** | `airbnb-amsterdam-listings.csv` (10,465 rows) | `bag-nummeraanduidingen.csv` (500), `bag-verblijfsobjecten.csv` (500), `bag-openbareruimtes-lookup.csv` (6 street names) |
| **Covers in our DB** | `People`/`Landlord` (hosts), `Neighbourhood`, `Listing` | `Postcode`, `address`, `House` (size), `City` |

## Complementary, not a subset (A not-subset-of B)
- A has hosts, prices and neighbourhoods that B does not contain; B has postcodes, house numbers and floor areas that A does not contain.
- They overlap only at city level (both Amsterdam). There is no shared key: Airbnb gives no street address and the BAG has no rent or owner. Because of this the two datasets are loaded side by side and are **not joined per property** (see limitations in `docs/week5_review.md`).
- Both datasets have well over 50 unique rows (A: 10,465 listings / 9,104 hosts; B: 499 usable addresses / 451 dwellings).

## Notes on how the BAG sample was obtained
The API returns records in ID order, so the 500-row samples are the first 500 records (mostly Amsterdam-Oost and part of the Jordaan; 25 postcodes, 6 streets), not a random sample. The street names for the 6 street IDs were looked up by hand in the API (`.../openbareruimtes/<id>`) because the first 500 public spaces do not include them; the mapping is stored in `bag-openbareruimtes-lookup.csv`.

Attribution required by CC BY 4.0: "Data from Inside Airbnb (insideairbnb.com), CC BY 4.0."
