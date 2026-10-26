-- Venue Table
CREATE TABLE Venues
(
    venue_id SERIAL PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    venue_address TEXT NOT NULL
);

-- Teams Table
CREATE TABLE Teams
(
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    coach_name VARCHAR(100) NOT NULL
);

-- Players Table
CREATE TABLE Players
(
    player_id SERIAL PRIMARY KEY,
    team_id INT REFERENCES Teams(team_id),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    jersey_number INT NOT NULL,
    UNIQUE (team_id, jersey_number)
);  