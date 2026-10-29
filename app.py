import os

from datetime import datetime
from functools import wraps



from dotenv import load_dotenv

from flask import (

    Flask, render_template_string, request,

    redirect, url_for, flash, session

)



from db import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash



load_dotenv()



app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")



if not app.secret_key:

    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")





HTML = """

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{{ title }} | ISMS</title>

    <link rel="stylesheet"

          href="{{ url_for('static', filename='css/style.css') }}">

    <style>

        nav a.active {

            color: #24518a;

            border-bottom: 3px solid #24518a;

            padding-bottom: 5px;

        }

        .message {

            background: #e8f5e9;

            padding: 12px 16px;

            border-radius: 6px;

            margin-bottom: 16px;

        }

        .score {

            width: 100px;

        }

        .form-row {

            margin-bottom: 18px;

        }

        .form-row label {

            display: inline-block;

            margin-bottom: 6px;

        }

        .inline-edit-form { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 0; }
        .inline-edit-form input, .inline-edit-form select { box-sizing: border-box; width: 100%; min-width: 90px; max-width: 220px; }
        table { width: 100%; border-collapse: collapse; table-layout: auto; }
        th, td { vertical-align: top; text-align: left; padding: 10px 8px; }
        td form button { white-space: nowrap; }
        @media (max-width: 760px) { table { display: block; overflow-x: auto; white-space: nowrap; } }

    </style>

</head>

<body>

    <header>

        <h1>ISMS Dashboard</h1>

        <p>Intramural Sports Management System</p>

    </header>



    <nav>
        {% if current_role == 'Admin' %}<span>Admin: {{ current_username }}</span>{% else %}<span>Viewer mode</span>{% endif %}
        <form action="{{ url_for('logout') }}" method="POST" style="display:inline"><button type="submit">Logout</button></form>

        <a class="{{ 'active' if page == 'teams' else '' }}"

           href="{{ url_for('teams_page') }}">Teams</a>

        <a class="{{ 'active' if page == 'add_team' else '' }}"

           href="{{ url_for('add_team_page') }}">Add Team</a>

        <a class="{{ 'active' if page == 'players' else '' }}"

           href="{{ url_for('players_page') }}">Players</a>

        <a class="{{ 'active' if page == 'venues' else '' }}"

           href="{{ url_for('venues_page') }}">Venues</a>

        <a class="{{ 'active' if page == 'schedule' else '' }}"

           href="{{ url_for('schedule_page') }}">Schedule Match</a>

        <a class="{{ 'active' if page == 'matches' else '' }}"

           href="{{ url_for('matches_page') }}">Matches</a>

        <a class="{{ 'active' if page == 'scores' else '' }}"

           href="{{ url_for('scores_page') }}">Score Management</a>

        <a class="{{ 'active' if page == 'leaderboard' else '' }}"

           href="{{ url_for('leaderboard_page') }}">Points Table</a>

    </nav>



    <main>

        {% with messages = get_flashed_messages(with_categories=true) %}

            {% for category, message in messages %}

                <p class="message">{{ message }}</p>

            {% endfor %}

        {% endwith %}



        {% if page == 'teams' %}

        <section>

            <h2>Registered Teams</h2>

            <p>Total teams: {{ teams|length }}</p>

            <table>

                <thead><tr><th>ID</th><th>Team Name</th><th>Coach</th><th>Edit details</th></tr></thead>

                <tbody>

                {% for team in teams %}
                    <tr>
                        <td>{{ team[0] }}</td>
                        <td>
                            {% if current_role == 'Admin' %}
                                <form action="{{ url_for('update_team') }}" method="POST" class="inline-edit-form">
                                    <input type="hidden" name="team_id" value="{{ team[0] }}">
                                    <input name="team_name" aria-label="Team name" value="{{ team[1] }}" maxlength="100" required>
                                    <input type="hidden" name="coach_name" value="{{ team[2] }}">
                                    <button type="submit">Save Team Name</button>
                                </form>
                            {% else %}{{ team[1] }}{% endif %}
                        </td>
                        <td>
                            {% if current_role == 'Admin' %}
                                <form action="{{ url_for('update_team') }}" method="POST" class="inline-edit-form">
                                    <input type="hidden" name="team_id" value="{{ team[0] }}">
                                    <input type="hidden" name="team_name" value="{{ team[1] }}">
                                    <input name="coach_name" aria-label="Coach name" value="{{ team[2] }}" maxlength="100" required>
                                    <button type="submit">Save Coach</button>
                                </form>
                            {% else %}{{ team[2] }}{% endif %}
                        </td>
                        <td>{% if current_role == 'Admin' %}Edit using the fields in this row.{% else %}View only{% endif %}</td>
                    </tr>
                {% else %}
                    <tr><td colspan="4">No teams found.</td></tr>
                {% endfor %}

                </tbody>

            </table>

        </section>

        {% endif %}



        {% if page == 'add_team' %}

        <section>

            <h2>Add a Team</h2>

            {% if current_role == 'Admin' %}<form action="{{ url_for('add_team') }}" method="POST">

                <div class="form-row">

                    <label for="team_name">Team Name</label><br>

                    <input id="team_name" name="team_name" maxlength="100" required>

                </div>

                <div class="form-row">

                    <label for="coach_name">Coach Name</label><br>

                    <input id="coach_name" name="coach_name" maxlength="100" required>

                </div>

                <button type="submit">Save Team</button>

            </form>{% else %}<p>Viewer access is read-only.</p>{% endif %}

        </section>

        {% endif %}



        {% if page == 'players' %}

        <section>

            <h2>Register a Player</h2>

            {% if current_role == 'Admin' %}<form action="{{ url_for('add_player') }}" method="POST">

                <div class="form-row">

                    <label for="first_name">First Name</label><br>

                    <input id="first_name" name="first_name" maxlength="100" required>

                </div>

                <div class="form-row">

                    <label for="last_name">Last Name</label><br>

                    <input id="last_name" name="last_name" maxlength="100" required>

                </div>

                <div class="form-row">

                    <label for="jersey_number">Jersey Number</label><br>

                    <input id="jersey_number" name="jersey_number"

                           type="number" min="0" required>

                </div>

                <div class="form-row">

                    <label for="team_id">Team</label><br>

                    <select id="team_id" name="team_id" required>

                        <option value="">Select a team</option>

                        {% for team in team_options %}

                        <option value="{{ team[0] }}">{{ team[1] }}</option>

                        {% endfor %}

                    </select>

                </div>

                <button type="submit">Register Player</button>

            </form>{% else %}<p>Viewer access is read-only.</p>{% endif %}

        </section>



        <section>

            <h2>Registered Players</h2>

            <p>Total players: {{ players|length }}</p>

            <table>

                <thead><tr><th>ID</th><th>First name</th><th>Last name</th><th>Jersey</th><th>Team</th><th>Save</th></tr></thead>

                <tbody>
                {% for player in players %}
                    <tr>
                        <td>{{ player[0] }}</td>
                        <td>{% if current_role == 'Admin' %}<form action="{{ url_for('update_player') }}" method="POST" class="inline-edit-form"><input type="hidden" name="player_id" value="{{ player[0] }}"><input type="hidden" name="last_name" value="{{ player[2] }}"><input type="hidden" name="jersey_number" value="{{ player[3] }}"><input type="hidden" name="team_id" value="{% for team in team_options %}{% if team[1] == player[4] %}{{ team[0] }}{% endif %}{% endfor %}"><input name="first_name" aria-label="First name" value="{{ player[1] }}" maxlength="100" required><button type="submit">Save</button></form>{% else %}{{ player[1] }}{% endif %}</td>
                        <td>{% if current_role == 'Admin' %}<form action="{{ url_for('update_player') }}" method="POST" class="inline-edit-form"><input type="hidden" name="player_id" value="{{ player[0] }}"><input type="hidden" name="first_name" value="{{ player[1] }}"><input type="hidden" name="jersey_number" value="{{ player[3] }}"><input type="hidden" name="team_id" value="{% for team in team_options %}{% if team[1] == player[4] %}{{ team[0] }}{% endif %}{% endfor %}"><input name="last_name" aria-label="Last name" value="{{ player[2] }}" maxlength="100" required><button type="submit">Save</button></form>{% else %}{{ player[2] }}{% endif %}</td>
                        <td>{% if current_role == 'Admin' %}<form action="{{ url_for('update_player') }}" method="POST" class="inline-edit-form"><input type="hidden" name="player_id" value="{{ player[0] }}"><input type="hidden" name="first_name" value="{{ player[1] }}"><input type="hidden" name="last_name" value="{{ player[2] }}"><input type="hidden" name="team_id" value="{% for team in team_options %}{% if team[1] == player[4] %}{{ team[0] }}{% endif %}{% endfor %}"><input name="jersey_number" aria-label="Jersey number" type="number" min="0" value="{{ player[3] }}" required><button type="submit">Save</button></form>{% else %}{{ player[3] }}{% endif %}</td>
                        <td>{% if current_role == 'Admin' %}<form action="{{ url_for('update_player') }}" method="POST" class="inline-edit-form"><input type="hidden" name="player_id" value="{{ player[0] }}"><input type="hidden" name="first_name" value="{{ player[1] }}"><input type="hidden" name="last_name" value="{{ player[2] }}"><input type="hidden" name="jersey_number" value="{{ player[3] }}"><select name="team_id" aria-label="Team" required>{% for team in team_options %}<option value="{{ team[0] }}" {% if team[1] == player[4] %}selected{% endif %}>{{ team[1] }}</option>{% endfor %}</select><button type="submit">Save</button></form>{% else %}{{ player[4] }}{% endif %}</td>
                        <td>{% if current_role == 'Admin' %}Edit using the fields in this row.{% else %}View only{% endif %}</td>
                    </tr>
                {% else %}
                    <tr><td colspan="6">No players registered yet.</td></tr>
                {% endfor %}
                </tbody>

            </table>

        </section>

        {% endif %}



        {% if page == 'venues' %}

        <section>

            <h2>Add a Venue</h2>
            {% if current_role == 'Admin' %}<form action="{{ url_for('add_venue') }}" method="POST">
                <div class="form-row">
                    <label for="venue_name">Venue Name</label><br>
                    <input id="venue_name" name="venue_name" maxlength="150" required>
                </div>
                <div class="form-row">
                    <label for="address">Address</label><br>
                    <input id="address" name="address" maxlength="255" required>
                </div>
                <button type="submit">Add Venue</button>
            </form>{% else %}<p>Viewer access is read-only.</p>{% endif %}
        </section>

        <section>

            <h2>Sports Venues</h2>

            <p>Total venues: {{ venues|length }}</p>

            <table>

                <thead><tr><th>ID</th><th>Venue Name</th><th>Address</th></tr></thead>

                <tbody>

                {% for venue in venues %}

                    <tr><td>{{ venue[0] }}</td><td>{{ venue[1] }}</td><td>{{ venue[2] }}</td></tr>

                {% else %}

                    <tr><td colspan="3">No venues found.</td></tr>

                {% endfor %}

                </tbody>

            </table>

        </section>

        {% endif %}



        {% if page == 'schedule' %}

        <section>

            <h2>Schedule a Match</h2>

            {% if team_options|length < 2 %}

                <p>You need at least two teams to schedule a match.</p>

            {% elif current_role != 'Admin' %}
                <p>You are viewing this page as a Viewer. You can view scheduled matches from the <strong>Matches</strong> page, but only an Admin can schedule a new match.</p>
            {% else %}
            <form action="{{ url_for('add_match') }}" method="POST">

                <div class="form-row">

                    <label for="home_team_id">Home Team</label><br>

                    <select id="home_team_id" name="home_team_id" required>

                        <option value="">Select home team</option>

                        {% for team in team_options %}

                        <option value="{{ team[0] }}">{{ team[1] }}</option>

                        {% endfor %}

                    </select>

                </div>

                <div class="form-row">

                    <label for="away_team_id">Away Team</label><br>

                    <select id="away_team_id" name="away_team_id" required>

                        <option value="">Select away team</option>

                        {% for team in team_options %}

                        <option value="{{ team[0] }}">{{ team[1] }}</option>

                        {% endfor %}

                    </select>

                </div>

                <div class="form-row">

                    <label for="venue_id">Venue</label><br>

                    <select id="venue_id" name="venue_id">

                        <option value="">No venue selected</option>

                        {% for venue in venue_options %}

                        <option value="{{ venue[0] }}">{{ venue[1] }}</option>

                        {% endfor %}

                    </select>

                </div>

                <div class="form-row">

                    <label for="match_date">Match Date and Time</label><br>

                    <input id="match_date" name="match_date"

                           type="datetime-local" required>

                </div>

                <button type="submit">Schedule Match</button>

            </form>

            {% endif %}

        </section>

        {% endif %}



        {% if page == 'matches' %}
        <section>
            <h2>Match Results and Status</h2>
            <p>Total matches: {{ matches|length }}</p>
            <p>Scores are calculated automatically from player goals. Mark a match as Completed when it has finished so its result can be counted.</p>
            <table>
                <thead>
                    <tr><th>ID</th><th>Home Team</th><th>Score</th><th>Away Team</th><th>Venue</th><th>Date and Time</th><th>Status</th><th>Result</th><th>Update Status</th></tr>
                </thead>
                <tbody>
                {% for match in matches %}
                    <tr>
                        <td>{{ match[0] }}</td>
                        <td>{{ match[1] }}</td>
                        <td>{{ match[2] }} - {{ match[3] }}</td>
                        <td>{{ match[4] }}</td>
                        <td>{{ match[5] or 'Not assigned' }}</td>
                        <td>{{ match[6] }}</td>
                        <td>{{ match[7] }}</td>
                        <td>
                            {% if match[7] == 'Completed' %}
                                {% if match[2] > match[3] %}{{ match[1] }} won
                                {% elif match[2] < match[3] %}{{ match[4] }} won
                                {% else %}Draw{% endif %}
                            {% elif match[7] == 'Cancelled' %}
                                Cancelled
                            {% else %}
                                Not decided
                            {% endif %}
                        </td>
                        <td>
                            {% if current_role == 'Admin' %}<form action="{{ url_for('update_match_status') }}" method="POST">
                                <input type="hidden" name="match_id" value="{{ match[0] }}">
                                <select name="match_status" aria-label="Status for match {{ match[0] }}"
                                        onchange="if ('{{ match[7] }}' === 'Completed' && this.value === 'In Progress') { if (!confirm('Reopen this completed match for score corrections?')) this.value = 'Completed'; }">
                                    {% for option in ['Scheduled', 'In Progress', 'Completed', 'Cancelled'] %}
                                    <option value="{{ option }}" {% if match[7] == option %}selected{% endif %}>{{ option }}</option>
                                    {% endfor %}
                                </select>
                                <button type="submit">Save</button>
                            </form>{% else %}Read-only{% endif %}
                        </td>
                    </tr>
                {% else %}
                    <tr><td colspan="9">No matches scheduled yet.</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </section>
        {% endif %}



        {% if page == 'scores' %}

        <section>
            <h2>Match Scores</h2>
            <p>Team scores are calculated automatically from recorded player goals.</p>
            {% if score_matches %}
            <table>
                <thead><tr><th>Match</th><th>Home Team</th><th>Score</th><th>Away Team</th><th>Date and Time</th><th>Status</th></tr></thead>
                <tbody>
                {% for match in score_matches %}
                    <tr>
                        <td>{{ match[0] }}</td>
                        <td>{{ match[1] }}</td>
                        <td>{{ match[2] }} - {{ match[3] }}</td>
                        <td>{{ match[4] }}</td>
                        <td>{{ match[6] }}</td>
                        <td>{{ match[7] }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
            {% else %}
                <p>No matches scheduled. Schedule a match first.</p>
            {% endif %}
        </section>



        <section>

            <h2>Record Player Goals</h2>
            {% if current_role == 'Admin' %}

            {% if goal_matches %}

            <form action="{{ url_for('save_player_goals') }}" method="POST">

                <div class="form-row">

                    <label for="stats_match_id">Match</label><br>

                    <select id="stats_match_id" name="match_id" required>

                        <option value="">Select a match</option>

                        {% for match in goal_matches %}
                        <option value="{{ match[0] }}"
                                data-home-team="{{ match[8] }}"
                                data-away-team="{{ match[9] }}">
                            {{ match[1] }} vs {{ match[4] }} (Match {{ match[0] }})
                        </option>
                        {% endfor %}

                    </select>

                </div>

                <div class="form-row">

                    <label for="player_id">Player</label><br>

                    <select id="player_id" name="player_id" required>

                        <option value="">Select a player</option>

                        {% for player in all_players %}

                        <option value="{{ player[0] }}" data-team-id="{{ player[4] }}">

                            {{ player[1] }} {{ player[2] }} — {{ player[3] }}

                        </option>

                        {% endfor %}

                    </select>

                    <p><small>Goals can only be recorded while a match is In Progress. The server verifies the match status and that the player belongs to one of its teams.</small></p>

                </div>

                <div class="form-row">

                    <label for="goals_scored">Total goals by this player in the match</label><br>

                    <input id="goals_scored" name="goals_scored"

                           type="number" min="0" value="0" required>

                </div>

                <button type="submit">Save Player Goals</button>

            </form>

            {% else %}
                <p>No matches are currently In Progress. On the Matches page, change a match to In Progress before recording goals.</p>
            {% endif %}

            {% else %}<p>Viewer access is read-only. You can view the score and player statistics above and below.</p>{% endif %}
        </section>



        <section>

            <h2>Player Match Statistics</h2>

            <table>

                <thead>

                    <tr><th>Match</th><th>Player</th><th>Team</th><th>Goals</th></tr>

                </thead>

                <tbody>

                {% for stat in player_stats %}

                    <tr>

                        <td>{{ stat[0] }}: {{ stat[1] }} vs {{ stat[2] }}</td>

                        <td>{{ stat[3] }}</td>

                        <td>{{ stat[4] }}</td>

                        <td>{{ stat[5] }}</td>

                    </tr>

                {% else %}

                    <tr><td colspan="4">No player statistics recorded yet.</td></tr>

                {% endfor %}

                </tbody>

            </table>

        </section>

        {% endif %}

        {% if page == 'leaderboard' %}
        <section>
            <h2>Points Table / Leaderboard</h2>
            <p>Only completed matches count. A win earns 3 points, a draw earns 1 point, and a loss earns 0 points.</p>
            <table>
                <thead><tr><th>Rank</th><th>Team</th><th>Played</th><th>Won</th><th>Drawn</th><th>Lost</th><th>Goals For</th><th>Goals Against</th><th>Goal Difference</th><th>Points</th></tr></thead>
                <tbody>
                {% for team in leaderboard %}
                    <tr><td>{{ loop.index }}</td><td>{{ team[1] }}</td><td>{{ team[2] }}</td><td>{{ team[3] }}</td><td>{{ team[4] }}</td><td>{{ team[5] }}</td><td>{{ team[6] }}</td><td>{{ team[7] }}</td><td>{{ team[8] }}</td><td><strong>{{ team[9] }}</strong></td></tr>
                {% else %}
                    <tr><td colspan="10">No teams registered yet.</td></tr>
                {% endfor %}
                </tbody>
            </table>
            {% if completed_match_count == 0 %}
                <p>No completed matches yet. Set a finished match to <strong>Completed</strong> on the Matches page to calculate the table.</p>
            {% endif %}
        </section>

        <section>
            <h2>Top Scorers — Player Rankings</h2>
            <p>Players are ranked by their total recorded goals. Players tied on goals share the same rank.</p>
            <table>
                <thead><tr><th>Rank</th><th>Player</th><th>Team</th><th>Total Goals</th></tr></thead>
                <tbody>
                {% for player in player_leaderboard %}
                    <tr><td>{{ player[0] }}</td><td>{{ player[1] }}</td><td>{{ player[2] }}</td><td><strong>{{ player[3] }}</strong></td></tr>
                {% else %}
                    <tr><td colspan="4">No players registered yet.</td></tr>
                {% endfor %}
                </tbody>
            </table>
            {% if player_leaderboard and player_leaderboard|sum(attribute=3) == 0 %}
                <p>No goals have been recorded yet. Player rankings will update when goals are saved on the Score Management page.</p>
            {% endif %}
        </section>
        {% endif %}

    </main>



    <footer>ISMS | College Sports Management</footer>

    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const matchSelect = document.getElementById("stats_match_id");
            const playerSelect = document.getElementById("player_id");

            // These controls exist only on the Score Management page.
            if (!matchSelect || !playerSelect) return;

            function filterPlayersForMatch() {
                const selectedMatch = matchSelect.options[matchSelect.selectedIndex];
                const homeTeam = selectedMatch ? selectedMatch.dataset.homeTeam : "";
                const awayTeam = selectedMatch ? selectedMatch.dataset.awayTeam : "";

                playerSelect.value = "";

                for (const option of playerSelect.options) {
                    if (!option.value) {
                        option.hidden = false;
                        continue;
                    }
                    const teamId = option.dataset.teamId;
                    option.hidden = !homeTeam || !awayTeam ||
                        (teamId !== homeTeam && teamId !== awayTeam);
                }
            }

            matchSelect.addEventListener("change", filterPlayersForMatch);
            filterPlayersForMatch();
        });
    </script>

</body>

</html>

"""





