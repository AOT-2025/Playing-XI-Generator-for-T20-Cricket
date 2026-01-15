import streamlit as st
import pandas as pd
from composition_rule_engine_new import get_predicted_role_counts

def get_match_context(players_df, team_df):
    st.sidebar.title("Match Context Configuration")

    # Tournament type & opponent
    tournament_type = st.sidebar.radio("Tournament Type", ["ICC", "Series"])
    selected_opponent = None
    if tournament_type == "Series":
        available_opponents = sorted(team_df['Team'].dropna().unique())
        available_opponents = [team for team in available_opponents if team != "India"] 
        selected_opponent = st.sidebar.selectbox("Select Opponent", available_opponents)

    # Ground, pitch, clutch , rank tier 
    home_away = st.sidebar.selectbox("Match Location", ["Home", "Away"])
    pitch_type = st.sidebar.selectbox("Pitch Type", ["Spin", "Pace"])
    is_clutch = st.sidebar.checkbox("Is it a Clutch Match?", value=False)
    rank_tier = st.sidebar.selectbox("Rank Tier", ["Top", "Mid", "Low"])

    # Unavailable players
    st.sidebar.subheader("Team Configuration")
    available_players = players_df['Player Name'].unique()
    unavailable_players = st.sidebar.multiselect("Unavailable Players", available_players)

    # -------------------------------- NEW BLOCK --------------------------------
    st.sidebar.markdown("---")
   
    #fetching role counts from knowledge base
    role_counts = get_predicted_role_counts(pitch_type, home_away, rank_tier, selected_opponent)

    st.session_state["button_clicked"] = False
    # Batting Roles

    max_total = 7
    max_bat_ar = 2
    min_batters = 3

    # Initialize session state variables once
    if "num_batters" not in st.session_state:
        st.session_state.num_batters = 5
    if "num_bat_ar" not in st.session_state:
        st.session_state.num_bat_ar = 2

    def on_batters_change():
        # When batters change, update max for batting allrounders if total > max_total
        total = st.session_state.num_batters + st.session_state.num_bat_ar
        if total > max_total:
            st.session_state.num_bat_ar = max_total - st.session_state.num_batters
            if st.session_state.num_bat_ar < 0:
                st.session_state.num_bat_ar = 0

    def on_bat_ar_change():
        # Batting allrounders change - no backward adjustment needed since batters fixed first
        pass

    # Number of Batsmen input first
    batsman = role_counts.get("Batsman", 0)
    wicketkeeper = role_counts.get("Wicketkeeper", 0)
    num_batters= batsman + wicketkeeper
    
    # Batting Allrounders input second, max depends on batters
    spinner_batting_allrounders=role_counts.get("Batting Allrounder Spinner", 0)
    pacer_batting_allrounders=role_counts.get("Batting Allrounder Pacer", 0)
    num_bat_ar = spinner_batting_allrounders+pacer_batting_allrounders

    # Bowling Roles - Spinners
    spinner_pure =role_counts.get("Spinner", 0)
    spinner_bowl_ar = role_counts.get("Bowling Allrounder Spinner", 0)+ role_counts.get("Bowling Allrounder Pacer", 0)


    # Bowling Roles - Pacers
    pacer_pure = role_counts.get("Pacer", 0) 
    pacer_bowl_ar = 0
    
    if "button_clicked" not in st.session_state:
        st.session_state["button_clicked"] = False

    if st.sidebar.button("Confirm Configuration"):
        total_players = num_batters + num_bat_ar + spinner_pure + spinner_bowl_ar + pacer_pure
        st.session_state["button_clicked"] = True

        if total_players == 11:
            st.sidebar.markdown(f"""<div style="line-height: 0.6;">&nbsp;</div>
                <div class="confirm-msg">
                ✅ Team composition confirmed! Total players: {total_players}
                </div>
                """, unsafe_allow_html=True)
            st.session_state.show_xi = True
            # 🔍 Display Predicted Role Counts
            
            st.sidebar.markdown("### 📊 Predicted Role Counts")
            st.sidebar.write(f"**Batsman**: {num_batters} (including Wicket Keepers)")
            for role, count in role_counts.items():
                if role not in ["Batsman", "Wicketkeeper"]:
                    st.sidebar.write(f"**{role}**: {count}")
        else:
            st.sidebar.markdown(f"""<div style="line-height: 0.6;">&nbsp;</div>
                <div class="warning-msg">
                ⚠️ Please select exactly 11 players. Currently selected: {total_players}
                </div>
                """, unsafe_allow_html=True)
            st.session_state.show_xi = False

    if not st.session_state["button_clicked"]:
        st.sidebar.markdown(f"""<div style="line-height: 0.6;">&nbsp;</div>
            <div class="info-msg">
            🔔 Please click <strong>Confirm Configuration</strong> after making changes to see the Predicted Role Counts.
            </div>
            """, unsafe_allow_html=True)

    # Final match context dictionary
    match_context = {
        "Tournament_Type": tournament_type,
        "Opponent": selected_opponent,
        "Ground": home_away,
        "Pitch_Type": pitch_type,
        "Clutch": is_clutch,
        "Unavailable": unavailable_players,
        "Team_Combo": {
            "Batters": num_batters,
            "Batting_AR": num_bat_ar,  # <== Must be exactly this
            "Spinner_Pure": spinner_pure,
            "Spinner_Bowling_AR": spinner_bowl_ar,
            "Pacer_Pure": pacer_pure
        }
    }
    return match_context