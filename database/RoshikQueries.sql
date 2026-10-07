-- Author: roshikreddy-netizen
-- Which neighbourhoods have the highest share of entire homes rather than rooms?
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

-- Author: roshikreddy-netizen
-- Which entire homes are listed with a minimum stay of 30 nights or more?
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
