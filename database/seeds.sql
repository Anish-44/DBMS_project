-- Insert Venues
INSERT INTO Venues (venue_name, address) VALUES
('Campus Main Arena', 'North Campus Athletic Complex'),
('Student Turf Field', 'East Campus Quad'),
('Indoor Sports Center', 'South Campus Gym');

-- Insert Teams
INSERT INTO Teams (team_name, coach_name) VALUES
('Thunderbolts', 'Coach Sarah'),
('Vipers', 'Coach Mike'),
('Strikers', 'Coach Elena'),
('Phoenix', 'Coach David');

-- Insert Players
-- Team 1: Thunderbolts, Team 2: Vipers,
-- Team 3: Strikers, Team 4: Phoenix
INSERT INTO Players (team_id, first_name, last_name, jersey_number) VALUES
-- Thunderbolts
(1, 'Alex', 'Rios', 10),
(1, 'Marcus', 'Vance', 7),
(1, 'Leo', 'Chen', 9),

-- Vipers
(2, 'Jordan', 'Smith', 10),
(2, 'Sam', 'Taylor', 11),
(2, 'Chris', 'Evans', 4),

-- Strikers
(3, 'Daniel', 'Kim', 9),
(3, 'Lucas', 'Silva', 8),

-- Phoenix
(4, 'Ethan', 'Wright', 7);

-- Insert Matches
INSERT INTO Matches (
    home_team_id,
    away_team_id,
    venue_id,
    match_status,
    match_date
) VALUES
(1, 2, 1, 'Completed', '2026-10-15 16:00:00'),
(3, 4, 2, 'Completed', '2026-10-16 17:30:00'),
(2, 3, 3, 'Completed', '2026-10-20 18:00:00');

-- Insert Player Match Stats
-- Match 1: Thunderbolts vs Vipers (3 - 1)
INSERT INTO Player_Match_Stats (
    match_id, player_id, goals_scored
) VALUES
(1, 1, 2), -- Alex Rios scored 2
(1, 2, 1), -- Marcus Vance scored 1
(1, 4, 1); -- Jordan Smith scored 1

-- Match 2: Strikers vs Phoenix (2 - 2)
INSERT INTO Player_Match_Stats (
    match_id, player_id, goals_scored
) VALUES
(2, 7, 2), -- Daniel Kim scored 2
(2, 9, 2); -- Ethan Wright scored 2

-- Match 3: Vipers vs Strikers (0 - 2)
INSERT INTO Player_Match_Stats (
    match_id, player_id, goals_scored
) VALUES
(3, 7, 1), -- Daniel Kim scored 1
(3, 8, 1); -- Lucas Silva scored 1