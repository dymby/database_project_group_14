--retrieves the size of the house and the people associated with it. This helps in retrieving who is already living there
SELECT h.size_sqm, COUNT(r.PeopleID) AS total_people
FROM House h JOIN address a USING (address_id)
JOIN People p ON a.address_id = p.address_id
JOIN Renter r ON p.PeopleID = r.PeopleID
GROUP BY h.address_address_id, h.size_sqm;
HAVING total_people < 2
ORDER total_people DESC;

--retrieves all contract that end in January 2027 and where their monthly amount is 400.
SELECT a.cityID, c.amount, c.expiration_date
FROM Contract c JOIN House h USING (contractID)
JOIN Address a ON h.address_id = a.address_id
WHERE c.expiration_date LIKE '%2027-01%' AND c.amount < 400;
ORDER c.expiration_date; --automatically depicts the earliest one first