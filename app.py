
from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])

def home():
    selected_mode = "quick"
    helper_text = "Enter names separated by commas. Example: Ali, Sara, John, Fatima"

    if request.method == "POST":

        selected_mode = request.form.get("mode","quick")

        # cheecking selected mode and assigning text field helper text
        if selected_mode == "balanced":
            helper_text = "Enter each person as Name-Rating, separated by commas. Rating must be from 1 to 10. Example: Ali-8, Sara-5, John-7"
        else:
            helper_text = "Enter names separated by commas. Example: Ali, Sara, John, Fatima"

        names = request.form["names"]
        team_count = request.form["team_count"]


        cleaned_names = []

        # quick mode parsing and error handling section
        if selected_mode == "quick":
            names_list = names.split(",")

            for name in names_list:
                name = name.strip().title()

                if name != "":
                    # error handling if name is only int - quick mode
                    if name.isdigit():
                        return render_template(
                            "index.html",
                            teams=None,
                            error_message="Names cannot contain only numbers.",
                            old_names=names,
                            old_team_count=team_count,
                            selected_mode=selected_mode,
                            helper_text=helper_text,
                            display_mode=selected_mode,
                            average_team_rating="N/A",
                            team_totals=[],
                        )

                    cleaned_names.append(name)

        # balanced mode parsing and error handling
        elif selected_mode == "balanced":
            names_list = names.split(",")

            for item in names_list:
                item = item.strip()

                if item == "":
                    continue
                
                # error handling if - is not given
                if "-" not in item:
                    return render_template(
                        "index.html",
                        teams=None,
                        error_message="Balanced Mode format must be Name-Rating. Example: Ali-8, Sara-5",
                        old_names=names,
                        old_team_count=team_count,
                        selected_mode=selected_mode,
                        helper_text=helper_text,
                        display_mode=selected_mode,
                        average_team_rating="N/A",
                        team_totals=[]
                    )

                person_parts = item.rsplit("-", 1)
                person_name = person_parts[0].strip().title()
                person_skill_text = person_parts[1].strip()

                # error handling if no name, only skill
                if person_name == "":
                    return render_template(
                        "index.html",
                        teams=None,
                        error_message="Every entry must contain a valid name before the Rating.",
                        old_names=names,
                        old_team_count=team_count,
                        selected_mode=selected_mode,
                        helper_text=helper_text,
                        display_mode=selected_mode,
                        average_team_rating="N/A",
                        team_totals=[]
                    )

                # error handling if name is int - balanced
                if person_name.isdigit():
                    return render_template(
                        "index.html",
                        teams=None,
                        error_message="Names cannot contain only numbers.",
                        old_names=names,
                        old_team_count=team_count,
                        selected_mode=selected_mode,
                        helper_text=helper_text,
                        display_mode=selected_mode,
                        average_team_rating="N/A",
                        team_totals=[]
                    )
                
                # error handling if skill is not in correct format
                if not person_skill_text.isdigit():
                    return render_template(
                        "index.html",
                        teams=None,
                        error_message="Rating must be a whole number from 1 to 10.",
                        old_names=names,
                        old_team_count=team_count,
                        selected_mode=selected_mode,
                        helper_text=helper_text,
                        display_mode=selected_mode,
                        average_team_rating="N/A",
                        team_totals=[]
                    )

                person_skill = int(person_skill_text)

                # error handling skill is not in correct range
                if person_skill < 1 or person_skill > 10:
                    return render_template(
                        "index.html",
                        teams=None,
                        error_message="Skill must be between 1 and 10.",
                        old_names=names,
                        old_team_count=team_count,
                        selected_mode=selected_mode,
                        helper_text=helper_text,
                        display_mode=selected_mode,
                        average_team_rating="N/A",
                        team_totals=[]
                    )

                cleaned_names.append({
                    "name": person_name,
                    "skill": person_skill
                })


    # common error handling for all modes

        # error handling if no names are given
        if len(cleaned_names) == 0:
            return render_template("index.html",
                                   teams=None,
                                   error_message="Please enter at least one valid name.",
                                   old_names=names,
                                   old_team_count=team_count,
                                   selected_mode=selected_mode,
                                   helper_text=helper_text,
                                   display_mode=selected_mode,
                                   average_team_rating="N/A",
                                   team_totals=[]
                                   )
        
        # error handling if team count is blank
        if team_count =="":
            return render_template("index.html",
                                   teams=None,
                                   error_message="Please enter the number of teams.",
                                   old_names=names,
                                   old_team_count=team_count,
                                   selected_mode=selected_mode,
                                   helper_text=helper_text,
                                   display_mode=selected_mode,
                                   average_team_rating="N/A",
                                   team_totals=[]
                                   )

        # converting team count to int datatype
        team_count = int(team_count)

        # error handling if team count is 0 or -ve
        if team_count <= 0:
            return render_template("index.html",
                                   teams=None,
                                   error_message="Number of teams must be greater than 0.",
                                   old_names=names,
                                   old_team_count=team_count,
                                   selected_mode=selected_mode,
                                   helper_text=helper_text,
                                   display_mode=selected_mode,
                                   average_team_rating="N/A",
                                   team_totals=[]
                                   )
        
        # error handling if team count is more than the no of participants
        if team_count > len(cleaned_names):
            return render_template("index.html",
                                   teams=None,
                                   error_message="Number of teams cannot be more than number of participants.",
                                   old_names=names,
                                   old_team_count=team_count,
                                   selected_mode=selected_mode,
                                   helper_text=helper_text,
                                   display_mode=selected_mode,
                                   average_team_rating="N/A",
                                   team_totals=[]
                                   )

        
        



        
        teams = []
        captains = []# list of captains
        team_totals = []
        team_data = []

        if selected_mode == "quick":
            random.shuffle(cleaned_names)

            for i in range(team_count):
                teams.append([])

            for index, name in enumerate(cleaned_names):
                team_number = index % team_count
                teams[team_number].append(name)

            for team in teams:
                team_totals.append("N/A")
                if len(team) > 0:
                    captains.append(team[0])
                else:
                    captains.append("No Captain")

        elif selected_mode == "balanced":

            # shuffle first to avoid bias
            random.shuffle(cleaned_names)

            # sort by skill (high → low)
            cleaned_names.sort(key=lambda person: person["skill"], reverse=True)

            team_data = []

            for i in range(team_count):
                team_data.append({
                    "members": [],
                    "total_skill": 0
                })

            for person in cleaned_names:
                # smallest team size
                min_size = min(len(team["members"]) for team in team_data)

                # teams with smallest size
                candidate_teams = [team for team in team_data if len(team["members"]) == min_size]

                # lowest total skill among them
                min_skill = min(team["total_skill"] for team in candidate_teams)

                best_teams = [team for team in candidate_teams if team["total_skill"] == min_skill]

                # random tie-break
                chosen_team = random.choice(best_teams)

                chosen_team["members"].append(person)
                chosen_team["total_skill"] += person["skill"]

            # convert to final structure
            teams = []
            captains = []

            for team in team_data:
                members = team["members"]
                teams.append(members)
                team_totals.append(team["total_skill"])

                if len(members) > 0:
                    # pick highest skill captain
                    max_skill = max(member["skill"] for member in members)
                    top_members = [m for m in members if m["skill"] == max_skill]

                    captain = random.choice(top_members)  # random if tie
                    captains.append(captain["name"])
                else:
                    captains.append("No Captain")


    # top summary data block
        total_participants = len(cleaned_names)
        number_of_teams = team_count
        average_team_size = round(total_participants / number_of_teams, 2)

        if selected_mode == "balanced":
            total_rating = sum(person["skill"] for person in cleaned_names)
            average_team_rating = round(total_rating / number_of_teams, 2)
           
        else:
            average_team_rating = "N/A"
           



        # team name generation block
        team_labels = ["Alpha","Beta","Gamma","Delta","Epsilon","Zeta","Eta","Theta","Iota","Kappa","Lambda",
                       "Mu","Nu","Xi","Omicron","Pi","Rho","Sigma","Tau","Upsilon","Phi","Chi","Psi","Omega",
                        "Zephyr","Nova","Orion","Vortex","Blaze","Apex","Zenith","Eclipse","Pulse","Quantum",
                        "Nebula","Titan","Phoenix","Aurora","Vertex","Drift","Ignite","Surge","Echo","Flare",
                        "Striker","Falcon","Raptor","Panther","Cobra","Wolfpack","Vanguard","Sentinel","Spartan",
                        "Gladiator","Storm","Cyclone","Hurricane","Tempest","Inferno","Tornado","Blizzard",
                        "Thunder","Lightning","Shadow","Velocity","Momentum","Impulse","Fusion","Matrix","Vector",
                        "Nexus","Core","Catalyst","Spectrum","Gravity","Orbit","Axis","PulseX","Sync","Binary",
                        "Logic","Circuit","CodeX","Algo","Atlas","Horizon","Summit","Peak","Pioneer","Voyager",
                        "Pathfinder","Frontier","Expedition","Trailblazer","Quest","Odyssey","Legacy","Origin",
                        "Genesis","Continuum","Infinity","Eon","Epoch","Chronos"]
        
        random.shuffle(team_labels) # randomizing team names

        display_team_names = []

        # team names assigining block
        for i in range(len(teams)):
            if i < len(team_labels):
                display_team_names.append(team_labels[i])
            else :
                display_team_names.append(f"Team {i+1}")

        # successful return block    
        return render_template("index.html",
                               teams = teams,
                               error_message=None,
                               old_names=names,
                               old_team_count=team_count,
                               total_participants=total_participants,
                               number_of_teams=number_of_teams,
                               average_team_size=average_team_size,
                               captains=captains,
                               display_team_names=display_team_names,
                               selected_mode=selected_mode,
                               helper_text=helper_text,
                               display_mode=selected_mode,
                               average_team_rating=average_team_rating,
                               team_totals=team_totals
        )
                              
    
    # unsuccessful return block
    return render_template("index.html",
                           teams = None,
                           error_message=None,
                           old_names="",
                           old_team_count="",
                           selected_mode=selected_mode,
                           helper_text=helper_text,
                           display_mode=selected_mode,
                           average_team_rating="N/A",
                           team_totals=[],
                           
                           )


# reset route section
@app.route("/reset")
def reset():
    return redirect(url_for("home"))

import os

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)