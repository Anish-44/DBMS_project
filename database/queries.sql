--Top Scorer Leaderboard Query
SELECT p.player_id, p.first_name || ' ' || p.last_name AS player_name,
t.team_name, SUM(pms.goals_scored) AS total_goals
FROM Players p JOIN Teams t on p.team_id=t.team_id
JOIN Player_Match_Stats pms ON p.player_id=pms.player_id
GROUP BY p.player_id, p.first_name, p.last_name, t.team_name
HAVING SUM(pms.goals_scored)>0
ORDER BY total_goals DESC;

--Match Schedule & Scores Overview Query
SELECT m.match_id, ht.team_name AS home_team, awt.team_name AS away_team,
m.home_score|| '-' || m.away_score AS score, v.venue_name, m.match_date
FROM Matches m JOIN Teams ht ON m.home_team_id=ht.team_id
JOIN Teams awt ON m.away_team_id=awt.team_id
JOIN Venues v ON m.venue_id=v.venue_id
ORDER BY m.match_date DESC;

--Dynamic League Standings Query
WITH TeamMatches AS
(
    SELECT home_team_id AS team_id, home_score AS score_for, away_score AS score_against
    FROM Matches
    UNION ALL
    SELECT away_team_id AS team_id, away_score AS score_for, home_score AS score_against
    FROM Matches
)
SELECT t.team_name, COUNT(tm.team_id) AS matches_played,
SUM(CASE WHEN tm.score_for>tm.score_against THEN 1 ELSE 0 END) AS wins,
SUM(CASE WHEN tm.score_for=tm.score_against THEN 1 ELSE 0 END) AS draws,
SUM(CASE WHEN tm.score_for<tm.score_against THEN 1 ELSE 0 END) AS losses,
SUM(CASE WHEN tm.score_for>tm.score_against THEN 3 WHEN tm.score_for=tm.score_against 
THEN 1 ELSE 0 END) AS total_points
FROM Teams t
LEFT JOIN TeamMatches tm ON t.team_id=tm.team_id
GROUP BY t.team_id, t.team_name
ORDER BY total_points DESC, wins DESC;   

-- Display all team ids, names and coach names
SELECT team_id, team_name, coach_name FROM Teams ORDER BY team_id;

--Display all venue ids, names and addresses
SELECT venue_id, venue_name, address FROM Venues ORDER BY venue_id;

--Display all matches
SELECT
m.match_id, ht.team_name AS home_team, awt.team_name AS away_team,
v.venue_name, m.match_date, m.home_score || '-' || m.away_score AS score,
m.match_status FROM matches m
JOIN Teams ht ON m.home_team_id=ht.team_id
JOIN Teams awt ON m.away_team_id=awt.team_id
JOIN Venues v ON m.venue_id=v.venue_id
ORDER BY m.match_date DESC;

--Display Matches
--Keep match status as a variable in UI
SELECT * FROM Matches WHERE match_status='Completed';

--Player match statistics for a specific completed match
--Replace 1 with a variable in the UI

SELECT p.first_name || ' ' || p.last_name AS player_name, t.team_name,
pms.goals_scored FROM Player_Match_Stats pms
JOIN Players p ON pms.player_id=p.player_id
JOIN Teams t ON p.team_id=t.team_id
WHERE pms.match_id=1
ORDER BY pms.goals_scored DESC;

--For the below queries, replace hardcoded names with placeholders in UI

--Add a new team
INSERT INTO Teams(team_name, coach_name) VALUES ('Warriors', 'Coach Dan');

--Add a player to a team
--Add a dropdown of teams to supply the team_id
INSERT INTO Players(team_id, first_name, last_name, jersey_number)
VALUES (5, 'John', 'Doe', 99);

--Add a new match
INSERT INTO Matches(home_team_id, away_team_id, venue_id, match_data, match_status)
VALUES (1,3,2, '2026-11-10 18:00:00', 'Scheduled');