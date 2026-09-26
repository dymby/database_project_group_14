--retrieves all houses sorted by amount, highest first.
SELECT
    House.address_addressID AS HouseID,
    address.Street,
    address.Number,
    City.Name AS City,
    House.size_sqm AS Size_sqm,
    Contract.amount AS Monthly_Rent,
    People.First_Name || ' ' || People.Last_Name AS Landlord
FROM House
JOIN address
    ON House.address_addressID = address.addressID
JOIN City
    ON address.City_CityID = City.CityID
JOIN Contract
    ON House.contract_contractID = Contract.contractID
JOIN People
    ON People.address_addressID = address.addressID
JOIN Landlord
    ON Landlord.People_PeopleID = People.PeopleID
ORDER BY Contract.amount DESC;
--Select all Cities that have multiple addresses?
SELECT
    City.Name AS City,
    COUNT(House.address_addressID) AS Number_of_Houses,
    ROUND(AVG(Contract.amount), 2) AS Average_Rent
FROM House
JOIN address
    ON House.address_addressID = address.addressID
JOIN City
    ON address.City_CityID = City.CityID
JOIN Contract
    ON House.contract_contractID = Contract.contractID
GROUP BY City.CityID, City.Name
HAVING COUNT(House.address_addressID) > 1
ORDER BY Average_Rent DESC;
--retrieves the houses that have a higher rent then average (highest first)
SELECT
    House.address_addressID AS HouseID,
    City.Name AS City,
    address.Street,
    address.Number,
    Contract.amount AS Monthly_Rent
FROM House
JOIN address
    ON House.address_addressID = address.addressID
JOIN City
    ON address.City_CityID = City.CityID
JOIN Contract
    ON House.contract_contractID = Contract.contractID
WHERE Contract.amount > (
    SELECT AVG(amount)
    FROM Contract
)
ORDER BY Contract.amount DESC;

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

