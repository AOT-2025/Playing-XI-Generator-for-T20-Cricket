import streamlit as st
import pandas as pd
import numpy as np

def custom_normalize(x, min_x, max_x, L=0.1, U=1):
    return (U - L) * (x - min_x) / (max_x - min_x) + L if max_x != min_x else L

def compute_statistical_score(df, match_context):
    factors = []

    if match_context['Unavailable']:
        df = df[~df['Player Name'].isin(match_context['Unavailable'])]

    if match_context["Tournament_Type"] == "Series":
        factors += ["Final_Opponent_Score_Recent", "Opponent_Overall_Final_Batting_Score", "Final_Position_Batting_Score"]
    else:
        unique_pos_opp = df.groupby(["Player ID", "Position", "Opponent"])["Final_Position_Batting_Score"].mean().reset_index()
        median_position_score = unique_pos_opp.groupby(["Player ID", "Position"])["Final_Position_Batting_Score"].median().reset_index()
        median_position_score.rename(columns={"Final_Position_Batting_Score": "Overall_Position_Median"}, inplace=True)
        df = df.merge(median_position_score, on=["Player ID", "Position"], how="left")
        df["Final_Position_Batting_Score"] = df["Overall_Position_Median"]
        df.drop(columns=["Overall_Position_Median"], inplace=True)
        df["Final_Opponent_Score_Recent"] = df["Final_Opponent_Score_Recent"].fillna(df["Final_Opponent_Score_Recent"].median())
        df["Opponent_Overall_Final_Batting_Score"] = df["Opponent_Overall_Final_Batting_Score"].fillna(df["Opponent_Overall_Final_Batting_Score"].median())
        factors += ["Final_Opponent_Score_Recent", "Opponent_Overall_Final_Batting_Score", "Final_Position_Batting_Score"]

    if match_context["Pitch_Type"] == "Spin":
        factors.append("Final_Score_Spin")
    else:
        factors.append("Final_Score_Pace")

    if match_context["Ground"] == "Home":
        factors.append("Final_Home_Batting_Score")
    else:
        factors.append("Final_Away_Batting_Score")

    if match_context["Clutch"]:
        factors += ["Powerplay_Score", "Middle_Over_Score", "Death_Over_Score"]

    factors += ["Final_Batsman_Overall_score"]

    for col in factors:
        min_val, max_val = df[col].min(), df[col].max()
        df[f"Norm_{col}"] = df[col].apply(lambda x: custom_normalize(x, min_val, max_val))

    var_dict = {col: df[f"Norm_{col}"].var() for col in factors}
    C_k = 1 / sum(1 / np.sqrt(v) for v in var_dict.values() if v > 0)
    weights = {col: C_k / np.sqrt(v) if v > 0 else 0 for col, v in var_dict.items()}

    # Adjust weights if Series mode and opponent provided
    if match_context["Tournament_Type"] == "Series" and match_context["Opponent"]:
        team_rank_df = pd.read_csv("TeamID.csv")
        opponent_rank = team_rank_df.loc[team_rank_df["Team"] == match_context["Opponent"], "Team_Rank"].values[0]

        # Calculate dynamic opponent weight
        raw_strength = 1 / (opponent_rank + 1e-5)
        strength_scale = np.interp(raw_strength, [1/10, 1/1], [0.5, 2.0])  # map inverse rank to scale range

        for col in weights:
            if col in ["Final_Opponent_Score_Recent", "Opponent_Overall_Final_Batting_Score"]:
                weights[col] *= strength_scale

    df["True_Final_Score"] = sum(weights[col] * df[f"Norm_{col}"] for col in factors)
    return df, weights, factors

def run_statistical_score_calc(match_context):
    score_df = pd.read_csv("Batting_Scores.csv")
    final_df, final_weights, used_factors = compute_statistical_score(score_df.copy(), match_context)

    valid_roles = ["Batsman", "WK-Batsman", "Batting Allrounder"]
    valid_players = pd.read_csv("Players.csv")
    final_df = final_df[final_df["Player Name"].isin(valid_players[valid_players["Role"].isin(valid_roles)]["Player Name"])]

    return final_df, final_weights, used_factors

def get_feature_target_from_final(final_df, used_factors):
    target_column = "True_Final_Score"
    mlp_feature_df = final_df.copy()
    mlp_feature_df = mlp_feature_df[used_factors + [target_column, "Player Name", "Role", "Position"]].dropna()
    X = mlp_feature_df[used_factors]
    y = mlp_feature_df[target_column]
    return X, y, mlp_feature_df

def run_statistical_bowling_score_calc(match_context):
    df = pd.read_csv("Bowler_final_score.csv")

    factors = []
    if match_context['Unavailable']:
        df = df[~df['Player Name'].isin(match_context['Unavailable'])]

    if match_context["Tournament_Type"] == "Series" and match_context["Opponent"]:
        df = df[df["Opponent"] == match_context["Opponent"]]
        factors += ["Opponent_Bowl_Score"]
    else:
        df["Opponent_Bowl_Score"] = df["Opponent_Bowl_Score"].fillna(df["Opponent_Bowl_Score"].median())
        factors += ["Opponent_Bowl_Score"]

    if match_context["Ground"] == "Home":
        factors.append("Home_Score")
    else:
        factors.append("Away_Score")

    if match_context["Clutch"]:
        factors += ["Powerplay_score", "Middle_Over_score", "Death_Over_score"]

    factors += ["Overall_Bowling_Score"]

    for col in factors:
        min_val, max_val = df[col].min(), df[col].max()
        df[f"Norm_{col}"] = df[col].apply(lambda x: (x - min_val) / (max_val - min_val) if max_val != min_val else 0.5)

    var_dict = {col: df[f"Norm_{col}"].var() for col in factors}
    C_k = 1 / sum(1 / np.sqrt(v) for v in var_dict.values() if v > 0)
    weights = {col: C_k / np.sqrt(v) if v > 0 else 0 for col, v in var_dict.items()}

    df["True_Final_Bowl_Score"] = sum(weights[col] * df[f"Norm_{col}"] for col in factors)
    valid_roles = ["Pacer", "Spinner", "Bowling Allrounder (Spinner)"]
    valid_players = pd.read_csv("Players.csv")

    # # Filter to include those who are either pacers/spinners or have the role "Bowling Allrounder"
    # valid_roles = valid_players[valid_players["Role"] == "Bowling Allrounder"]["Player Name"].tolist()

    # # Filter final bowlers
    # valid_bowlers = df[
    #     (df["Bowler_Type"].isin(["Pacer", "Spinner"])) | (df["Player Name"].isin(valid_roles))
    # ].copy()

    valid_bowlers = df[df["Player Name"].isin(valid_players[valid_players["Role"].isin(valid_roles)]["Player Name"])]
    # st.dataframe(valid_bowlers)
    return valid_bowlers, weights, factors

def get_bowling_feature_target(final_df, used_factors):
    target_column = "True_Final_Bowl_Score"
    mlp_feature_df = final_df.copy()
    mlp_feature_df = mlp_feature_df[used_factors + [target_column, "Player Name", "Position", "Role"]].dropna()
    X = mlp_feature_df[used_factors]
    y = mlp_feature_df[target_column]
    return X, y, mlp_feature_df