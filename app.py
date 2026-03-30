from flask import Flask, render_template, request, redirect, url_for, send_file
import random
import re
import os
import csv
import io

app = Flask(__name__)


def is_valid_name(name):
    return bool(re.fullmatch(r"[A-Za-z\s\-]+", name.strip()))


def get_helper_text(selected_mode):
    return ""


def render_home(
    teams=None,
    error_message=None,
    old_names="",
    old_team_count="",
    selected_mode="quick",
    use_team_names=True,
    total_participants=None,
    number_of_teams=None,
    average_team_size=None,
    average_team_rating=None,
    captains=None,
    display_team_names=None,
    team_totals=None
):
    return render_template(
        "index.html",
        teams=teams,
        error_message=error_message,
        old_names=old_names,
        old_team_count=old_team_count,
        selected_mode=selected_mode,
        helper_text=get_helper_text(selected_mode),
        display_mode=selected_mode,
        use_team_names=use_team_names,
        total_participants=total_participants,
        number_of_teams=number_of_teams,
        average_team_size=average_team_size,
        average_team_rating=average_team_rating if average_team_rating is not None else "N/A",
        captains=captains if captains is not None else [],
        display_team_names=display_team_names if display_team_names is not None else [],
        team_totals=team_totals if team_totals is not None else []
    )


def parse_quick_names(raw_names):
    cleaned_names = []
    names_list = raw_names.split(",")

    for name in names_list:
        name = name.strip().title()

        if name == "":
            continue

        if not is_valid_name(name):
            return [], "Names can only contain letters, spaces, and hyphens."

        cleaned_names.append(name)

    return cleaned_names, None


def parse_balanced_names(raw_names):
    cleaned_names = []
    names_list = raw_names.split(",")

    for item in names_list:
        item = item.strip()

        if item == "":
            continue

        if "-" not in item:
            return [], "Balanced Mode format must be Name-Rating. Example: John-8, Jane-5, Alex-7"

        person_parts = item.rsplit("-", 1)
        person_name = person_parts[0].strip().title()
        person_rating_text = person_parts[1].strip()

        if person_name == "":
            return [], "Every entry must contain a valid name before the rating."

        if not is_valid_name(person_name):
            return [], "Names can only contain letters, spaces, and hyphens."

        if not person_rating_text.isdigit():
            return [], "Rating must be a whole number from 1 to 10."

        person_rating = int(person_rating_text)

        if person_rating < 1 or person_rating > 10:
            return [], "Rating must be between 1 and 10."

        cleaned_names.append({
            "name": person_name,
            "skill": person_rating
        })

    return cleaned_names, None


def build_quick_teams(cleaned_names, team_count):
    random.shuffle(cleaned_names)

    teams = [[] for _ in range(team_count)]

    for index, name in enumerate(cleaned_names):
        team_number = index % team_count
        teams[team_number].append(name)

    captains = []
    team_totals = []

    for team in teams:
        team_totals.append("N/A")
        if len(team) > 0:
            captains.append(team[0])
        else:
            captains.append("No Captain")

    return teams, captains, team_totals


def build_balanced_teams(cleaned_names, team_count):
    random.shuffle(cleaned_names)
    cleaned_names.sort(key=lambda person: person["skill"], reverse=True)

    team_data = []
    for _ in range(team_count):
        team_data.append({
            "members": [],
            "total_skill": 0
        })

    for person in cleaned_names:
        min_size = min(len(team["members"]) for team in team_data)
        candidate_teams = [team for team in team_data if len(team["members"]) == min_size]

        min_skill = min(team["total_skill"] for team in candidate_teams)
        best_teams = [team for team in candidate_teams if team["total_skill"] == min_skill]

        chosen_team = random.choice(best_teams)
        chosen_team["members"].append(person)
        chosen_team["total_skill"] += person["skill"]

    teams = []
    captains = []
    team_totals = []

    for team in team_data:
        members = team["members"]
        teams.append(members)
        team_totals.append(team["total_skill"])

        if len(members) > 0:
            max_skill = max(member["skill"] for member in members)
            top_members = [m for m in members if m["skill"] == max_skill]
            captain = random.choice(top_members)
            captains.append(captain["name"])
        else:
            captains.append("No Captain")

    return teams, captains, team_totals


