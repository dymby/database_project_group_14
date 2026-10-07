-- Author: roshikreddy
--
-- Question: Which neighbourhoods have the highest share of entire homes
-- rather than private rooms among their Airbnb listings?
--
-- Relevance: An entire home listed for tourists is a dwelling taken out of the
-- long-term housing stock, while a spare room is not. Neighbourhoods with a high
-- share are therefore losing the most housing to short stay rental, which is one
-- of the causes of the shortage described in our problem statement.
SELECT n.Name AS Neighbourhood,
       COUNT(*) AS Total_listings,
       SUM(CASE WHEN l.room_type = 'Entire home/apt' THEN 1 ELSE 0 END) AS Entire_homes,
       ROUND(100.0 * SUM(CASE WHEN l.room_type = 'Entire home/apt' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS Pct_entire_homes
FROM Listing l
JOIN Neighbourhood n ON l.Neighbourhood_NeighbourhoodID = n.NeighbourhoodID
GROUP BY n.NeighbourhoodID, n.Name
HAVING COUNT(*) >= 50
ORDER BY Pct_entire_homes DESC;
 
-- Author: roshikreddy
--
-- Question: Which entire homes are advertised with a minimum stay of 30 nights
-- or more?
--
-- Relevance: A whole apartment with a one-month minimum is not a holiday rental
-- but a long term let running on a short stay platform. These are homes being
-- used as housing while staying outside normal rental contracts and the
-- protections that come with them, so they matter when measuring how much
-- housing is really available to people looking to live in the city.
SELECT l.ListingID,
       l.Name,
       n.Name AS Neighbourhood,
       l.room_type,
       l.minimum_nights,
       l.price_per_night
FROM Listing l
JOIN Neighbourhood n ON l.Neighbourhood_NeighbourhoodID = n.NeighbourhoodID
WHERE l.minimum_nights >= 30
  AND l.room_type = 'Entire home/apt'
ORDER BY l.minimum_nights DESC, l.price_per_night;
