import pandas as pd
import streamlit as st
from collections import defaultdict

# Load fielding scores CSV
fielding_df = pd.read_csv("Fielding_Scores.csv")
fielding_score_map = fielding_df.set_index("Player Name")["Predicted_Fielding_Score"].to_dict()

def select_most_reliable_batters(final_df, roles_df, innings_df):
    positions = list(range(1, 8))
    max_inns = innings_df['Inns'].max()
    innings_summary = innings_df.groupby(["Player Name", "Position"])["Inns"].sum().reset_index()
    total_inns_per_player = innings_df.groupby("Player Name")['Inns'].sum().to_dict()

    position_rankings = {}
    player_position_scores = defaultdict(dict)

    for pos in positions:
        pos_df = final_df[final_df["Position"] == pos].copy()
        valid_roles = ["Batsman", "WK-Batsman", "Batting Allrounder"]
        pos_df = pos_df[pos_df["Role"].isin(valid_roles)]

        pos_inns_map = innings_summary[innings_summary["Position"] == pos].set_index("Player Name")["Inns"].to_dict()
        std_score = pos_df["Predicted_Score"].std()
        std_inns = pd.Series(pos_inns_map).std()
        total_var = std_score + std_inns + 1e-8
        alpha = std_score / total_var
        beta = std_inns / total_var

        pos_df["Inns_at_Pos"] = pos_df["Player Name"].map(pos_inns_map).fillna(0)
        pos_df["Max_Inns_Pos"] = max(pos_inns_map.values()) if pos_inns_map else 1
        pos_df["Normalized_Inns"] = pos_df["Inns_at_Pos"] / pos_df["Max_Inns_Pos"]
        pos_df["Effective_Score"] = pos_df["Predicted_Score"] * (alpha + beta * pos_df["Normalized_Inns"])
        pos_df["Fielding_Score"] = pos_df["Player Name"].map(fielding_score_map).fillna(0)

        pos_df = pos_df.sort_values(by=["Effective_Score", "Fielding_Score"], ascending=False)
        pos_df = pos_df.drop_duplicates("Player Name")

        position_rankings[pos] = []
        for rank_idx, (_, player) in enumerate(pos_df.iterrows(), start=1):
            player_name = player["Player Name"]
            score = player["Effective_Score"]
            player_data = player.to_dict()
            player_data["Rank"] = rank_idx  # ⬆️ Add Rank

            position_rankings[pos].append((player_name, score, player_data))
            player_position_scores[player_name][pos] = {
                'score': score,
                'fielding_score': player_data["Fielding_Score"],
                'data': player_data
            }

    class OptimalAssignment:
        def __init__(self):
            self.assignments = {}
            self.player_positions = {}

        def assign(self, position, player_name):
            if player_name in self.player_positions:
                old_pos = self.player_positions[player_name]
                if old_pos in self.assignments:
                    del self.assignments[old_pos]
            if position in self.assignments:
                old_player = self.assignments[position]
                if old_player in self.player_positions:
                    del self.player_positions[old_player]
            self.assignments[position] = player_name
            self.player_positions[player_name] = position

        def is_player_assigned(self, player_name):
            return player_name in self.player_positions

        def get_player_at_position(self, position):
            return self.assignments.get(position)

        def remove_player(self, player_name):
            if player_name in self.player_positions:
                position = self.player_positions[player_name]
                del self.assignments[position]
                del self.player_positions[player_name]
                return position
            return None

        def get_assigned_positions(self):
            return set(self.assignments.keys())

        def get_assigned_players(self):
            return set(self.player_positions.keys())

    def find_optimal_assignment():
        assignment = OptimalAssignment()

        for pos in positions:
            best_available = None
            best_score = -1
            best_fielding = -1
            for player_name, score, player_data in position_rankings[pos]:
                if not assignment.is_player_assigned(player_name):
                    fielding = fielding_score_map.get(player_name, 0)
                    if (abs(score - best_score) < 0.001):
                        if fielding > best_fielding:
                            best_available = player_name
                            best_score = score
                            best_fielding = fielding
                    elif score > best_score:
                        best_available = player_name
                        best_score = score
                        best_fielding = fielding
            if best_available:
                assignment.assign(pos, best_available)

        improved = True
        max_iterations = 10
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            for pos in positions:
                current_player = assignment.get_player_at_position(pos)
                if not current_player:
                    continue
                current_score = player_position_scores[current_player][pos]['score']
                current_fielding = player_position_scores[current_player][pos]['fielding_score']
                for player_name, score, player_data in position_rankings[pos]:
                    new_fielding = fielding_score_map.get(player_name, 0)
                    if not assignment.is_player_assigned(player_name):
                        if (
                            score > current_score or
                            (abs(score - current_score) < 0.01 and new_fielding > current_fielding)
                        ):
                            assignment.assign(pos, player_name)
                            improved = True
                            break
                    else:
                        other_pos = assignment.player_positions[player_name]
                        other_current_score = player_position_scores[player_name][other_pos]['score']
                        current_at_other_score = player_position_scores[current_player].get(other_pos, {}).get('score', 0)
                        if current_at_other_score == 0:
                            continue
                        current_total = current_score + other_current_score
                        new_total = score + current_at_other_score
                        if new_total > current_total:
                            assignment.assign(pos, player_name)
                            assignment.assign(other_pos, current_player)
                            improved = True
                            break
                if improved:
                    break

        for pos in positions:
            if pos not in assignment.assignments:
                for player_name, score, player_data in position_rankings[pos]:
                    if not assignment.is_player_assigned(player_name):
                        assignment.assign(pos, player_name)
                        break

        return assignment

    final_assignment = find_optimal_assignment()

    final_selections = []
    total_score = 0
    for pos in positions:
        player_name = final_assignment.get_player_at_position(pos)
        if player_name and pos in player_position_scores[player_name]:
            player_data = player_position_scores[player_name][pos]['data']
            final_selections.append(player_data)
            total_score += player_position_scores[player_name][pos]['score']

    if final_selections:
        best_7_df = pd.DataFrame(final_selections)
        best_7_df = best_7_df.sort_values("Position").reset_index(drop=True)

        st.subheader("\U0001F3CF Position-Optimal Batting Lineup")
        st.write(f"**Total Lineup Score: {total_score:.4f}**")
        st.dataframe(best_7_df[["Player Name", "Role", "Position", "Rank", "Predicted_Score", "Effective_Score", "Fielding_Score"]])

        #with st.expander("\U0001F4CA Position Performance Analysis"):
        tab1, tab2 = st.tabs(["\U0001F4CA Position Performance Analysis", "\U0001F501 Assignment Process"])
        with tab1:
            st.write("Each position filled with the optimal performer:")
            for pos in positions:
                player_name = final_assignment.get_player_at_position(pos)
                if player_name:
                    best_for_pos = position_rankings[pos][0][0] if position_rankings[pos] else None
                    is_optimal_for_position = (player_name == best_for_pos)
                    player_rank = None
                    for i, (p_name, _, _) in enumerate(position_rankings[pos]):
                        if p_name == player_name:
                            player_rank = i + 1
                            break
                    status = "\U0001F947 Optimal" if is_optimal_for_position else f"#{player_rank} choice"
                    score = player_position_scores[player_name][pos]['score']
                    st.write(f"**Position {pos}**: {player_name} - {status} (Score: {score:.4f})")

        #with st.expander("\U0001F501 Assignment Process"):
        with tab2:
            st.write("All candidates considered for each position:")
            for pos in positions:
                st.write(f"**Position {pos}:**")
                assigned_player = final_assignment.get_player_at_position(pos)
                for i, (player_name, score, _) in enumerate(position_rankings[pos]):
                    if player_name == assigned_player:
                        status = "✅ SELECTED"
                    elif not final_assignment.is_player_assigned(player_name):
                        status = "⚪ Available for selection"
                    else:
                        status = "❌ Already selected"
                    st.write(f"  {i+1}. {player_name} (Score: {score:.4f}) - {status}")
                st.write("")

        return best_7_df, position_rankings
    else:
        st.error("Could not create optimal lineup assignments.")
        return pd.DataFrame()