def generate_team_labels(team_count, use_team_names):
    if not use_team_names:
        return [f"Team {i + 1}" for i in range(team_count)]

    team_labels = [
    "Crimson Falcons","Silent Warriors","Electric Titans","Rapid Riders","Golden Guardians",
    "Iron Hunters","Shadow Strikers","Quantum Raiders","Fierce Knights","Blazing Commanders",
    "Dynamic Legends","Phantom Force","Vivid Pulse","Infinite Orbit","Stealth Unit",
    "Radiant Crew","Cosmic Division","Hyper Squad","Neon Syndicate","Storm Alliance",
    "Turbo Collective","Prime Network","Dark Empire","Solar Vortex","Nova Squad",
    "Ultra Force","Core Titans","Epic Riders","Royal Guardians","Crystal Hunters",
    "Fusion Strikers","Arctic Raiders","Infernal Knights","Midnight Commanders","Digital Legends",
    "Atomic Force","Cyber Pulse","Glacial Orbit","Titanic Unit","Wild Crew",
    "Velocity Squad","Ignite Syndicate","Momentum Alliance","Catalyst Collective","Spectrum Network",
    "Gravity Empire","Apex Vortex","Vertex Squad","Drift Force","Surge Titans",
    "Echo Riders","Flare Guardians","Striker Hunters","Falcon Raiders","Raptor Knights",
    "Panther Commanders","Cobra Legends","Wolfpack Force","Vanguard Pulse","Sentinel Orbit",
    "Spartan Unit","Gladiator Crew","Cyclone Squad","Hurricane Syndicate","Tempest Alliance",
    "Inferno Collective","Tornado Network","Blizzard Empire","Thunder Vortex","Lightning Squad",
    "Shadow Force","Velocity Titans","Momentum Riders","Impulse Guardians","Fusion Hunters",
    "Matrix Raiders","Vector Knights","Nexus Commanders","Core Legends","Catalyst Force",
    "Spectrum Pulse","Gravity Orbit","Axis Unit","Sync Crew","Binary Squad",
    "Logic Syndicate","Circuit Alliance","CodeX Collective","Algo Network","Atlas Empire",
    "Horizon Vortex","Summit Squad","Peak Force","Pioneer Titans","Voyager Riders",
    "Frontier Guardians","Expedition Hunters","Trailblazer Raiders","Quest Knights","Odyssey Commanders",
    "Legacy Legends","Origin Force","Genesis Pulse","Continuum Orbit","Infinity Unit",
    "Eon Crew","Epoch Squad","Chronos Syndicate","PulseX Alliance","NovaCore Collective",
    "HyperGrid Network","QuantumEdge Empire","DarkMatter Vortex","SolarFlux Squad","NeonEdge Force",
    "CyberStorm Titans","AtomicWave Riders","DigitalFlux Guardians","FusionEdge Hunters","CorePulse Raiders",
    "VertexEdge Knights","OrbitX Commanders","VectorCore Legends","MatrixEdge Force","LogicPulse Pulse",
    "BinaryEdge Orbit","CircuitX Unit","CodeStorm Crew","AlgoEdge Squad","AtlasCore Syndicate",
    "SummitEdge Alliance","PeakX Collective","PioneerCore Network","VoyagerEdge Empire","FrontierX Vortex",
    "QuestCore Squad","OdysseyEdge Force","LegacyX Titans","OriginCore Riders","GenesisEdge Guardians",
    "ContinuumX Hunters","InfinityCore Raiders","EpochEdge Knights","ChronosCore Commanders","EonEdge Legends"
    ]


    random.shuffle(team_labels)

    display_team_names = []
    for i in range(team_count):
        if i < len(team_labels):
            display_team_names.append(team_labels[i])
        else:
            display_team_names.append(f"Team {i + 1}")

    return display_team_names


def parse_uploaded_csv(uploaded_file):
    try:
        stream = io.StringIO(uploaded_file.stream.read().decode("utf-8-sig"))
        reader = csv.reader(stream)

        rows = []
        for row in reader:
            if not row:
                continue

            cleaned_row = [cell.strip() for cell in row if cell.strip() != ""]
            if cleaned_row:
                rows.append(cleaned_row)

        if not rows:
            return "", "", "Uploaded CSV file is empty."

        first_row = [cell.strip().lower() for cell in rows[0]]

        if len(first_row) >= 2 and first_row[0] in ["name", "names", "member", "members"] and first_row[1] in ["rating", "score"]:
            rows = rows[1:]
        elif len(first_row) >= 1 and first_row[0] in ["name", "names", "member", "members"]:
            rows = rows[1:]

        if not rows:
            return "", "", "Uploaded CSV file has no valid data rows."

        is_balanced_csv = all(len(row) >= 2 and row[1].strip().isdigit() for row in rows)

        if is_balanced_csv:
            collected_entries = []

            for row in rows:
                if len(row) < 2:
                    return "", "", "Balanced CSV must contain two columns: name,rating"

                name = row[0].strip().title()
                rating = row[1].strip()

                if name == "" or rating == "":
                    continue

                collected_entries.append(f"{name}-{rating}")

            if not collected_entries:
                return "", "", "Balanced CSV must contain valid name and rating rows."

            return ", ".join(collected_entries), "balanced", None

        collected_names = []

        for row in rows:
            if len(row) < 1:
                continue

            name = row[0].strip().title()

            if name == "":
                continue

            collected_names.append(name)

        if not collected_names:
            return "", "", "Quick CSV must contain at least one valid name."

        return ", ".join(collected_names), "quick", None

    except Exception:
        return "", "", "Could not read the uploaded CSV file. Please upload a valid CSV."


