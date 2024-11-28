# ---------------
# --- IMPORTS ---
# ---------------
import pandas as pd
import json
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px

# ----------------
# --- SELECTOR ---
# ----------------


df_stations_carrefour = st.session_state.df_stations_carrefour.sort_values(by="Ville")
df_stations_others = st.session_state.df_stations_others.sort_values(by="Ville")
df_prix = st.session_state.df_prix
df_prix = df_prix.rename(columns={"id": "ID"})

# Load concurrents json file
with open("data/processed/Concurrents.json", "r") as f:
    concurrents_json = json.load(f)

# Date input
if "selected_date" not in st.session_state:
    st.session_state.selected_date = st.date_input(
        "Select a date",
        value=df_prix["Date"].max(),
        min_value=df_prix["Date"].min(),
        max_value=df_prix["Date"].max(),
        key="initial_date_input",
    )
else:
    st.session_state.selected_date = st.date_input(
        "Select a date",
        value=st.session_state.selected_date,
        min_value=df_prix["Date"].min(),
        max_value=df_prix["Date"].max(),
        key="initial_date_input",
    )

# Create a list of concatenated strings for the selectbox
station_options = [
    f"{row['Adresse']}, {row['Ville']} (ID: {row['ID']})"
    for index, row in df_stations_carrefour.iterrows()
]

# Create a mapping from the concatenated string back to the ID
station_id_mapping = df_stations_carrefour["ID"].values

# If the selected station is not in session state, initialize it
if "selected_station" not in st.session_state:
    selected_station_index = st.selectbox(
        "Select a station",
        station_options,
    )
    # Store the selected ID in session state
    st.session_state.selected_station = station_id_mapping[
        station_options.index(selected_station_index)
    ]
else:
    selected_station_index = st.selectbox(
        "Select a station",
        station_options,
        index=station_options.index(
            f"{df_stations_carrefour[df_stations_carrefour['ID'] == st.session_state.selected_station]['Adresse'].values[0]}, {df_stations_carrefour[df_stations_carrefour['ID'] == st.session_state.selected_station]['Ville'].values[0]} (ID: {st.session_state.selected_station})"
        ),
    )
    # Update the selected station ID in session state
    st.session_state.selected_station = station_id_mapping[
        station_options.index(selected_station_index)
    ]

# -----------
# --- MAP ---
# -----------


# Get selected station details
selected_station_row = df_stations_carrefour[
    df_stations_carrefour["ID"] == st.session_state.selected_station
].iloc[0]
selected_lat = selected_station_row["Latitude"]
selected_lon = selected_station_row["Longitude"]

# Create a Folium map centered on the selected station
m = folium.Map(location=[selected_lat, selected_lon], zoom_start=12)

# Add a red marker for the selected station
folium.Marker(
    location=[selected_lat, selected_lon],
    popup=f"<b>{selected_station_row['Adresse']}</b><br>{selected_station_row['Ville']}",
    icon=folium.Icon(color="red"),
).add_to(m)

# -----------------------
# --- ADD CONCURRENTS ---
# -----------------------

# Extract the concurrents ids list from json
concurrents_ids = concurrents_json[str(st.session_state.selected_station)]

# Add blue markers for concurrents
for concurrent_id in concurrents_ids:
    concurrent_row = df_stations_others[df_stations_others["ID"] == concurrent_id].iloc[
        0
    ]
    concurrent_lat = concurrent_row["Latitude"]
    concurrent_lon = concurrent_row["Longitude"]
    folium.Marker(
        location=[concurrent_lat, concurrent_lon],
        popup=f"<b>{concurrent_row['Enseignes']}</b><br><br>{concurrent_row['Adresse']}<br>{concurrent_row['Ville']}",
        icon=folium.Icon(color="blue"),
    ).add_to(m)

# Display the map
st_folium(m, width="100%", height=600)

# ------------------------
# --- PRICE COMPARATOR ---
# ------------------------

