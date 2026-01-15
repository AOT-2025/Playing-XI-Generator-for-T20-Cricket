import json
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import LabelEncoder

# Load match data
def load_match_data():
    with open("team_composition_updated_new.json") as f:
        return json.load(f)

# Prepare dataset
def prepare_dataset(match_data):
    rows = []
    for match in match_data:
        if match.get("Result", "").lower() != "win":
            continue
        row = {
            "Match_No": match.get("Match_No"),
            "Opponent": match.get("Opponent"),
            "Pitch_Type": match.get("Pitch_Type"),
            "HomeAway": match.get("HomeAway"),
            "Venue": match.get("Venue"),
            "Team_Rank": match.get("Team_Rank", 10)
        }
        comp = match.get("Team_Composition", {})
        for role, count in comp.items():
            row[role] = count
        rows.append(row)

    df = pd.DataFrame(rows)
    df["Rank_Tier"] = pd.cut(df["Team_Rank"], bins=[0, 3, 7, 11], labels=["Top", "Mid", "Low"])
    role_cols = [col for col in df.columns if col not in ['Match_No', 'Opponent', 'Pitch_Type', 'HomeAway', 'Venue', 'Team_Rank', 'Rank_Tier']]
    df[role_cols] = df[role_cols].fillna(0).astype(int)
    df = df.dropna(subset=["Opponent", "Pitch_Type", "HomeAway", "Rank_Tier"])

    return df, role_cols

# Train fallback ML model
def train_ml_model(df, role_cols):
    le_opponent = LabelEncoder()
    le_pitch = LabelEncoder()
    le_homeaway = LabelEncoder()
    le_rank = LabelEncoder()

    X_cat = pd.DataFrame({
        "Opponent": le_opponent.fit_transform(df["Opponent"]),
        "Pitch_Type": le_pitch.fit_transform(df["Pitch_Type"]),
        "HomeAway": le_homeaway.fit_transform(df["HomeAway"]),
        "Rank_Tier": le_rank.fit_transform(df["Rank_Tier"])
    })

    y = df[role_cols]
    model = MultiOutputRegressor(lgb.LGBMRegressor(random_state=42))
    model.fit(X_cat, y)

    return model, (le_opponent, le_pitch, le_homeaway, le_rank)

# Main callable function
def get_predicted_role_counts(pitch, homeaway, rank_tier, opponent=None):
    match_data = load_match_data()
    df, role_cols = prepare_dataset(match_data)

    # Build composition map
    composition_map = {}
    for _, row in df.iterrows():
        key = (row["Pitch_Type"], row["HomeAway"], row["Rank_Tier"], row["Opponent"])
        composition_map[key] = {role: row[role] for role in role_cols}

    input_context = (pitch, homeaway, rank_tier, opponent)

    def context_similarity(ctx1, ctx2):
        # If opponent is None, compare only first 3 fields
        if ctx1[3] is None:
            return sum(1 for a, b in zip(ctx1[:3], ctx2[:3]) if a == b)
        else:
            return sum(1 for a, b in zip(ctx1, ctx2) if a == b)

    # Find best match in historical data
    best_match = None
    best_score = -1
    for ctx, comp in composition_map.items():
        score = context_similarity(input_context, ctx)
        if score > best_score:
            best_score = score
            best_match = (ctx, comp)

    if best_match and best_score >= 2:
        return best_match[1]

    # ML fallback
    model, encoders = train_ml_model(df, role_cols)
    le_opponent, le_pitch, le_homeaway, le_rank = encoders

    # Get most frequent opponent from dataset
    most_common_opponent = df['Opponent'].mode()[0]

    # Handle missing or unknown opponent
    opponent_for_ml = opponent
    if opponent_for_ml is None or opponent_for_ml not in le_opponent.classes_:
        opponent_for_ml = most_common_opponent

    x_input = pd.DataFrame([{
        "Opponent": le_opponent.transform([opponent_for_ml])[0],
        "Pitch_Type": le_pitch.transform([pitch])[0],
        "HomeAway": le_homeaway.transform([homeaway])[0],
        "Rank_Tier": le_rank.transform([rank_tier])[0]
    }])
    y_pred = model.predict(x_input)[0]
    role_counts = {role: int(round(count)) for role, count in zip(role_cols, y_pred)}
    return role_counts

# Optional: Streamlit UI for testing
if __name__ == "__main__":
    import streamlit as st

    st.set_page_config(page_title="Rule-Based + ML Team Composition Predictor")
    st.title("🏏 Team Composition Predictor + Final XI Generator")

    match_data = load_match_data()
    df, role_cols = prepare_dataset(match_data)
    all_opponents = sorted(df["Opponent"].unique())

    st.subheader("🎯 Select Match Context")
    pitch = st.selectbox("Pitch Type", ["Spin", "Pace"])
    homeaway = st.selectbox("Home/Away", ["Home", "Away"])
    rank_tier = st.selectbox("Rank Tier", ["Top", "Mid", "Low"])
    opponent = st.selectbox("Opponent", [None] + all_opponents)

    predicted_counts = get_predicted_role_counts(pitch, homeaway, rank_tier, opponent)

    st.subheader("🧮 Predicted Role Counts")
    st.json(predicted_counts)