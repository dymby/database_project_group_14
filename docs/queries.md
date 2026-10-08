# Answers that our queries provide

# MarcPyioQueries:

**1.)** This query retrieves `houses` where only one person lives, since it people and houses entity relation allows for multiple people to live in a house it helps people that are looking for single person households, for example if you do not want to share a kitchen or a bath room. This is important for our social challenge since its allows more nuance when it comes to choosing a home. 

**2.)** This query retrieves all `contracts` that end in January 2027 and where their monthly `amount` = 400. Why is this important? If someone is looking for housing in the netherlands (no specific city) and is arriving in January 2027 it makes no sense for him to view houses which contract only ends in 2030. The `amount` parameter is there for people searching for cheaper places. 

# RoshikQueries:

**1.)** This query retrieves the neighbourhoods with the highest share of listings that are entire homes rather than private rooms, showing the total number of listings, how many of those are entire homes, and the percentage. Only neighbourhoods with at least 50 listings are included, since a neighbourhood with two listings could otherwise show 100% without meaning anything. This matters for our social challenge because an entire home rented out to tourists is a property that has left the long-term housing stock, while a spare room has not. Neighbourhoods like Bos en Lommer and Westerpark are therefore the areas losing the most housing to short-stay rental.

**2.)** This query retrieves all listings that are entire homes and require a minimum stay of 30 nights or more, sorted with the longest minimum stay first. Why is this important? A whole apartment with a one-month minimum is not really a holiday rental but a long-term let running on a short-stay platform, often to work around the 30-night cap on short-stay rentals in Amsterdam. These homes are being used as housing while staying outside normal rental contracts and the protections that come with them, so they matter when measuring how much housing is genuinely available to people who want to live in the city rather than visit it.
