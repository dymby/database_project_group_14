-- Q1: houses by rent
SELECT
    House.address_addressID AS HouseID,
    address_full.Street,
    address_full.Number,
    City.Name AS City,
    House.size_sqm AS Size_sqm,
    Contract.amount AS Monthly_Rent,
    People.First_Name || ' ' || People.Last_Name AS Landlord
FROM House
JOIN address_full
    ON House.address_addressID = address_full.addressID
JOIN City
    ON address_full.City_CityID = City.CityID
JOIN Contract
    ON House.contract_contractID = Contract.contractID
LEFT JOIN People
    ON People.address_addressID = address_full.addressID
    AND People.PeopleID IN (SELECT People_PeopleID FROM Landlord)
ORDER BY Contract.amount DESC;
-- Q2: cities with multiple rented houses
SELECT
    City.Name AS City,
    COUNT(House.address_addressID) AS Number_of_Houses,
    ROUND(AVG(Contract.amount), 2) AS Average_Rent
FROM House
JOIN address_full
    ON House.address_addressID = address_full.addressID
JOIN City
    ON address_full.City_CityID = City.CityID
JOIN Contract
    ON House.contract_contractID = Contract.contractID
GROUP BY City.CityID, City.Name
HAVING COUNT(House.address_addressID) > 1
ORDER BY Average_Rent DESC;
-- Q3: houses with rent above average
SELECT
    House.address_addressID AS HouseID,
    City.Name AS City,
    address_full.Street,
    address_full.Number,
    Contract.amount AS Monthly_Rent
FROM House
JOIN address_full
    ON House.address_addressID = address_full.addressID
JOIN City
    ON address_full.City_CityID = City.CityID
JOIN Contract
    ON House.contract_contractID = Contract.contractID
WHERE Contract.amount > (
    SELECT AVG(amount)
    FROM Contract
)
ORDER BY Contract.amount DESC;
-- Q4: people who are neither renter nor landlord
SELECT
    People.PeopleID,
    People.First_Name,
    People.Last_Name,
    People.Age
FROM People
LEFT JOIN Renter
    ON People.PeopleID = Renter.People_PeopleID
LEFT JOIN Landlord
    ON People.PeopleID = Landlord.People_PeopleID
WHERE Renter.People_PeopleID IS NULL
  AND Landlord.People_PeopleID IS NULL;
-- Q5: listings and average price per neighbourhood
SELECT
    Neighbourhood.Name AS Neighbourhood,
    COUNT(*) AS Number_of_Listings,
    ROUND(AVG(Listing.price_per_night), 2) AS Average_Price
FROM Listing
JOIN Neighbourhood
    ON Listing.Neighbourhood_NeighbourhoodID = Neighbourhood.NeighbourhoodID
GROUP BY Neighbourhood.NeighbourhoodID, Neighbourhood.Name
ORDER BY Average_Price DESC;
-- Q6: landlords with more than one listing
SELECT
    People.PeopleID,
    People.First_Name,
    COUNT(*) AS Number_of_Listings
FROM Listing
JOIN People
    ON Listing.Landlord_PeopleID = People.PeopleID
GROUP BY People.PeopleID, People.First_Name
HAVING COUNT(*) > 1
ORDER BY Number_of_Listings DESC, People.PeopleID;
-- Q7: houses and average size per street in Amsterdam
SELECT
    Postcode.Street,
    COUNT(*) AS Number_of_Houses,
    ROUND(AVG(House.size_sqm), 1) AS Average_Size_sqm
FROM House
JOIN address
    ON House.address_addressID = address.addressID
JOIN Postcode
    ON address.Postalcode = Postcode.Postalcode
JOIN City
    ON Postcode.City_CityID = City.CityID
WHERE City.Name = 'Amsterdam'
GROUP BY Postcode.Street
ORDER BY Number_of_Houses DESC;
-- Q8: listings without a price per room type
SELECT
    room_type,
    COUNT(*) AS Number_of_Listings,
    COUNT(*) - COUNT(price_per_night) AS Without_Price,
    ROUND(100.0 * (COUNT(*) - COUNT(price_per_night)) / COUNT(*), 1) AS Percent_Without_Price
FROM Listing
GROUP BY room_type
ORDER BY Number_of_Listings DESC;
-- Q9: average lot size per city with at least 20 houses
SELECT
    City.Name AS City,
    COUNT(*) AS Number_of_Houses,
    ROUND(AVG(House.lot_size_sqm), 1) AS Average_Lot_Size_sqm
FROM House
JOIN address_full
    ON House.address_addressID = address_full.addressID
JOIN City
    ON address_full.City_CityID = City.CityID
WHERE House.lot_size_sqm IS NOT NULL
GROUP BY City.CityID, City.Name
HAVING COUNT(*) >= 20
ORDER BY Average_Lot_Size_sqm DESC;