@app.route("/", methods=["GET", "POST"])
def home():
    selected_mode = "quick"
    use_team_names = True

    if request.method == "POST":
        selected_mode = request.form.get("mode", "quick")
        use_team_names = request.form.get("use_team_names") == "on"
        names = request.form.get("names", "").strip()
        team_count_text = request.form.get("team_count", "").strip()
        uploaded_file = request.files.get("csv_file")

        if uploaded_file and uploaded_file.filename:
            parsed_names, detected_mode, csv_error = parse_uploaded_csv(uploaded_file)

            if csv_error:
                return render_home(
                    teams=None,
                    error_message=csv_error,
                    old_names=names,
                    old_team_count=team_count_text,
                    selected_mode=selected_mode,
                    use_team_names=use_team_names
                )

            names = parsed_names
            selected_mode = detected_mode

        if selected_mode == "quick":
            cleaned_names, parse_error = parse_quick_names(names)
        else:
            cleaned_names, parse_error = parse_balanced_names(names)

        if parse_error:
            return render_home(
                teams=None,
                error_message=parse_error,
                old_names=names,
                old_team_count=team_count_text,
                selected_mode=selected_mode,
                use_team_names=use_team_names
            )

        if len(cleaned_names) == 0:
            return render_home(
                teams=None,
                error_message="Please enter at least one valid name.",
                old_names=names,
                old_team_count=team_count_text,
                selected_mode=selected_mode,
                use_team_names=use_team_names
            )

        if team_count_text == "":
            return render_home(
                teams=None,
                error_message="Please enter the number of teams.",
                old_names=names,
                old_team_count=team_count_text,
                selected_mode=selected_mode,
                use_team_names=use_team_names
            )

        if not team_count_text.isdigit():
            return render_home(
                teams=None,
                error_message="Number of teams must be a whole number.",
                old_names=names,
                old_team_count=team_count_text,
                selected_mode=selected_mode,
                use_team_names=use_team_names
            )

        team_count = int(team_count_text)

        if team_count <= 0:
            return render_home(
                teams=None,
                error_message="Number of teams must be greater than 0.",
                old_names=names,
                old_team_count=team_count_text,
                selected_mode=selected_mode,
                use_team_names=use_team_names
            )

        if team_count > len(cleaned_names):
            return render_home(
                teams=None,
                error_message="Number of teams cannot be more than number of participants.",
                old_names=names,
                old_team_count=team_count_text,
                selected_mode=selected_mode,
                use_team_names=use_team_names
            )

        if selected_mode == "quick":
            teams, captains, team_totals = build_quick_teams(cleaned_names, team_count)
            average_team_rating = None
        else:
            teams, captains, team_totals = build_balanced_teams(cleaned_names, team_count)
            total_rating = sum(person["skill"] for person in cleaned_names)
            average_team_rating = round(total_rating / team_count, 2)

        total_participants = len(cleaned_names)
        number_of_teams = team_count
        average_team_size = round(total_participants / number_of_teams, 2)
        display_team_names = generate_team_labels(len(teams), use_team_names)

        return render_home(
            teams=teams,
            error_message=None,
            old_names=names,
            old_team_count=str(team_count),
            selected_mode=selected_mode,
            use_team_names=use_team_names,
            total_participants=total_participants,
            number_of_teams=number_of_teams,
            average_team_size=average_team_size,
            average_team_rating=average_team_rating,
            captains=captains,
            display_team_names=display_team_names,
            team_totals=team_totals
        )

    return render_home(
        teams=None,
        error_message=None,
        old_names="",
        old_team_count="",
        selected_mode=selected_mode,
        use_team_names=use_team_names
    )


@app.route("/reset")
def reset():
    return redirect(url_for("home"))


@app.route("/sample-csv/quick")
def download_quick_sample_csv():
    csv_content = "name\nJohn Doe\nJane Doe\nAlex Smith\nSam Wilson\n"
    return send_file(
        io.BytesIO(csv_content.encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="intelliteam_quick_sample.csv"
    )


@app.route("/sample-csv/balanced")
def download_balanced_sample_csv():
    csv_content = "name,rating\nJohn Doe,8\nJane Doe,5\nAlex Smith,7\nSam Wilson,6\n"
    return send_file(
        io.BytesIO(csv_content.encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="intelliteam_balanced_sample.csv"
    )


port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)