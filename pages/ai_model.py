# ---------------
# --- IMPORTS ---
# ---------------
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.express as px

df_prix = st.session_state.df_prix
df_prix = df_prix.rename(columns={"id": "ID"})
df_stations = st.session_state.df_stations

# ---------------------
# --- DATE SELECTOR ---
# ---------------------

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
    if "selected_date_end_ai" not in st.session_state:
        st.session_state.selected_date_end_ai = st.date_input(
            "Select a end date",
            value=df_prix["Date"].max() + pd.Timedelta(days=1),
            min_value=df_prix["Date"].max() + pd.Timedelta(days=1),
            key="subsequent_date_input_end",
        )
    else:
        st.session_state.selected_date_end_ai = st.date_input(
            "Select a end date",
            value=st.session_state.selected_date_end_ai,
            min_value=df_prix["Date"].max() + pd.Timedelta(days=1),
            key="subsequent_date_input_end",
        )

# -------------------------------
# --- STATION & FUEL SELECTOR ---
# -------------------------------

# Create a list of concatenated strings for the selectbox
station_options = [
    f"{row['Adresse']}, {row['Ville']} (ID: {row['ID']})"
    for index, row in df_stations.iterrows()
]

# Create a mapping from the concatenated string back to the ID
station_id_mapping = df_stations["ID"].values


col3, col4 = st.columns(2)

with col3:
    # If the selected station is not in session state, initialize it
    if "selected_station_ai" not in st.session_state:
        selected_station_ai_index = st.selectbox(
            "Select a station",
            station_options,
        )
        # Store the selected ID in session state
        st.session_state.selected_station_ai = station_id_mapping[
            station_options.index(selected_station_ai_index)
        ]
    else:
        selected_station_ai_index = st.selectbox(
            "Select a station",
            station_options,
            index=station_options.index(
                f"{df_stations[df_stations['ID'] == st.session_state.selected_station_ai]['Adresse'].values[0]}, {df_stations[df_stations['ID'] == st.session_state.selected_station_ai]['Ville'].values[0]} (ID: {st.session_state.selected_station_ai})"
            ),
        )
        # Update the selected station ID in session state
        st.session_state.selected_station_ai = station_id_mapping[
            station_options.index(selected_station_ai_index)
        ]

with col4:
    carburant = st.selectbox(
        "Select a fuel type", ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
    )

# Filter df
selected_station_ai_id = st.session_state.selected_station_ai

df_filtered = df_prix[df_prix["ID"] == selected_station_ai_id]

print(df_filtered)

# Convert dates to ordinal
df_filtered["Date_Ordinal"] = df_filtered["Date"].apply(lambda x: x.toordinal())

# Split the data into training and testing sets
X = df_filtered[["Date_Ordinal"]].values
y = df_filtered[carburant].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create and train the model
model = LinearRegression()

model.fit(X_train, y_train)

# Predict the closing price each days until the end date

date_range = pd.date_range(
    start=st.session_state.selected_date,
    end=st.session_state.selected_date_end_ai,
    freq="D",
)

date_range_ordinal = (
    date_range.to_series().apply(lambda x: x.toordinal()).values.reshape(-1, 1)
)

predicted_prices = model.predict(date_range_ordinal)

# Create a dataframe with the predicted prices
df_predicted_prices = pd.DataFrame(
    {
        "Date": date_range,
        "Predicted_Price": predicted_prices,
    }
)

print(df_predicted_prices)

# Plot the past data and forecasted prices using plotly express, forecasted data is dotted line

fig = px.line(
    df_filtered,
    x="Date",
    y=carburant,
    title=f"Price of {carburant} at station {selected_station_ai_id}",
)

fig.add_scatter(
    x=df_predicted_prices["Date"],
    y=df_predicted_prices["Predicted_Price"],
    mode="lines",
    line=dict(dash="dot"),
    name="Predicted Price",
)

st.plotly_chart(fig)
