INSERT INTO City (Name) VALUES
    ("Eindhoven"),
    ("Amsterdam"),
    ("Rotterdam"),
    ("Utrecht"),
    ("Tilburg");

INSERT INTO address (Postalcode, Street, Number, City_CityID) VALUES
    ("5611 AB", "Kerkstraat", 12, 1),
    ("5612 CD", "Stationsweg", 45, 1),
    ("1012 AB", "Prinsengracht", 120, 2),
    ("1017 CD", "Leidsegracht", 88, 2),
    ("3011 AA", "Coolsingel", 25, 3),
    ("3012 BB", "Westblaak", 67, 3),
    ("3511 CC", "Oudegracht", 14, 4),
    ("3521 DD", "Croeselaan", 33, 4),
    ("5038 EE", "Heuvelstraat", 9, 5),
    ("5041 FF", "Besterdring", 21, 5);

INSERT INTO People (First_Name, Last_Name, Age, address_addressID) VALUES
    ("Jan", "de Vries", 34, 1),
    ("Sophie", "Jansen", 28, 2),
    ("Mark", "Bakker", 45, 3),
    ("Lisa", "Smit", 31, 4),
    ("Thomas", "Visser", 52, 5),
    ("Emma", "Meijer", 26, 6),
    ("Daan", "Mulder", 39, 7),
    ("Anna", "de Boer", 42, 8),
    ("Lucas", "Bos", 29, 9),
    ("Nina", "Vos", 36, 10);

INSERT INTO Renter (People_PeopleID) VALUES
    (1),
    (2),
    (3),
    (4),
    (5);

INSERT INTO Landlord (People_PeopleID) VALUES
    (6),
    (7),
    (8),
    (9),
    (10);

INSERT INTO Contract (amount, start_date, expiration_date) VALUES
    (1250, "2025-01-01", "2026-01-01"),
    (1450, "2025-03-01", "2026-03-01"),
    (1100, "2025-06-01", "2026-06-01"),
    (1800, "2025-09-01", "2026-09-01"),
    (950, "2025-11-01", "2026-11-01"),
    (1600, "2026-01-01", "2027-01-01");

INSERT INTO House (address_addressID, size_sqm, contract_contractID) VALUES
    (1, 85, 1),
    (2, 110, 2),
    (3, 65, 3),
    (4, 95, 4),
    (5, 120, 5),
    (6, 75, 6),
    (7, 140, 1),
    (8, 90, 2),
    (9, 60, 3),
    (10, 105, 4);
