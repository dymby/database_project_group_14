-- Rent per square metre of the rented houses
SELECT c.Name AS City,
       a.Street,
       a.Number,
       h.size_sqm,
       ct.amount AS Monthly_Rent,
       ROUND(1.0 * ct.amount / h.size_sqm, 2) AS Rent_per_sqm
FROM House h
JOIN address_full a ON h.address_addressID = a.addressID
JOIN City c ON a.City_CityID = c.CityID
JOIN Contract ct ON h.contract_contractID = ct.contractID
ORDER BY Rent_per_sqm;

-- Renters, what they pay and when their contract ends
SELECT p.First_Name,
       p.Last_Name,
       c.Name AS City,
       ct.amount AS Monthly_Rent,
       ct.expiration_date
FROM Renter r
JOIN People p ON r.People_PeopleID = p.PeopleID
JOIN House h ON p.address_addressID = h.address_addressID
JOIN address_full a ON h.address_addressID = a.addressID
JOIN City c ON a.City_CityID = c.CityID
JOIN Contract ct ON h.contract_contractID = ct.contractID
ORDER BY ct.expiration_date;