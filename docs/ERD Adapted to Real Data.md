# ERD - schema v2 (after week 5)

This diagram documents the schema **as implemented now** (`database/schema.sql`), so it can be
compared with the original ERD in [`Erd_report.pdf`](Erd_report.pdf).
GitHub renders the Mermaid below automatically.

Changes versus the week 2 ERD are listed under the diagram.

```mermaid
erDiagram
    City ||--o{ Postcode : "contains"
    City ||--o{ Neighbourhood : "contains"
    City ||--o{ address : "contains (no postcode)"
    Postcode ||--o{ address : "groups"
    address ||--o| House : "identifies"
    address ||--o{ People : "is home of"
    People ||--o| Renter : "is a"
    People ||--o| Landlord : "is a"
    Contract ||--o{ House : "applies to"
    Landlord ||--o{ Listing : "offers"
    Neighbourhood ||--o{ Listing : "locates"

    City {
        int CityID PK
        varchar Name UK
    }
    Neighbourhood {
        int NeighbourhoodID PK
        varchar Name
        int City_CityID FK
    }
    Postcode {
        text Postalcode PK "format NNNN AA"
        varchar Street
        int City_CityID FK
    }
    address {
        int addressID PK
        text Postalcode FK "NULL if unknown"
        varchar Street "only without postcode"
        int City_CityID FK "only without postcode"
        int Number
        text Letter "huisletter"
        varchar Addition "toevoeging"
        text bag_address_id UK "source id, NULL for mock"
    }
    People {
        int PeopleID PK
        varchar First_Name "nullable"
        varchar Last_Name "nullable"
        int Age "nullable"
        int address_addressID FK
        text source_host_id UK "Airbnb host, NULL for mock"
    }
    Renter {
        int People_PeopleID PK, FK
    }
    Landlord {
        int People_PeopleID PK, FK
    }
    Contract {
        int contractID PK
        int amount "> 0"
        date start_date
        date expiration_date "> start_date"
    }
    House {
        int address_addressID PK, FK
        int size_sqm "5..1000, floor area"
        int lot_size_sqm "plot area"
        int contract_contractID FK "nullable"
    }
    Listing {
        int ListingID PK "Airbnb id"
        text Name
        int Landlord_PeopleID FK "nullable"
        int Neighbourhood_NeighbourhoodID FK
        text room_type
        int price_per_night "nullable = not reported"
        int minimum_nights
        real latitude
        real longitude
        date last_review
    }
```

## What changed since the week 2 ERD

| Change | Why | Detail |
|---|---|---|
| **New entity `Postcode`** | 3NF fix | `Postalcode -> Street, City` was a transitive dependency inside `address`. See [`normalization_report.md`](normalization_report.md). `Street` and `City_CityID` moved out of `address`. |
| **New entities `Neighbourhood` and `Listing`** | Airbnb data has no street address | Listings attach to a neighbourhood, not to a `House`. |
| **`address` gained `Letter`, `Addition`** | real house numbers are `12A`, `12-2`, `12 1L` | week 2 modelled only `number (smallINT)` |
| **Source-id columns** (`bag_address_id`, `source_host_id`) | traceability, prevents double loading | not in the week 2 ERD |
| **`Age`, `First_Name` now optional** | Airbnb hosts have neither | week 2 assumed both always known |
| **`Postalcode` is TEXT, not INT** | `1015 NR` is not a number | week 2 listed `Postalcode (int)` |
| **`address.Postalcode` optional, `Street`/`City_CityID` on `address`** | Kaggle houses have no postcode | filled only when the postcode is unknown; the view `address_full` returns street and city for every address |
| **`House.lot_size_sqm`** | Kaggle gives the plot area, not the floor area | `size_sqm` is now optional, one of the two is required |

## Still not modelled

The week 2 ERD gives `Landlord/contractor` a `houseID` so a landlord manages houses.
**That link is still missing**, in week 3 and here. Until it is added, the database cannot
answer "who rents out this house", which is central to the project's goal. Adding it
requires a group decision on cardinality, so it is deliberately not invented here.

`Renter` also still has no attributes. The README describes matching renters to houses on
maximum rent, location and contract dates, but none of those are stored.
