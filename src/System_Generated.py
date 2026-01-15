import sys
import streamlit as st
import numpy as np
import pandas as pd
import io
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from context_sidebar_system_generated import get_match_context
from statistical_score_calc import run_statistical_score_calc, get_feature_target_from_final
from statistical_score_calc import run_statistical_bowling_score_calc, get_bowling_feature_target
from mlp_trainer import train_mlp
from reliability_adjuster import select_most_reliable_batters, select_dynamic_reliable_batters, select_dynamic_bowlers_assignment


try:
    # Page config
    st.set_page_config(
        page_title="System Generated",
        page_icon="🏏",
        layout="centered"
    )
    from stylesheet import apply_custom_style2
    apply_custom_style2()
    # Load base data
    players_df = pd.read_csv("Players.csv")
    teams_df = pd.read_csv("TeamID.csv")
    fielding_df = pd.read_csv("Fielding_Scores.csv")
    # Always show the sidebar
    match_context = get_match_context(players_df, teams_df)

    # Step 1: Run statistical score calculation
    final_df, final_weights, used_factors = run_statistical_score_calc(match_context)

    # Step 2: Visualize statistical calculations
    with st.expander("See Batting Prediction Process and Results"):
        st.subheader("\U0001F4C8 Statistical Score Calculation Breakdown")

        st.markdown("#### \U0001F4CA Feature Weights (Inverse-Variance Based)")
        weights_df = pd.DataFrame({
            "Feature": list(final_weights.keys()),
            "Weight": list(final_weights.values())
        }).sort_values(by="Weight", ascending=False)

        st.dataframe(weights_df.style.format({"Weight": "{:.6f}"}))

        norm_cols = [f"Norm_{col}" for col in used_factors]
        top_stat_df = final_df.sort_values("True_Final_Score", ascending=False)[["Player Name", "True_Final_Score"] + norm_cols].drop_duplicates("Player Name")

        st.markdown("#### \U0001F4C1 Top 10 Players by True Final Score")
        st.dataframe(top_stat_df[["Player Name", "True_Final_Score"]].head(10).reset_index(drop=True))

        # Step 3: Global importance (optional)
        def iyengar_sudarsan_weights(X_np):
            means = np.mean(X_np, axis=0)
            stds = np.std(X_np, axis=0)
            epsilon = 1e-8
            return means / (stds + epsilon)


    # Step 4: Position-specific batting prediction
        st.subheader("Top 5 Players Per Batting Position (Position-Specific MLP)")
        tournament_type = match_context["Tournament_Type"]
        position_dfs = {}

        for pos in range(1, 8):
            pos_df = final_df[final_df["Position"] == pos]
            X_pos, y_pos, mlp_pos_df = get_feature_target_from_final(pos_df, used_factors)
            X_pos_np = X_pos.to_numpy(dtype=np.float32)
            y_pos_np = y_pos.to_numpy(dtype=np.float32).reshape(-1, 1)

            iw_pos = iyengar_sudarsan_weights(X_pos_np)
            pos_preds = train_mlp(X_pos_np, y_pos_np, iw_pos)
            mlp_pos_df["Predicted_Score"] = pos_preds

            if tournament_type == "ICC":
                grouped = mlp_pos_df.groupby(["Player Name", "Position"]).agg({
                    "Predicted_Score": "median",
                    "Role": "first"
                }).reset_index()
            else:
                grouped = mlp_pos_df.sort_values("Predicted_Score", ascending=False).drop_duplicates("Player Name")

            top_5 = grouped.sort_values("Predicted_Score", ascending=False).head(5).reset_index(drop=True)
            position_dfs[f"Position_{pos}"] = grouped

            st.markdown(f"### \U0001F3CF Position {pos}")
            st.dataframe(top_5[["Player Name", "Role", "Predicted_Score"]])


        # Step 6: Most Reliable Batters by Position
        innings_df = pd.read_csv("Batting_Scores.csv")
        roles_df = pd.read_csv("Players.csv")
        final_df_with_preds = pd.concat(position_dfs.values(), ignore_index=True)
        #select_most_reliable_batters(final_df_with_preds, roles_df, innings_df)

        # st.dataframe(final_df_with_preds)
        # st.dataframe(roles_df)
        # st.dataframe(bowl_feature_df)

        # Step 6: Most Reliable Batters by Position (with Rank Info)
        innings_df = pd.read_csv("Batting_Scores.csv")
        roles_df = pd.read_csv("Players.csv")
        final_df_with_preds = pd.concat(position_dfs.values(), ignore_index=True)
        # # Assuming bowlers_df is already defined
        # st.write(bowl_feature_df.columns.tolist())

        # This now returns both the selected 7 batters and their rank info
        from reliability_adjuster import select_most_reliable_batters
        best_7_batters_df, _ = select_most_reliable_batters(final_df_with_preds, roles_df, innings_df)

        final_batters = select_dynamic_reliable_batters(
            final_df_with_preds,  # The merged df with predicted scores
            roles_df,
            innings_df,
            match_context,
            fielding_df
        )

    with st.expander("See Bowling Prediction Process and Results"):
        # Step 5: Bowler prediction
        #st.subheader("\U0001F3AF Bowler Score Prediction and Visualization")
        bowl_df, bowl_weights, bowl_factors = run_statistical_bowling_score_calc(match_context)
        st.subheader("\U0001F4C8 Statistical Score Calculation Breakdown")
        st.subheader("\U0001F4CA Feature Weights (Inverse-Variance Based)")
        bowl_weight_df = pd.DataFrame({
            "Feature": list(bowl_weights.keys()),
            "Weight": list(bowl_weights.values())
        }).sort_values(by="Weight", ascending=False)
        st.dataframe(bowl_weight_df.style.format({"Weight": "{:.6f}"}))

        st.subheader("\U0001F3AF Bowler Score Prediction and Visualization")
        X_bowl, y_bowl, bowl_feature_df = get_bowling_feature_target(bowl_df, bowl_factors)
        X_bowl_np = X_bowl.to_numpy(dtype=np.float32)
        y_bowl_np = y_bowl.to_numpy(dtype=np.float32).reshape(-1, 1)

        bowl_weights_mlp = iyengar_sudarsan_weights(X_bowl_np)
        bowl_preds = train_mlp(X_bowl_np, y_bowl_np, bowl_weights_mlp)
        bowl_feature_df["Predicted_Bowl_Score"] = bowl_preds

        st.dataframe(bowl_feature_df)
        st.subheader("\U0001F3C6 Top Paces, Spinners and Bowling All-rounders")
        for btype in ["Pacer", "Spinner", "Bowling Allrounder (Spinner)"]:
            st.markdown(f"### \u26BE {btype}s")
            sub_df = bowl_feature_df[bowl_feature_df["Role"] == btype]
            sub_df = sub_df.sort_values("Predicted_Bowl_Score", ascending=False).drop_duplicates("Player Name")
            st.dataframe(sub_df[["Player Name", "Role", "Position", "Predicted_Bowl_Score"]].head(5).reset_index(drop=True))



        used_positions = set(final_batters["Position"])
        used_players = set(final_batters["Player Name"])

        final_bowlers = select_dynamic_bowlers_assignment(
            bowlers_df=bowl_feature_df,
            innings_df=innings_df,
            fielding_df=fielding_df,
            match_context=match_context,
            used_positions=used_positions,
            used_players=used_players
        )

    # Combine batters and bowlers
    selected_players_df = pd.concat([
        final_batters[["Player Name", "Role", "Position"]],
        final_bowlers[["Player Name", "Role", "Position"]]
    ])

    # Sort by Position
    selected_players_df = selected_players_df.sort_values(by="Position").reset_index(drop=True)

    combo = match_context["Team_Combo"]

    total_players = (
        combo["Batters"] +
        combo["Batting_AR"] +
        combo["Spinner_Pure"] +
        combo["Spinner_Bowling_AR"] +
        combo["Pacer_Pure"]
    )

    if total_players != len(selected_players_df):
        st.markdown(
        """
        <div style="font-size:24px; color:#006d77; font-weight:600; padding:8px 12px;">
            Sorry! Due to limitations in the dataset, we're unable to generate a complete playing XI.
        <br></div>""",
        unsafe_allow_html=True)
        st.write(f"""<div style="line-height: 0.1;">&nbsp;</div>
                        """, unsafe_allow_html=True)
        styled_table = selected_players_df.style\
            .hide(axis="index")\
            .applymap(lambda _: 'text-align: center; font-weight: 500; color: #1a73e8;', subset=['Position'])\
            .set_table_attributes('class="styled-table"')\
            .to_html()

        st.markdown(styled_table, unsafe_allow_html=True)
    
    else:
        # Sort by Position
        # selected_players_df = selected_players_df.sort_values(by="Position").reset_index(drop=True)

        # Display in Streamlit
        st.subheader("✅ Final Selected Playing XI")
        st.write(f"""<div style="line-height: 0.4;">&nbsp;</div>
                        """, unsafe_allow_html=True)
        styled_table = selected_players_df.style\
            .hide(axis="index")\
            .applymap(lambda _: 'text-align: center; font-weight: 500; color: #1a73e8;', subset=['Position'])\
            .set_table_attributes('class="styled-table"')\
            .to_html()

        st.markdown(styled_table, unsafe_allow_html=True)
except Exception as e:
    st.markdown(
        """
        <div style="font-size:24px; color:#006d77; font-weight:600; padding:8px 12px;">
            ⚠️ Sorry! We encountered an issue and couldn't complete your request.  
    <br><br>This might be due to limitations in the dataset or unexpected data conditions.  
    Please try adjusting your selections and refresh the page.
        <br></div>""",
        unsafe_allow_html=True)
