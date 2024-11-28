# ---------------
# --- IMPORTS ---
# ---------------

import datetime
import json
import math
from pathlib import Path
import streamlit as st
import pandas as pd


# ------------------------
# --- DATA PREPARATION ---
# ------------------------

# Load data

df_stations = pd.read_csv(Path.cwd() / "data" / "origin" / "Infos_Stations.csv")
df_prix = pd.read_csv(Path.cwd() / "data" / "processed" / "Prix_2_weeks.csv")

# Remove NaN values

df_stations.dropna(inplace=True)
df_prix.dropna(inplace=True)

# Convert date column to datetime

df_prix["Date"] = pd.to_datetime(df_prix["Date"], format="%Y-%m-%d").dt.date

# --- Fix "Enseignes" column ---

# Lower case Enseignes
df_stations["Enseignes"] = df_stations["Enseignes"].str.lower()

# Order alphabetically by enseignes
df_stations = df_stations.sort_values(by="Enseignes")

# Normalize enseignes names
df_stations["Enseignes"] = (
    df_stations["Enseignes"]
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
)


# Regroup names referring to the same enseigne
def regroup_enseignes(df, pattern, new_name):
    df["Enseignes"] = df["Enseignes"].replace(
        to_replace=pattern, value=new_name, regex=True
    )
    return df


operationsList = [
    [r".*carrefour.*", "carrefour"],
    [r".*casino.*", "casino"],
    [r".*geant.*", "casino"],
    [r".*leclerc.*", "leclerc"],
    [r".*8.*", "8 a huit"],
    [r".*aire-c*", "airec"],
    [r".*aire c*", "airec"],
    [r".*esso.*", "esso"],
    [r".*g20.*", "g20"],
    [r".* u.*", "systeme u"],
    [r".*u .*", "systeme u"],
    [r".*total .*", "totalenergies"],
    [r".*spar.*", "spar"],
    [r".*simply.*", "simply"],
    [r".*intermarche.*", "intermarche"],
    # excluded
    [r".*indapendant.*", "excluded"],
    [r".*independant.*", "excluded"],
    [r".*inconnu.*", "excluded"],
    [r".*pas de marque.*", "excluded"],
    [r".*sans enseigne.*", "excluded"],
    [r".*sans marque.*", "excluded"],
    [r".*station commun.*", "excluded"],
    [r".*aucune.*", "excluded"],
    [r".*autre.*", "excluded"],
]

for operation in operationsList:
    df_stations = regroup_enseignes(df_stations, operation[0], operation[1])

# Order alphabetically by enseignes again
df_stations = df_stations.sort_values(by="Enseignes")

# Exclude rows with enseignes to be excluded
df_stations = df_stations[df_stations["Enseignes"] != "excluded"]

# Keep only road stations
df_stations = df_stations[df_stations["Type"] == "R"]

# We keep only the "enseignes" having more than 100 stations

enseignes = df_stations["Enseignes"].value_counts()
enseignes = enseignes[enseignes > 100].index.tolist()

df_stations = df_stations[df_stations["Enseignes"].isin(enseignes)]

# Replace outliers Q1 and Q3 in price df


def replace_outliers(df, col_name, q1, q3):
    df.loc[(df[col_name] < q1) & (df[col_name] != 0), col_name] = q1
    df.loc[df[col_name] > q3, col_name] = q3
    return df


columnsList = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]

for column in columnsList:
    q1 = df_prix[df_prix[column] != 0][column].quantile(0.25)
    q3 = df_prix[df_prix[column] != 0][column].quantile(0.75)
    df_prix = replace_outliers(df_prix, column, q1, q3)

# ------------------------------
# --- EXTRACT CARREFOUR DATA ---
# ------------------------------

df_stations_carrefour = df_stations[df_stations["Enseignes"] == "carrefour"]
df_stations_others = df_stations[df_stations["Enseignes"] != "carrefour"]

# Download as CSV

df_stations_carrefour.to_csv(Path.cwd() / "data" / "processed" / "Carrefour.csv")
df_stations_others.to_csv(Path.cwd() / "data" / "processed" / "Concurrents.csv")

# ---------------------------
# --- NEAREST CONCCURENTS ---
# ---------------------------

# For each Carrefour station, we find every concurrent station in a 10km radius


def haversine(lat1, lon1, lat2, lon2):
    # Convertir les degrés en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Rayon moyen de la Terre en kilomètres
    R = 6371.0
    # Différences de coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Formule de Haversine
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Distance en kilomètres
    distance = R * c
    return distance


df_stations_carrefour["ID"] = df_stations_carrefour["ID"].apply(str)
df_stations_others["ID"] = df_stations_others["ID"].apply(str)

df_stations_carrefour["Latitude"] = (
    df_stations_carrefour["Latitude"].apply(float) / 100000
)
df_stations_carrefour["Longitude"] = (
    df_stations_carrefour["Longitude"].apply(float) / 100000
)

df_stations_others["Latitude"] = df_stations_others["Latitude"].apply(float) / 100000
df_stations_others["Longitude"] = df_stations_others["Longitude"].apply(float) / 100000

D1 = {
    df_stations_others.loc[id, "ID"]: (
        df_stations_others.loc[id, "Latitude"],
        df_stations_others.loc[id, "Longitude"],
    )
    for id in df_stations_others.index
}

D2 = {
    df_stations_carrefour.loc[id, "ID"]: (
        df_stations_carrefour.loc[id, "Latitude"],
        df_stations_carrefour.loc[id, "Longitude"],
    )
    for id in df_stations_carrefour.index
}

D = dict()


def list_concurrents(id):
    L_conc = list()
    for x in D1:
        d = haversine(D2[id][0], D2[id][1], D1[x][0], D1[x][1])
        if d <= 10:
            L_conc.append(x)
    return L_conc


# # We create a dictionary with the Carrefour stations id as keys and the concurrent stations ids as values

# D = {id: list_concurrents(id) for id in D2}


# # And we save it as a JSON file

# with open(Path.cwd() / "data" / "processed" / "Concurrents.json", "w") as f:
#     json.dump(D, f)

# ---------------------
# --- STREAMLIT APP ---
# ---------------------

st.set_page_config(
    page_title="Gas explorer", page_icon=":material/edit:", layout="wide"
)

# Push variables to session state
st.session_state.df_stations = df_stations
st.session_state.df_prix = df_prix
st.session_state.df_stations_carrefour = df_stations_carrefour
st.session_state.df_stations_others = df_stations_others


kpis_page = st.Page("pages/kpi.py", title="KPIs", icon=":material/heap_snapshot_large:")
map_page = st.Page("pages/map.py", title="Map", icon=":material/pin_drop:")

pg = st.navigation([kpis_page, map_page])

with st.sidebar:
    st.title("Fuel price explorator")
    st.image(
        "https://avatars.githubusercontent.com/u/64584150?s=400&u=e110967fbf6e30094c813414eaa60770b4cd8e25&v=4",
        width=350,
    )
    # border radius image using css
    st.markdown(
        "<style>img{border-radius: 50%;}h1{text-align:center; font-size:2em!important; font-weight:bold!important;}</style>",
        unsafe_allow_html=True,
    )

pg.run()
