
CREATE TABLE IF NOT EXISTS City (
    CityID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(45) NOT NULL
);

-- Create address table
CREATE TABLE IF NOT EXISTS address (
    addressID INTEGER PRIMARY KEY AUTOINCREMENT,
    Postalcode INTEGER NOT NULL,
    Street VARCHAR(45) NOT NULL,
    Number INTEGER,
    City_CityID INTEGER,
    CONSTRAINT fk_address_city
        FOREIGN KEY (City_CityID)
        REFERENCES City(CityID)
        ON UPDATE SET NULL
        ON DELETE SET NULL
);

-- Create People table
CREATE TABLE IF NOT EXISTS People (
    PeopleID INTEGER PRIMARY KEY AUTOINCREMENT,
    First_Name VARCHAR(45) NOT NULL,
    Last_Name VARCHAR(45),
    Age INTEGER NOT NULL,
    address_addressID INTEGER,
    CONSTRAINT fk_people_address
        FOREIGN KEY (address_addressID)
        REFERENCES address(addressID)
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
    expiration_date DATE
);

-- Create House table
CREATE TABLE IF NOT EXISTS House (
    address_addressID INTEGER PRIMARY KEY,
    size_sqm INTEGER NOT NULL CHECK (size_sqm > 0),
    contract_contractID INTEGER,
    CONSTRAINT fk_house_address
        FOREIGN KEY (address_addressID)
        REFERENCES address(addressID),
    CONSTRAINT fk_house_contract
        FOREIGN KEY (contract_contractID)
        REFERENCES Contract(contractID)
        ON UPDATE SET NULL
        ON DELETE SET NULL
);