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
    UNIQUE (team_id, jersey_number)  --constraint
);  

-- Matches Table
CREATE TABLE Matches
(
    match_id SERIAL PRIMARY KEY,
    home_team_id INT REFERENCES Teams(team_id) ON DELETE CASCADE,
    away_team_id INT REFERENCES Teams(team_id) ON DELETE CASCADE,
    venue_id INT REFERENCES Venues(venue_id) ON DELETE SET NULL,
    match_date TIMESTAMP NOT NULL,
    home_score INT DEFAULT 0,
    away_score INT DEFAULT 0,
    CONSTRAINT check_different_teams CHECK (home_team_id != away_team_id) --constraint
);

-- Player Match Stats Table
CREATE TABLE Player_Match_Stats
(
    stat_id SERIAL PRIMARY KEY,
    match_id INT REFERENCES Matches(match_id) ON DELETE CASCADE,
    player_id INT REFERENCES Players(player_id) ON DELETE CASCADE,
    goals_scored INT DEFAULT 0 CHECK (goals_scored>=0),
    UNIQUE (match_id, player_id) -- constraint
);  