def select_dynamic_reliable_batters(final_df, roles_df, innings_df, match_context, fielding_df):

    positions = list(range(1, 8))
    combo = match_context["Team_Combo"]

    max_batters = min(combo["Batters"] + combo["Batting_AR"], 7)
    required_bats = combo["Batters"]
    required_ars = combo["Batting_AR"]
    required_wk = 1

    fielding_score_map = fielding_df.set_index("Player Name")["Predicted_Fielding_Score"].to_dict()
    innings_summary = innings_df.groupby(["Player Name", "Position"])["Inns"].sum().reset_index()

    position_rankings = {}
    player_position_scores = defaultdict(dict)

    for pos in positions:
        pos_df = final_df[final_df["Position"] == pos].copy()
        valid_roles = ["Batsman", "WK-Batsman", "Batting Allrounder"]
        pos_df = pos_df[pos_df["Role"].isin(valid_roles)]

        pos_inns_map = innings_summary[innings_summary["Position"] == pos].set_index("Player Name")["Inns"].to_dict()
        std_score = pos_df["Predicted_Score"].std()
        std_inns = pd.Series(pos_inns_map).std()
        total_var = std_score + std_inns + 1e-8
        alpha = std_score / total_var
        beta = std_inns / total_var

        pos_df["Inns_at_Pos"] = pos_df["Player Name"].map(pos_inns_map).fillna(0)
        pos_df["Max_Inns_Pos"] = max(pos_inns_map.values()) if pos_inns_map else 1
        pos_df["Normalized_Inns"] = pos_df["Inns_at_Pos"] / pos_df["Max_Inns_Pos"]
        pos_df["Effective_Score"] = pos_df["Predicted_Score"] * (alpha + beta * pos_df["Normalized_Inns"])
        pos_df["Fielding_Score"] = pos_df["Player Name"].map(fielding_score_map).fillna(0)

        pos_df = pos_df.sort_values(by=["Effective_Score", "Fielding_Score"], ascending=False)
        pos_df = pos_df.drop_duplicates("Player Name")

        position_rankings[pos] = []
        for rank_idx, (_, player) in enumerate(pos_df.iterrows(), start=1):
            player_name = player["Player Name"]
            score = player["Effective_Score"]
            player_data = player.to_dict()
            player_data["Rank"] = rank_idx

            position_rankings[pos].append((player_name, score, player_data))
            player_position_scores[player_name][pos] = {
                'score': score,
                'fielding_score': player_data["Fielding_Score"],
                'data': player_data
            }

    class RoleAwareAssignment:
        def __init__(self):
            self.assignments = {}
            self.player_positions = {}
            self.role_counts = {"Batsman": 0, "Batting Allrounder": 0, "WK-Batsman": 0}

        def can_assign(self, role):
            if "WK-Batsman" in role:
                return (self.role_counts["WK-Batsman"] < required_wk or self.role_counts["Batsman"] < required_bats)
            elif "Batting Allrounder" in role:
                return self.role_counts["Batting Allrounder"] < required_ars
            elif "Batsman" in role:
                return self.role_counts["Batsman"] < required_bats or self.role_counts["WK-Batsman"] < required_wk
            return False

        def assign(self, position, player_name, role):
            if player_name in self.player_positions:
                old_pos = self.player_positions[player_name]
                if old_pos in self.assignments:
                    del self.assignments[old_pos]
            if position in self.assignments:
                old_player = self.assignments[position]
                if old_player in self.player_positions:
                    del self.player_positions[old_player]

            self.assignments[position] = player_name
            self.player_positions[player_name] = position

            if "WK-Batsman" in role:
                if self.role_counts["WK-Batsman"] < required_wk:
                    self.role_counts["WK-Batsman"] += 1
                elif self.role_counts["Batsman"] < required_bats:
                    self.role_counts["Batsman"] += 1
            elif "Batting Allrounder" in role:
                self.role_counts["Batting Allrounder"] += 1
            elif "Batsman" in role:
                self.role_counts["Batsman"] += 1

        def is_player_assigned(self, player_name):
            return player_name in self.player_positions

        def get_player_at_position(self, position):
            return self.assignments.get(position)

        def get_total_assigned(self):
            return len(self.assignments)

        def get_assigned_players(self):
            return set(self.player_positions.keys())

    def find_optimal_assignment():
        assignment = RoleAwareAssignment()

        for pos in positions:
            if assignment.get_total_assigned() >= max_batters:
                break
            best_available = None
            best_score = -1
            best_fielding = -1
            for player_name, score, player_data in position_rankings[pos]:
                if not assignment.is_player_assigned(player_name):
                    role = player_data["Role"]
                    if not assignment.can_assign(role):
                        continue
                    fielding = fielding_score_map.get(player_name, 0)
                    if (abs(score - best_score) < 0.001):
                        if fielding > best_fielding:
                            best_available = (player_name, role)
                            best_score = score
                            best_fielding = fielding
                    elif score > best_score:
                        best_available = (player_name, role)
                        best_score = score
                        best_fielding = fielding
            if best_available:
                assignment.assign(pos, best_available[0], best_available[1])

        # Fallback: ensure at least one WK-Batsman
        if assignment.role_counts["WK-Batsman"] < required_wk:
            for pos in positions:
                for player_name, score, player_data in position_rankings[pos]:
                    if "WK-Batsman" in player_data["Role"] and not assignment.is_player_assigned(player_name):
                        assignment.assign(pos, player_name, player_data["Role"])
                        break
                if assignment.role_counts["WK-Batsman"] >= required_wk:
                    break

        return assignment

    final_assignment = find_optimal_assignment()

    final_selections = []
    total_score = 0
    for pos in sorted(final_assignment.assignments.keys()):
        player_name = final_assignment.get_player_at_position(pos)
        if player_name and pos in player_position_scores[player_name]:
            player_data = player_position_scores[player_name][pos]['data']
            final_selections.append(player_data)
            total_score += player_position_scores[player_name][pos]['score']

    if final_selections:
        best_df = pd.DataFrame(final_selections).sort_values("Position").reset_index(drop=True)
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.subheader("🧠 Role-Constrained Position-Optimal Batting Lineup")
        #st.write("This lineup arranges players into the best batting positions, based on the number of batsmen (including WK-Batsman) and batting all-rounders selected by you.")
        st.write(f"**Total Lineup Score: {total_score:.4f}**")
        st.dataframe(best_df[["Player Name", "Role", "Position", "Predicted_Score"]])

        return best_df
    else:
        st.error("Could not create optimal lineup assignments.")
        return pd.DataFrame()