def render_page(page, title):

    data = {

        "page": page,

        "title": title,

        "teams": [],

        "team_options": [],

        "players": [],

        "venues": [],

        "venue_options": [],

        "matches": [],

        "score_matches": [],

        "all_players": [],

        "player_stats": [],
        "leaderboard": [],
        "completed_match_count": 0,
        "current_role": session.get("role"),
        "current_username": session.get("username")

    }



    with get_db_connection() as conn:

        if page == "teams":

            data["teams"] = conn.execute(

                """

                SELECT team_id, team_name, coach_name

                FROM teams ORDER BY team_name

                """

            ).fetchall()



        elif page == "players":

            data["team_options"] = conn.execute(

                "SELECT team_id, team_name FROM teams ORDER BY team_name"

            ).fetchall()



            data["players"] = conn.execute(

                """

                SELECT p.player_id, p.first_name, p.last_name,

                       p.jersey_number, t.team_name

                FROM players p

                JOIN teams t ON p.team_id = t.team_id

                ORDER BY t.team_name, p.jersey_number

                """

            ).fetchall()



        elif page == "venues":

            data["venues"] = conn.execute(

                """

                SELECT venue_id, venue_name, address

                FROM venues ORDER BY venue_name

                """

            ).fetchall()



        elif page == "schedule":

            data["team_options"] = conn.execute(

                "SELECT team_id, team_name FROM teams ORDER BY team_name"

            ).fetchall()



            data["venue_options"] = conn.execute(

                "SELECT venue_id, venue_name FROM venues ORDER BY venue_name"

            ).fetchall()



        elif page == "matches":

            data["matches"] = conn.execute(

                """

                SELECT m.match_id, ht.team_name, m.home_score,

                       m.away_score, at.team_name, v.venue_name,

                       TO_CHAR(m.match_date, 'YYYY-MM-DD HH24:MI'),

                       m.match_status

                FROM matches m

                JOIN teams ht ON m.home_team_id = ht.team_id

                JOIN teams at ON m.away_team_id = at.team_id

                LEFT JOIN venues v ON m.venue_id = v.venue_id

                ORDER BY m.match_date, m.match_id

                """

            ).fetchall()



        elif page == "scores":

            data["score_matches"] = conn.execute(

                """

                SELECT m.match_id, ht.team_name, m.home_score,

                       m.away_score, at.team_name, v.venue_name,

                       TO_CHAR(m.match_date, 'YYYY-MM-DD HH24:MI'),

                       m.match_status, m.home_team_id, m.away_team_id

                FROM matches m

                JOIN teams ht ON m.home_team_id = ht.team_id

                JOIN teams at ON m.away_team_id = at.team_id

                LEFT JOIN venues v ON m.venue_id = v.venue_id

                ORDER BY m.match_date, m.match_id

                """

            ).fetchall()

            data["goal_matches"] = [
                match for match in data["score_matches"]
                if match[7] == "In Progress"
            ]

            data["all_players"] = conn.execute(

                """

                SELECT p.player_id, p.first_name, p.last_name,

                       t.team_name, p.team_id

                FROM players p

                JOIN teams t ON p.team_id = t.team_id

                ORDER BY t.team_name, p.last_name, p.first_name

                """

            ).fetchall()



            data["player_stats"] = conn.execute(

                """

                SELECT s.match_id, ht.team_name, at.team_name,

                       p.first_name || ' ' || p.last_name,

                       t.team_name, s.goals_scored

                FROM player_match_stats s

                JOIN matches m ON s.match_id = m.match_id

                JOIN teams ht ON m.home_team_id = ht.team_id

                JOIN teams at ON m.away_team_id = at.team_id

                JOIN players p ON s.player_id = p.player_id

                JOIN teams t ON p.team_id = t.team_id

                ORDER BY s.match_id, t.team_name, p.last_name

                """

            ).fetchall()



        elif page == "leaderboard":
            teams = conn.execute(
                "SELECT team_id, team_name FROM teams ORDER BY team_name"
            ).fetchall()
            standings = {
                team[0]: {
                    "team_id": team[0], "team_name": team[1],
                    "played": 0, "won": 0, "drawn": 0, "lost": 0,
                    "goals_for": 0, "goals_against": 0, "points": 0
                }
                for team in teams
            }
            completed_matches = conn.execute(
                """
                SELECT home_team_id, away_team_id, home_score, away_score
                FROM matches
                WHERE match_status = 'Completed'
                """
            ).fetchall()
            data["completed_match_count"] = len(completed_matches)

            for home_id, away_id, home_score, away_score in completed_matches:
                if home_id not in standings or away_id not in standings:
                    continue
                home = standings[home_id]
                away = standings[away_id]
                home_score = home_score or 0
                away_score = away_score or 0
                home["played"] += 1
                away["played"] += 1
                home["goals_for"] += home_score
                home["goals_against"] += away_score
                away["goals_for"] += away_score
                away["goals_against"] += home_score
                if home_score > away_score:
                    home["won"] += 1
                    away["lost"] += 1
                    home["points"] += 3
                elif home_score < away_score:
                    away["won"] += 1
                    home["lost"] += 1
                    away["points"] += 3
                else:
                    home["drawn"] += 1
                    away["drawn"] += 1
                    home["points"] += 1
                    away["points"] += 1

            sorted_standings = sorted(
                standings.values(),
                key=lambda team: (
                    -team["points"],
                    -(team["goals_for"] - team["goals_against"]),
                    -team["goals_for"], team["team_name"].lower()
                )
            )
            data["leaderboard"] = [
                (team["team_id"], team["team_name"], team["played"],
                 team["won"], team["drawn"], team["lost"],
                 team["goals_for"], team["goals_against"],
                 team["goals_for"] - team["goals_against"], team["points"])
                for team in sorted_standings
            ]
            data["player_leaderboard"] = conn.execute(
                """
                SELECT RANK() OVER (ORDER BY COALESCE(SUM(s.goals_scored), 0) DESC) AS player_rank,
                       p.first_name || ' ' || p.last_name AS player_name,
                       t.team_name,
                       COALESCE(SUM(s.goals_scored), 0) AS total_goals
                FROM players p
                JOIN teams t ON t.team_id = p.team_id
                LEFT JOIN player_match_stats s ON s.player_id = p.player_id
                GROUP BY p.player_id, p.first_name, p.last_name, t.team_name
                ORDER BY total_goals DESC, player_name ASC
                """
            ).fetchall()

    return render_template_string(HTML, **data)





LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} | ISMS</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <style>
    body { font-family: Arial, sans-serif; }
    .auth-wrap { max-width: 440px; margin: 35px auto; padding: 24px; border: 1px solid #ddd; border-radius: 12px; }
    .auth-wrap form { margin: 18px 0; }
    .auth-wrap input { box-sizing: border-box; width: 100%; padding: 10px; margin: 6px 0 14px; }
    .auth-wrap button { padding: 10px 14px; cursor: pointer; }
    .message { background: #e8f5e9; padding: 12px 16px; border-radius: 6px; }
    .viewer-button { width: 100%; }
  </style>
</head>
<body>
<header><h1>ISMS</h1><p>Intramural Sports Management System</p></header>
<main class="auth-wrap">
  {% with messages = get_flashed_messages(with_categories=true) %}{% for category, message in messages %}<p class="message">{{ message }}</p>{% endfor %}{% endwith %}
  {% if mode == 'login' %}
    <h2>Continue as Viewer</h2>
    <p>View teams, players, venues, matches, scores, and the points table without an account.</p>
    <form action="{{ url_for('viewer_access') }}" method="POST"><button class="viewer-button" type="submit">Continue as Viewer</button></form>
    <hr>
    <h2>Admin Login</h2>
    <form action="{{ url_for('admin_login') }}" method="POST">
      <label for="username">Username</label><input id="username" name="username" autocomplete="username" maxlength="100" required>
      <label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required>
      <button type="submit">Log in as Admin</button>
    </form>
    <p><small>Default demo login: <strong>admin</strong> / <strong>Admin@ISMS2026</strong></small></p>
  {% endif %}
</main>
</body></html>
"""


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if session.get("role") not in ("Admin", "Viewer"):
            flash("Choose Viewer access or log in as Admin to continue.")
            return redirect(url_for("login_page"))
        return view_function(*args, **kwargs)
    return wrapped_view


def admin_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "Admin":
            flash("Admin access is required to make changes.")
            return redirect(url_for("login_page"))
        return view_function(*args, **kwargs)
    return wrapped_view


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@ISMS2026"


def ensure_default_admin():
    """Create the documented demo admin account if its username is unused."""
    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE LOWER(username) = LOWER(%s) LIMIT 1",
            (DEFAULT_ADMIN_USERNAME,)
        ).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'Admin')",
                (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD))
            )


@app.route("/login")
def login_page():
    if session.get("role") in ("Admin", "Viewer"):
        return redirect(url_for("teams_page"))
    try:
        ensure_default_admin()
    except Exception:
        app.logger.exception("Could not ensure default admin account")
        flash("Could not prepare the default admin account. Check your database settings and Users table.")
    return render_template_string(LOGIN_HTML, title="Login", mode="login")


@app.route("/viewer", methods=["POST"])
def viewer_access():
    session.clear()
    session["role"] = "Viewer"
    session["username"] = "Viewer"
    flash("You are viewing ISMS in read-only mode.")
    return redirect(url_for("teams_page"))


@app.route("/admin-login", methods=["POST"])
def admin_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        flash("Enter your admin username and password.")
        return redirect(url_for("login_page"))
    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT user_id, username, password_hash, role FROM users WHERE LOWER(username) = LOWER(%s) AND LOWER(role) = 'admin'",
                (username,)
            ).fetchone()
        if user and check_password_hash(user[2], password):
            session.clear()
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = "Admin"
            flash("Admin login successful.")
            return redirect(url_for("teams_page"))
        flash("Invalid admin username or password.")
    except Exception:
        app.logger.exception("Admin login failed")
        flash("Could not log in. Check the Users table and database connection.")
    return redirect(url_for("login_page"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login_page"))


@app.route("/")

def home():

    if session.get("role") not in ("Admin", "Viewer"):
        return redirect(url_for("login_page"))
    return redirect(url_for("teams_page"))





@app.route("/teams")

@login_required

def teams_page():

    return render_page("teams", "Teams")





@app.route("/teams/new")

@login_required

def add_team_page():

    return render_page("add_team", "Add Team")





@app.route("/players")

@login_required

def players_page():

    return render_page("players", "Players")





@app.route("/venues")

@login_required

def venues_page():

    return render_page("venues", "Venues")





@app.route("/matches/schedule")

@login_required

def schedule_page():

    return render_page("schedule", "Schedule Match")





@app.route("/matches")

@login_required

def matches_page():

    return render_page("matches", "Matches")





@app.route("/scores")

@login_required

def scores_page():

    return render_page("scores", "Score Management")


@app.route("/leaderboard")
@login_required
def leaderboard_page():
    return render_page("leaderboard", "Points Table")





@app.route("/venues/add", methods=["POST"])
@admin_required
def add_venue():
    venue_name = request.form.get("venue_name", "").strip()
    address = request.form.get("address", "").strip()
    if not venue_name or not address:
        flash("Enter both the venue name and address.")
        return redirect(url_for("venues_page"))
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO venues (venue_name, address) VALUES (%s, %s)",
                (venue_name, address)
            )
        flash("Venue added successfully!")
    except Exception:
        app.logger.exception("Could not add venue")
        flash("Could not add venue. Check the details and whether the venue already exists.")
    return redirect(url_for("venues_page"))


@app.route("/teams/update", methods=["POST"])
@admin_required
def update_team():
    team_text = request.form.get("team_id", "").strip()
    team_name = request.form.get("team_name", "").strip()
    coach_name = request.form.get("coach_name", "").strip()
    if not team_name or not coach_name:
        flash("Enter both the team name and coach name.")
        return redirect(url_for("teams_page"))
    try:
        team_id = int(team_text)
        with get_db_connection() as conn:
            result = conn.execute(
                "UPDATE teams SET team_name = %s, coach_name = %s WHERE team_id = %s",
                (team_name, coach_name, team_id)
            )
            if result.rowcount == 0:
                flash("Team not found.")
            else:
                flash("Team details updated successfully!")
    except Exception:
        app.logger.exception("Could not update team")
        flash("Could not update team. The team name may already exist.")
    return redirect(url_for("teams_page"))


@app.route("/players/update", methods=["POST"])
@admin_required
def update_player():
    player_text = request.form.get("player_id", "").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    jersey_text = request.form.get("jersey_number", "").strip()
    team_text = request.form.get("team_id", "").strip()
    if not first_name or not last_name:
        flash("Enter the player's first and last name.")
        return redirect(url_for("players_page"))
    try:
        player_id = int(player_text)
        jersey_number = int(jersey_text)
        team_id = int(team_text)
        if jersey_number < 0:
            raise ValueError
        with get_db_connection() as conn:
            result = conn.execute(
                "UPDATE players SET first_name = %s, last_name = %s, jersey_number = %s, team_id = %s WHERE player_id = %s",
                (first_name, last_name, jersey_number, team_id, player_id)
            )
            if result.rowcount == 0:
                flash("Player not found.")
            else:
                flash("Player details updated successfully!")
    except ValueError:
        flash("Enter a valid jersey number and select a team.")
    except Exception:
        app.logger.exception("Could not update player")
        flash("Could not update player. Check the team and jersey number.")
    return redirect(url_for("players_page"))


@app.route("/teams/add", methods=["POST"])

@admin_required

def add_team():

    team_name = request.form.get("team_name", "").strip()

    coach_name = request.form.get("coach_name", "").strip()



    if not team_name or not coach_name:

        flash("Enter both the team name and coach name.")

        return redirect(url_for("add_team_page"))



    try:

        with get_db_connection() as conn:

            conn.execute(

                """

                INSERT INTO teams (team_name, coach_name)

                VALUES (%s, %s)

                """,

                (team_name, coach_name)

            )

        flash("Team added successfully!")

    except Exception:

        app.logger.exception("Could not add team")

        flash("Could not add team. The team name may already exist.")



    return redirect(url_for("add_team_page"))





@app.route("/players/add", methods=["POST"])

@admin_required

def add_player():

    first_name = request.form.get("first_name", "").strip()

    last_name = request.form.get("last_name", "").strip()

    jersey_text = request.form.get("jersey_number", "").strip()

    team_text = request.form.get("team_id", "").strip()



    if not first_name or not last_name:

        flash("Enter the player's first and last name.")

        return redirect(url_for("players_page"))



    try:

        jersey_number = int(jersey_text)

        team_id = int(team_text)



        if jersey_number < 0:

            raise ValueError



        with get_db_connection() as conn:

            conn.execute(

                """

                INSERT INTO players

                    (team_id, first_name, last_name, jersey_number)

                VALUES (%s, %s, %s, %s)

                """,

                (team_id, first_name, last_name, jersey_number)

            )

        flash("Player registered successfully!")

    except ValueError:

        flash("Enter a valid jersey number and select a team.")

    except Exception:

        app.logger.exception("Could not register player")

        flash("Could not register player. Check the team and jersey number.")



    return redirect(url_for("players_page"))





@app.route("/matches/add", methods=["POST"])

@admin_required

def add_match():

    home_text = request.form.get("home_team_id", "").strip()

    away_text = request.form.get("away_team_id", "").strip()

    venue_text = request.form.get("venue_id", "").strip()

    date_text = request.form.get("match_date", "").strip()



    try:

        home_team_id = int(home_text)

        away_team_id = int(away_text)



        if home_team_id == away_team_id:

            flash("A team cannot play against itself.")

            return redirect(url_for("schedule_page"))



        match_date = datetime.fromisoformat(date_text)

        venue_id = int(venue_text) if venue_text else None



        with get_db_connection() as conn:

            conn.execute(

                """

                INSERT INTO matches

                    (home_team_id, away_team_id, venue_id, match_date)

                VALUES (%s, %s, %s, %s)

                """,

                (home_team_id, away_team_id, venue_id, match_date)

            )

        flash("Match scheduled successfully!")

    except ValueError:

        flash("Select both teams and enter a valid date and time.")

        return redirect(url_for("schedule_page"))

    except Exception:

        app.logger.exception("Could not schedule match")

        flash("Could not schedule match. Check the selected details.")



    return redirect(url_for("matches_page"))





@app.route("/matches/status", methods=["POST"])
@admin_required
def update_match_status():
    match_text = request.form.get("match_id", "").strip()
    match_status = request.form.get("match_status", "").strip()
    allowed_statuses = {"Scheduled", "In Progress", "Completed", "Cancelled"}

    try:
        match_id = int(match_text)
        if match_status not in allowed_statuses:
            flash("Choose a valid match status.")
            return redirect(url_for("matches_page"))

        with get_db_connection() as conn:
            result = conn.execute(
                "UPDATE matches SET match_status = %s WHERE match_id = %s",
                (match_status, match_id)
            )
            if result.rowcount == 0:
                flash("Match not found.")
                return redirect(url_for("matches_page"))

        flash("Match status updated successfully!")
    except ValueError:
        flash("Invalid match selected.")
    except Exception:
        app.logger.exception("Could not update match status")
        flash("Could not update match status. Confirm the database migration was run.")

    return redirect(url_for("matches_page"))


@app.route("/scores/player-goals", methods=["POST"])
@admin_required
def save_player_goals():

    match_text = request.form.get("match_id", "").strip()

    player_text = request.form.get("player_id", "").strip()

    goals_text = request.form.get("goals_scored", "").strip()



    try:

        match_id = int(match_text)

        player_id = int(player_text)

        goals = int(goals_text)



        if goals < 0:

            raise ValueError



        with get_db_connection() as conn:

            match = conn.execute(

                """

                SELECT home_team_id, away_team_id, match_status

                FROM matches

                WHERE match_id = %s

                """,

                (match_id,)

            ).fetchone()



            if match is None:
                flash("The selected match does not exist.")
                return redirect(url_for("scores_page"))

            if match[2] != "In Progress":
                if match[2] == "Completed":
                    flash("This match is completed and its score is locked. Reopen it to In Progress before correcting goals.")
                elif match[2] == "Cancelled":
                    flash("Goals cannot be recorded for a cancelled match. Change its status before resuming play.")
                else:
                    flash("Goals can only be recorded while a match is In Progress. Change the status first.")
                return redirect(url_for("scores_page"))

            player = conn.execute(

                """

                SELECT team_id FROM players

                WHERE player_id = %s

                """,

                (player_id,)

            ).fetchone()



            if player is None:

                flash("The selected player does not exist.")

                return redirect(url_for("scores_page"))



            if player[0] not in (match[0], match[1]):

                flash("The player must belong to one of the teams in this match.")

                return redirect(url_for("scores_page"))



            conn.execute(

                """

                INSERT INTO player_match_stats

                    (match_id, player_id, goals_scored)

                VALUES (%s, %s, %s)

                ON CONFLICT (match_id, player_id)

                DO UPDATE SET goals_scored = EXCLUDED.goals_scored

                """,

                (match_id, player_id, goals)

            )



        flash("Player goal statistics saved successfully!")



    except ValueError:

        flash("Enter valid match, player, and non-negative goal values.")

    except Exception:

        app.logger.exception("Could not save player goals")

        flash("Could not save player statistics.")



    return redirect(url_for("scores_page"))





if __name__ == "__main__":

    app.run(debug=True)
