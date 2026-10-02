
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS City (
    CityID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(45) NOT NULL UNIQUE
);

-- Create Postcode table
CREATE TABLE IF NOT EXISTS Postcode (
    Postalcode TEXT PRIMARY KEY
        CHECK (Postalcode GLOB '[0-9][0-9][0-9][0-9] [A-Z][A-Z]'),
    Street VARCHAR(45) NOT NULL,
    City_CityID INTEGER NOT NULL,
    CONSTRAINT fk_postcode_city
        FOREIGN KEY (City_CityID)
        REFERENCES City(CityID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Create address table
-- Street and City_CityID are only filled when the postcode is unknown
CREATE TABLE IF NOT EXISTS address (
    addressID INTEGER PRIMARY KEY AUTOINCREMENT,
    Postalcode TEXT,
    Street VARCHAR(45),
    City_CityID INTEGER,
    Number INTEGER CHECK (Number IS NULL OR typeof(Number) = 'integer'),
    Letter TEXT,
    Addition VARCHAR(45),
    bag_address_id TEXT UNIQUE,
    CONSTRAINT fk_address_postcode
        FOREIGN KEY (Postalcode)
        REFERENCES Postcode(Postalcode)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_address_city
        FOREIGN KEY (City_CityID)
        REFERENCES City(CityID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT ck_address_postcode_or_street
        CHECK ((Postalcode IS NOT NULL AND Street IS NULL AND City_CityID IS NULL)
            OR (Postalcode IS NULL AND Street IS NOT NULL AND City_CityID IS NOT NULL))
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_address_unique
    ON address (Postalcode, Number, IFNULL(Letter, ''), IFNULL(Addition, ''))
    WHERE Postalcode IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_address_unique_no_postcode
    ON address (City_CityID, Street, Number, IFNULL(Letter, ''), IFNULL(Addition, ''))
    WHERE Postalcode IS NULL;

-- Create People table
CREATE TABLE IF NOT EXISTS People (
    PeopleID INTEGER PRIMARY KEY AUTOINCREMENT,
    First_Name VARCHAR(45),
    Last_Name VARCHAR(45),
    Age INTEGER CHECK (Age IS NULL OR Age BETWEEN 0 AND 120),
    address_addressID INTEGER,
    source_host_id TEXT UNIQUE,
    CONSTRAINT fk_people_address
        FOREIGN KEY (address_addressID)
        REFERENCES address(addressID)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- Create Renter table
CREATE TABLE IF NOT EXISTS Renter (
    People_PeopleID INTEGER PRIMARY KEY,
    CONSTRAINT fk_renter_people
        FOREIGN KEY (People_PeopleID)
        REFERENCES People(PeopleID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Create Landlord table
CREATE TABLE IF NOT EXISTS Landlord (
    People_PeopleID INTEGER PRIMARY KEY,
    CONSTRAINT fk_landlord_people
        FOREIGN KEY (People_PeopleID)
        REFERENCES People(PeopleID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- Create Contract table
CREATE TABLE IF NOT EXISTS Contract (
    contractID INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER CHECK (amount > 0),
    start_date DATE NOT NULL,
    expiration_date DATE,
    CONSTRAINT ck_contract_dates
        CHECK (expiration_date IS NULL OR expiration_date > start_date)
);

-- Create House table
CREATE TABLE IF NOT EXISTS House (
    address_addressID INTEGER PRIMARY KEY,
    size_sqm INTEGER CHECK (size_sqm IS NULL OR size_sqm BETWEEN 5 AND 1000),
    lot_size_sqm INTEGER CHECK (lot_size_sqm IS NULL OR (typeof(lot_size_sqm) = 'integer' AND lot_size_sqm > 0)),
    contract_contractID INTEGER,
    CONSTRAINT fk_house_address
        FOREIGN KEY (address_addressID)
        REFERENCES address(addressID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_house_contract
        FOREIGN KEY (contract_contractID)
        REFERENCES Contract(contractID)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT ck_house_has_a_size
        CHECK (size_sqm IS NOT NULL OR lot_size_sqm IS NOT NULL)
);

-- Create Neighbourhood table
CREATE TABLE IF NOT EXISTS Neighbourhood (
    NeighbourhoodID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(45) NOT NULL,
    City_CityID INTEGER NOT NULL,
    CONSTRAINT uq_neighbourhood_name_city
        UNIQUE (Name, City_CityID),
    CONSTRAINT fk_neighbourhood_city
        FOREIGN KEY (City_CityID)
        REFERENCES City(CityID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Create Listing table
CREATE TABLE IF NOT EXISTS Listing (
    ListingID INTEGER PRIMARY KEY,
    Name TEXT,
    Landlord_PeopleID INTEGER,
    Neighbourhood_NeighbourhoodID INTEGER NOT NULL,
    room_type TEXT NOT NULL
        CHECK (room_type IN ('Entire home/apt', 'Private room', 'Shared room', 'Hotel room')),
    price_per_night INTEGER CHECK (price_per_night IS NULL OR price_per_night > 0),
    minimum_nights INTEGER CHECK (minimum_nights IS NULL OR minimum_nights >= 1),
    latitude REAL,
    longitude REAL,
    last_review DATE,
    CONSTRAINT fk_listing_landlord
        FOREIGN KEY (Landlord_PeopleID)
        REFERENCES Landlord(People_PeopleID)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_listing_neighbourhood
        FOREIGN KEY (Neighbourhood_NeighbourhoodID)
        REFERENCES Neighbourhood(NeighbourhoodID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Create address_full view
CREATE VIEW IF NOT EXISTS address_full AS
SELECT
    address.addressID,
    address.Postalcode,
    COALESCE(Postcode.Street, address.Street) AS Street,
    COALESCE(Postcode.City_CityID, address.City_CityID) AS City_CityID,
    address.Number,
    address.Letter,
    address.Addition
FROM address
LEFT JOIN Postcode
    ON Postcode.Postalcode = address.Postalcode;
