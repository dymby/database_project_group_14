-- Author: roshikreddy
/*Joins each listing to its neighbourhood, groups the listings by neighbourhood, 
and counts two things per group at once: how many listings there are in total, 
and how many of those are entire homes. Dividing one by the other gives the percentage, 
and groups with fewer than 50 listings are dropped before sorting by that percentage. */
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
 
/*Joins each listing to its neighbourhood, then filters down to the rows meeting two conditions at the same time: 
the listing is an entire home, and its minimum stay is at least 30 nights. No grouping is involved — 
it returns the individual listings, ordered by the longest minimum stay first. */
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
