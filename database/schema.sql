-- Venue Table
CREATE TABLE Venues
(
    venue_id SERIAL PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL
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

-- Matches Table
CREATE TABLE Matches
(
    match_id SERIAL PRIMARY KEY,
    home_team_id INT REFERENCES Teams(team_id) ON DELETE CASCADE,
    away_team_id INT REFERENCES Teams(team_id) ON DELETE CASCADE,
    venue_id INT REFERENCES Venues(venue_id) ON DELETE SET NULL,
    match_status VARCHAR(20) DEFAULT 'Scheduled' CHECK (match_status IN ('Scheduled', 'In Progress', 'Completed', 'Cancelled')),
    match_date TIMESTAMP NOT NULL,
    home_score INT DEFAULT 0 CHECK (home_score >= 0),
    away_score INT DEFAULT 0 CHECK (away_score >= 0),
    CONSTRAINT check_different_teams CHECK (home_team_id != away_team_id)
);

-- Player Match Stats Table
CREATE TABLE Player_Match_Stats
(
    stat_id SERIAL PRIMARY KEY,
    match_id INT REFERENCES Matches(match_id) ON DELETE CASCADE,
    player_id INT REFERENCES Players(player_id) ON DELETE CASCADE,
    goals_scored INT DEFAULT 0 CHECK (goals_scored >= 0),
    UNIQUE (match_id, player_id)
);  

-- Users Table for Admin/Viewer roles
CREATE TABLE Users 
(
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Viewer' CHECK (role IN ('Admin', 'Viewer'))
);

--  Prevent direct score editing in Matches table
CREATE OR REPLACE FUNCTION enforce_derived_scores()
RETURNS TRIGGER AS $$
BEGIN
    NEW.home_score := COALESCE((SELECT SUM(pms.goals_scored) FROM Player_Match_Stats pms JOIN Players p ON pms.player_id = p.player_id WHERE pms.match_id = NEW.match_id AND p.team_id = NEW.home_team_id), 0);
    
    NEW.away_score := COALESCE((SELECT SUM(pms.goals_scored) FROM Player_Match_Stats pms JOIN Players p ON pms.player_id = p.player_id WHERE pms.match_id = NEW.match_id AND p.team_id = NEW.away_team_id), 0);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_derived_scores
BEFORE INSERT OR UPDATE ON Matches
FOR EACH ROW EXECUTE FUNCTION enforce_derived_scores();

--  Force Matches table to recalculate when Player_Match_Stats change
CREATE OR REPLACE FUNCTION sync_match_scores()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.match_id != NEW.match_id) THEN
        UPDATE Matches SET home_score = home_score WHERE match_id = OLD.match_id;
    END IF;

    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        UPDATE Matches SET home_score = home_score WHERE match_id = NEW.match_id;
    END IF;

    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_match_scores
AFTER INSERT OR UPDATE OR DELETE ON Player_Match_Stats
FOR EACH ROW EXECUTE FUNCTION sync_match_scores();

-- Validate player teams and block edits on Scheduled/Cancelled matches
CREATE OR REPLACE FUNCTION validate_goal_modification()
RETURNS TRIGGER AS $$
DECLARE
    v_match_status VARCHAR(20);
    v_home_team INT;
    v_away_team INT;
    v_player_team INT;
    v_match_id INT;
BEGIN
    v_match_id := COALESCE(NEW.match_id, OLD.match_id);

    SELECT match_status, home_team_id, away_team_id 
    INTO v_match_status, v_home_team, v_away_team
    FROM Matches WHERE match_id = v_match_id;

    IF v_match_status IN ('Scheduled', 'Cancelled') THEN
        RAISE EXCEPTION 'Cannot modify goals for % matches.', v_match_status;
    END IF;

    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        SELECT team_id INTO v_player_team FROM Players WHERE player_id = NEW.player_id;
        IF v_player_team != v_home_team AND v_player_team != v_away_team THEN
            RAISE EXCEPTION 'Player does not belong to either team in this match.';
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_goal_modification
BEFORE INSERT OR UPDATE OR DELETE ON Player_Match_Stats
FOR EACH ROW EXECUTE FUNCTION validate_goal_modification();