# Create a dataframe with selected one and concurrents
df_selected_station = df_prix[
    (df_prix["ID"] == int(st.session_state.selected_station))
    & (df_prix["Date"] == st.session_state.selected_date)
]

df_selected_station["Enseignes"] = "carrefour"

# List to hold dataframes
dfs = [df_selected_station]

for id in concurrents_ids:
    df_concurrent = df_prix[
        (df_prix["ID"] == int(id)) & (df_prix["Date"] == st.session_state.selected_date)
    ]
    if not df_concurrent.empty:
        df_concurrent["Enseignes"] = df_stations_others[df_stations_others["ID"] == id][
            "Enseignes"
        ].values[0]
        dfs.append(df_concurrent)

# Concatenate all dataframes
df_combined = pd.concat(dfs, ignore_index=True)

# Replace 0 values with NaN
df_combined = df_combined.replace(0, pd.NA)

# Remove ID and Date columns
df_combined = df_combined.drop(columns=["ID", "Date"])

# Set "Enseignes" to be the first column
cols = df_combined.columns.tolist()
cols = cols[-1:] + cols[:-1]
df_combined = df_combined[cols]


# Function to highlight the carrefour row
def highlight_selected_row(row):
    if row["Enseignes"] == "carrefour":
        return ["background-color: #5ce75c; color: black"] * len(row)
    return [""] * len(row)


styled_df = df_combined.style.apply(highlight_selected_row, axis=1)

st.dataframe(styled_df, use_container_width=True)

# ------------------
# --- LINE CHART ---
# ------------------

col1, col2 = st.columns(2)

with col1:
    # Date input
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = st.date_input(
            "Select a start date",
            value=df_prix["Date"].max(),
            min_value=df_prix["Date"].min(),
            max_value=df_prix["Date"].max(),
            key="subsequent_date_input",
        )
    else:
        st.session_state.selected_date = st.date_input(
            "Select a start date",
            value=st.session_state.selected_date,
            min_value=df_prix["Date"].min(),
            max_value=df_prix["Date"].max(),
            key="subsequent_date_input",
        )

with col2:
    # Date input
    if "selected_date_end" not in st.session_state:
        st.session_state.selected_date_end = st.date_input(
            "Select a end date",
            value=st.session_state.selected_date,
            min_value=st.session_state.selected_date,
            max_value=df_prix["Date"].max(),
            key="subsequent_date_input_end",
        )
    else:
        st.session_state.selected_date_end = st.date_input(
            "Select a end date",
            value=st.session_state.selected_date_end,
            min_value=st.session_state.selected_date,
            max_value=df_prix["Date"].max(),
            key="subsequent_date_input_end",
        )

# Prepare df

df_selected_station_line = df_prix[
    (df_prix["ID"] == int(st.session_state.selected_station))
    & (df_prix["Date"] >= st.session_state.selected_date)
    & (df_prix["Date"] <= st.session_state.selected_date_end)
]

df_selected_station_line["Enseignes"] = "carrefour"

dfs_line = [df_selected_station_line]

for id in concurrents_ids:
    df_concurrent = df_prix[
        (df_prix["ID"] == int(id))
        & (df_prix["Date"] >= st.session_state.selected_date)
        & (df_prix["Date"] <= st.session_state.selected_date_end)
    ]
    if not df_concurrent.empty:
        df_concurrent["Enseignes"] = df_stations_others[df_stations_others["ID"] == id][
            "Enseignes"
        ].values[0]
        dfs_line.append(df_concurrent)

# Concatenate all dataframes

df_combined_line = pd.concat(dfs_line, ignore_index=True)

# Extract a df with only the selected carburant
carburant = st.selectbox(
    "Select a fuel type", ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
)

fig = px.line(
    df_combined_line,
    x="Date",
    y=carburant,
    color="Enseignes",
    line_group="ID",
    hover_name="Enseignes",
    color_discrete_sequence=px.colors.sequential.Viridis,
    markers=True,
)

st.plotly_chart(fig)
