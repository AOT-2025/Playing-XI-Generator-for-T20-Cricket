import streamlit as st
import pandas as pd

def get_match_context(players_df, team_df):
    st.sidebar.title("Match Context Configuration")

    # Tournament type & opponent
    tournament_type = st.sidebar.radio("Tournament Type", ["ICC", "Series"])
    selected_opponent = None
    if tournament_type == "Series":
        available_opponents = sorted(team_df['Team'].dropna().unique())
        available_opponents = [team for team in available_opponents if team != "India"]
        selected_opponent = st.sidebar.selectbox("Select Opponent", available_opponents)

    # Ground, pitch, clutch
    home_away = st.sidebar.selectbox("Match Location", ["Home", "Away"])
    pitch_type = st.sidebar.selectbox("Pitch Type", ["Spin", "Pace"])
    is_clutch = st.sidebar.checkbox("Is it a Clutch Match?", value=False)

    # Unavailable players
    st.sidebar.subheader("Team Configuration")
    available_players = players_df['Player Name'].unique()
    unavailable_players = st.sidebar.multiselect("Unavailable Players", available_players)

    # -------------------------------- ADD INSTRUCTION EXPANDER --------------------------------
    
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] details > summary {
        font-size: 24px !important;
        #background: linear-gradient(90deg, #00f0ff 0%, #00bcd4 100%);
        transform: scale(1.03); 
        font-weight: 800 !important;
        color: #00f0ff !important;
        -webkit-text-stroke: 0.7px white;
        text-shadow: 0 0 5px #00f0ff, 0 0 10px #00f0ff !important;
        padding: 12px 20px !important;
        margin: 10px 0 !important;
        border: 0.6px solid white !important;
        border-radius: 12px !important;
        background: rgba(0, 240, 255, 0.15) !important;
        box-shadow: 0 0 15px #00f0ff !important;
        cursor: pointer !important;
        animation: glowPulse 2.5s ease-in-out infinite !important;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }
}
    </style>
""", unsafe_allow_html=True)
    st.sidebar.markdown(f"""<div style="line-height: 2.7;">&nbsp;</div>
            """, unsafe_allow_html=True)
    with st.sidebar.expander('🧩 Team Composition Guidelines'):
        st.markdown("""
        
                    
        To build a context-aware, match-ready XI, please follow the structured role-based guidelines when selecting the number of players per role. The system uses this information to form an optimal playing XI that balances batting depth, bowling variety, and role suitability.

        ### 🔢 Batting Positions (1–7):
        These positions are reserved for top-order and middle-order batting roles.

        ✅ Include only:
        - Batters  
        - Batting Allrounders  
        - Bowling Allrounders


        ⚖️ The total number of batters (including Batting ARs and WK-Batsman) should not exceed 7. Example:  
        3 Batters, 1 WK-Batsman, 2 Batting Allrounders, 1 Bowling Allrounder

        ### 🛡️ Tail Positions (8–11):
        These are reserved primarily for bowlers, focusing on role balance and real-game practicality.

        ✅ Include only:
        - Bowling Allrounders  
        - Pure Bowlers (Pacer or Spinner)

        📌 Bowling Allrounders are preferably placed at positions lower middle order (positions 6-8), allowing added batting depth without compromising bowling strength.

        🚫 Avoid assigning specialist batters or batting ARs to these positions—these are tailender roles meant for players with a primary bowling skillset.

        """)
    st.sidebar.markdown(f"""<div style="line-height: 0.6;">&nbsp;</div>
            <div class="info-msg">
            💡 <strong>Need help?</strong> Feel free to check the <em>Team Composition Guidelines</em> above for useful tips and guidance.
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------- TEAM COMPOSITION INPUTS --------------------------------

    st.sidebar.markdown("---")
    st.sidebar.subheader("Team Composition (11 Players)")

    #Initialization
    if "show_xi" not in st.session_state:
        st.session_state.show_xi = False

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
        total = st.session_state.num_batters + st.session_state.num_bat_ar
        if total > max_total:
            st.session_state.num_bat_ar = max_total - st.session_state.num_batters
            if st.session_state.num_bat_ar < 0:
                st.session_state.num_bat_ar = 0

    def on_bat_ar_change():
        pass  # Placeholder if logic is added later

    num_batters = st.sidebar.number_input(
        "Number of Batsmen (Incl. WK-Batsman)",
        min_value=min_batters,
        max_value=max_total,
        key="num_batters",
        on_change=on_batters_change
    )

    num_bat_ar = st.sidebar.number_input(
        "Number of Batting Allrounders",
        min_value=0,
        max_value=min(max_bat_ar, max_total - st.session_state.num_batters),
        key="num_bat_ar",
        on_change=on_bat_ar_change
    )

    # Bowling Roles - Spinners
    st.sidebar.markdown("### Spinners")
    spinner_pure = st.sidebar.number_input("Pure Spinners", min_value=0, max_value=4, value=1)
    spinner_bowl_ar = st.sidebar.number_input("Spinner Bowling Allrounders", min_value=0, max_value=2, value=1)

    # Bowling Roles - Pacers
    st.sidebar.markdown("### Pacers")
    pacer_pure = st.sidebar.number_input("Pure Pacers", min_value=0, max_value=4, value=2)
    pacer_bowl_ar = st.sidebar.number_input("Pacer Bowling Allrounders", min_value=0, max_value=0, value=0)
    st.sidebar.markdown("<span style='font-size:13px; color:grey;'>⚠️ Pacer bowling all-rounders are not available in the current dataset, so the above option is disabled.</span>", unsafe_allow_html=True)

    st.sidebar.markdown("<span style='font-size:13px; color:grey;'>⚠️ Ensure total players add up to 11.</span>", unsafe_allow_html=True)

    if "button_clicked" not in st.session_state:
        st.session_state["button_clicked"] = False

    if st.sidebar.button("Confirm Selection"):
        total_players = num_batters + num_bat_ar + spinner_pure + spinner_bowl_ar + pacer_pure
        st.session_state["button_clicked"] = True

        if total_players == 11:
            st.sidebar.markdown(f"""<div style="line-height: 0.6;">&nbsp;</div>
                <div class="confirm-msg">
                ✅ Team composition confirmed! Total players: {total_players}
                </div>
                """, unsafe_allow_html=True)
            st.session_state.show_xi = True
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
            🔔 Please click <strong>Confirm Selection</strong> after making changes.
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
            "Batting_AR": num_bat_ar,
            "Spinner_Pure": spinner_pure,
            "Spinner_Bowling_AR": spinner_bowl_ar,
            "Pacer_Pure": pacer_pure
        }
    }
    return match_context