def select_dynamic_bowlers_assignment(bowlers_df, fielding_df, innings_df, match_context, used_positions, used_players):
    combo = match_context["Team_Combo"]
    unavailable = set(match_context.get("Unavailable", []))
    # Define exact required roles
    required_counts = {
        "Pacer": combo.get("Pacer_Pure", 0),
        "Spinner": combo.get("Spinner_Pure", 0),
        "Bowling Allrounder (Spinner)": combo.get("Spinner_Bowling_AR", 0)
    }
    total_required = sum(required_counts.values())
    max_positions = set(range(1, 13)) - set(used_positions)

    # Mapping fielding score
    fielding_map = fielding_df.set_index("Player Name")["Predicted_Fielding_Score"].to_dict()
    innings_summary = innings_df.groupby(["Player Name", "Position"])["Inns"].sum().reset_index()

    bowlers_df = bowlers_df.copy()
    bowlers_df["Fielding_Score"] = bowlers_df["Player Name"].map(fielding_map).fillna(0)

    # Filter out unavailable or used players
    bowlers_df = bowlers_df[
        (~bowlers_df["Player Name"].isin(unavailable)) &
        (~bowlers_df["Player Name"].isin(used_players))
    ]

    # Apply innings-aware scoring
    player_position_scores = defaultdict(dict)
    position_rankings = defaultdict(list)

    for pos in max_positions:
        pos_df = bowlers_df[bowlers_df["Position"] == pos].copy()
        if pos_df.empty:
            continue

        pos_inns_map = innings_summary[innings_summary["Position"] == pos].set_index("Player Name")["Inns"].to_dict()
        std_score = pos_df["Predicted_Bowl_Score"].std()
        std_inns = pd.Series(pos_inns_map).std()
        total_var = std_score + std_inns + 1e-8
        alpha = std_score / total_var
        beta = std_inns / total_var

        pos_df["Inns_at_Pos"] = pos_df["Player Name"].map(pos_inns_map).fillna(0)
        pos_df["Max_Inns_Pos"] = max(pos_inns_map.values()) if pos_inns_map else 1
        pos_df["Normalized_Inns"] = pos_df["Inns_at_Pos"] / pos_df["Max_Inns_Pos"]
        pos_df["Effective_Score"] = pos_df["Predicted_Bowl_Score"] * (alpha + beta * pos_df["Normalized_Inns"])
        pos_df["Total_Score"] = pos_df["Effective_Score"] + pos_df["Fielding_Score"]

        for _, row in pos_df.iterrows():
            name = row["Player Name"]
            role = row["Role"]
            score = row["Total_Score"]
            fielding = row["Fielding_Score"]
            player_position_scores[name][pos] = {
                "score": score,
                "fielding_score": fielding,
                "data": row.to_dict()
            }
            position_rankings[pos].append((name, score, role, fielding, row.to_dict()))


    # Sort each position’s ranking
    for pos in position_rankings:
        position_rankings[pos].sort(key=lambda x: (-x[1], -x[3]))

    # Role-aware assignment class
    class RoleAwareAssignment:
        def __init__(self):
            self.assignments = {}  # pos -> (player, role)
            self.player_positions = {}  # player -> pos
            self.role_counts = {k: 0 for k in required_counts}

        def get_exact_role_key(self, role):
            for key in self.role_counts:
                if role.strip().lower() == key.strip().lower():
                    return key
            return None

        def can_assign(self, role):
            key = self.get_exact_role_key(role)
            return key is not None and self.role_counts[key] < required_counts[key]

        def assign(self, position, player_name, role):
            key = self.get_exact_role_key(role)
            if key is None:
                return

            # Remove previous assignment if exists
            if player_name in self.player_positions:
                old_pos = self.player_positions[player_name]
                if old_pos in self.assignments:
                    old_player, old_role = self.assignments[old_pos]
                    old_key = self.get_exact_role_key(old_role)
                    if old_key:
                        self.role_counts[old_key] -= 1
                    del self.assignments[old_pos]
                del self.player_positions[player_name]

            if position in self.assignments:
                old_player, old_role = self.assignments[position]
                old_key = self.get_exact_role_key(old_role)
                if old_player in self.player_positions:
                    del self.player_positions[old_player]
                if old_key:
                    self.role_counts[old_key] -= 1
                del self.assignments[position]

            self.assignments[position] = (player_name, role)
            self.player_positions[player_name] = position
            self.role_counts[key] += 1

        def is_player_assigned(self, player_name):
            return player_name in self.player_positions

        def get_player_at_position(self, position):
            val = self.assignments.get(position)
            if val is None:
                return None
            return val[0]

        def get_total_assigned(self):
            return len(self.assignments)

    # Assignment algorithm
    def find_optimal_assignment():
        assignment = RoleAwareAssignment()

        for pos in sorted(position_rankings.keys()):
            if assignment.get_total_assigned() >= total_required:
                break

            for name, score, role, fielding, data in position_rankings[pos]:
                if assignment.is_player_assigned(name):
                    continue
                if not assignment.can_assign(role):
                    continue
                assignment.assign(pos, name, role)
                break

        # Fallback: fill if under-assigned
        if assignment.get_total_assigned() < total_required:
            needed = total_required - assignment.get_total_assigned()
            unassigned_positions = sorted(max_positions - set(assignment.assignments.keys()))
            assigned_players = set(assignment.player_positions.keys())
            remaining_candidates = []
            for pos in unassigned_positions:
                for name, score, role, fielding, data in position_rankings.get(pos, []):
                    if name not in assigned_players and assignment.can_assign(role):
                        remaining_candidates.append((pos, name, score, role, fielding, data))
            remaining_candidates.sort(key=lambda x: (-x[2], -x[4]))

            for pos, name, score, role, fielding, data in remaining_candidates:
                if assignment.get_total_assigned() >= total_required:
                    break
                if assignment.is_player_assigned(name):
                    continue
                assignment.assign(pos, name, role)

        return assignment

    # Apply assignment
    final_assignment = find_optimal_assignment()

    selected_bowlers = []
    for pos in sorted(final_assignment.assignments.keys()):
        player_name = final_assignment.get_player_at_position(pos)
        if player_name in player_position_scores and pos in player_position_scores[player_name]:
            player_data = player_position_scores[player_name][pos]["data"]
            selected_bowlers.append(player_data)

    final_bowlers_df = pd.DataFrame(selected_bowlers).reset_index(drop=True)
    st.markdown("<br><br>",unsafe_allow_html=True)
    st.subheader("🧠 Role-Constrained Optimal Bowling Selection")
    #st.write(f"Total Bowlers Selected: {len(final_bowlers_df)} / {total_required}")
    #st.write("This lineup arranges players into positions based on the number of pure spinners, pure pacers, and batting and bowling all-rounders selected by you.")
    st.dataframe(final_bowlers_df[["Player Name", "Role", "Position", "Predicted_Bowl_Score"]].rename(columns={
        "Predicted_Bowl_Score": "Predicted_Score"
    }))

    return final_bowlers_df

    