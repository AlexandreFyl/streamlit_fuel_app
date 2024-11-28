# ---------------
# --- IMPORTS ---
# ---------------

import streamlit as st

# ----------------
# --- SELECTOR ---
# ----------------

df_prix = st.session_state.df_prix
df_stations = st.session_state.df_stations

# We merge the "Enseigne" column from df_stations to df_prix
df_prix = df_prix.rename(columns={"id": "ID"})
df_prix = df_prix.merge(df_stations[["ID", "Enseignes"]], on="ID")

# Date input
if "selected_date" not in st.session_state:
    st.session_state.selected_date = st.date_input(
        "Select a date",
        value=df_prix["Date"].max(),
        min_value=df_prix["Date"].min(),
        max_value=df_prix["Date"].max(),
    )
else:
    st.session_state.selected_date = st.date_input(
        "Select a date",
        value=st.session_state.selected_date,
        min_value=df_prix["Date"].min(),
        max_value=df_prix["Date"].max(),
    )


# -----------------
# --- TREATMENT ---
# -----------------


# Filter the data
def filter_data(df, date):
    df_filtered = df[df["Date"] == date]
    df_filtered_auchan = df_filtered[df_filtered["Enseignes"] == "auchan"]
    df_filtered_carrefour = df_filtered[df_filtered["Enseignes"] == "carrefour"]
    df_filtered_intermarche = df_filtered[df_filtered["Enseignes"] == "intermarche"]
    df_filtered_leclerc = df_filtered[df_filtered["Enseignes"] == "leclerc"]
    df_filtered_systemeu = df_filtered[df_filtered["Enseignes"] == "systeme u"]
    df_filtered_totalaccess = df_filtered[
        df_filtered["Enseignes"] == "totalenergies access"
    ]

    #  We return mean price for each gas type in a global object

    def mean_without_zeros(series):
        return series[series != 0].mean()

    return {
        "Auchan": {
            "Gazole": mean_without_zeros(df_filtered_auchan["Gazole"]),
            "SP95": mean_without_zeros(df_filtered_auchan["SP95"]),
            "SP98": mean_without_zeros(df_filtered_auchan["SP98"]),
            "E10": mean_without_zeros(df_filtered_auchan["E10"]),
            "E85": mean_without_zeros(df_filtered_auchan["E85"]),
            "GPLc": mean_without_zeros(df_filtered_auchan["GPLc"]),
        },
        "Carrefour": {
            "Gazole": mean_without_zeros(df_filtered_carrefour["Gazole"]),
            "SP95": mean_without_zeros(df_filtered_carrefour["SP95"]),
            "SP98": mean_without_zeros(df_filtered_carrefour["SP98"]),
            "E10": mean_without_zeros(df_filtered_carrefour["E10"]),
            "E85": mean_without_zeros(df_filtered_carrefour["E85"]),
            "GPLc": mean_without_zeros(df_filtered_carrefour["GPLc"]),
        },
        "Intermarché": {
            "Gazole": mean_without_zeros(df_filtered_intermarche["Gazole"]),
            "SP95": mean_without_zeros(df_filtered_intermarche["SP95"]),
            "SP98": mean_without_zeros(df_filtered_intermarche["SP98"]),
            "E10": mean_without_zeros(df_filtered_intermarche["E10"]),
            "E85": mean_without_zeros(df_filtered_intermarche["E85"]),
            "GPLc": mean_without_zeros(df_filtered_intermarche["GPLc"]),
        },
        "Leclerc": {
            "Gazole": mean_without_zeros(df_filtered_leclerc["Gazole"]),
            "SP95": mean_without_zeros(df_filtered_leclerc["SP95"]),
            "SP98": mean_without_zeros(df_filtered_leclerc["SP98"]),
            "E10": mean_without_zeros(df_filtered_leclerc["E10"]),
            "E85": mean_without_zeros(df_filtered_leclerc["E85"]),
            "GPLc": mean_without_zeros(df_filtered_leclerc["GPLc"]),
        },
        "Système U": {
            "Gazole": mean_without_zeros(df_filtered_systemeu["Gazole"]),
            "SP95": mean_without_zeros(df_filtered_systemeu["SP95"]),
            "SP98": mean_without_zeros(df_filtered_systemeu["SP98"]),
            "E10": mean_without_zeros(df_filtered_systemeu["E10"]),
            "E85": mean_without_zeros(df_filtered_systemeu["E85"]),
            "GPLc": mean_without_zeros(df_filtered_systemeu["GPLc"]),
        },
        "Total Access": {
            "Gazole": mean_without_zeros(df_filtered_totalaccess["Gazole"]),
            "SP95": mean_without_zeros(df_filtered_totalaccess["SP95"]),
            "SP98": mean_without_zeros(df_filtered_totalaccess["SP98"]),
            "E10": mean_without_zeros(df_filtered_totalaccess["E10"]),
            "E85": mean_without_zeros(df_filtered_totalaccess["E85"]),
            "GPLc": mean_without_zeros(df_filtered_totalaccess["GPLc"]),
        },
    }


# --------------
# --- RENDER ---
# --------------


# Function used to display the filtered data
def render_data(data):
    # Create a html flexbox container
    st.write(
        """
    <style>
        .flex-row {
            width: 100%;
            display: flex;
            flex-direction: row;
        }

        .flex-row > div {
            width: 12.5%;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
            text-align: center;
        }

        #no-border {
            border: none!important;
        }

        .gas-header, .enseigne {
            font-weight: bold;
            font-size: 1.5em;
        }

        .gas-header > div, .enseigne {
            border: 2px solid #ccc!important;
        }

        .data-value {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .lowest {
            border: 1px solid #ff6666!important;
            border-left : 7px solid #ff6666!important;
        }

        .highest {
            border: 1px solid #66ff66!important;
            border-left : 7px solid #66ff66!important;
        }
    </style>

    <div class="main-container">
        <div class="flex-row gas-header">
            <div id="no-border"></div>
            <div>Gazole</div>
            <div>SP95</div>
            <div>SP98</div>
            <div>E10</div>
            <div>E85</div>
            <div>GPLc</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Calculate min and max values for each fuel type
    all_values = {
        "Gazole": [],
        "SP95": [],
        "SP98": [],
        "E10": [],
        "E85": [],
        "GPLc": [],
    }

    for element in data.values():
        for fuel_type in all_values.keys():
            all_values[fuel_type].append(float(element[fuel_type]))  # Convert to float

    min_values = {fuel_type: min(values) for fuel_type, values in all_values.items()}
    max_values = {fuel_type: max(values) for fuel_type, values in all_values.items()}

    print("Min values:", min_values)  # Debugging output
    print("Max values:", max_values)  # Debugging output

    # Add tolerance for comparison
    tolerance = 1e-9

    # Render the data from the filtered dataframe
    for element in data.items():
        gasole_value = element[1]["Gazole"]
        is_lowest_gazole = abs(gasole_value - min_values["Gazole"]) < tolerance
        is_highest_gazole = abs(gasole_value - max_values["Gazole"]) < tolerance

        print(is_lowest_gazole)  # Debugging output
        print(is_highest_gazole)

        sp95_value = element[1]["SP95"]
        is_lowest_sp95 = abs(sp95_value - min_values["SP95"]) < tolerance
        is_highest_sp95 = abs(sp95_value - max_values["SP95"]) < tolerance

        sp98_value = element[1]["SP98"]
        is_lowest_sp98 = abs(sp98_value - min_values["SP98"]) < tolerance
        is_highest_sp98 = abs(sp98_value - max_values["SP98"]) < tolerance

        e10_value = element[1]["E10"]
        is_lowest_e10 = abs(e10_value - min_values["E10"]) < tolerance
        is_highest_e10 = abs(e10_value - max_values["E10"]) < tolerance

        e85_value = element[1]["E85"]
        is_lowest_e85 = abs(e85_value - min_values["E85"]) < tolerance
        is_highest_e85 = abs(e85_value - max_values["E85"]) < tolerance

        gplc_value = element[1]["GPLc"]
        is_lowest_gplc = abs(gplc_value - min_values["GPLc"]) < tolerance
        is_highest_gplc = abs(gplc_value - max_values["GPLc"]) < tolerance

        st.write(
            f"""
            <div class="flex-row data-row">
                <div class="enseigne">{element[0]}</div>
                <div class="data-value {'lowest' if is_lowest_gazole else 'highest' if is_highest_gazole else ''}">{gasole_value:.3f}</div>
                <div class="data-value {'lowest' if is_lowest_sp95 else 'highest' if is_highest_sp95 else ''}">{sp95_value:.3f}</div>
                <div class="data-value {'lowest' if is_lowest_sp98 else 'highest' if is_highest_sp98 else ''}">{sp98_value:.3f}</div>
                <div class="data-value {'lowest' if is_lowest_e10 else 'highest' if is_highest_e10 else ''}">{e10_value:.3f}</div>
                <div class="data-value {'lowest' if is_lowest_e85 else 'highest' if is_highest_e85 else ''}">{e85_value:.3f}</div>
                <div class="data-value {'lowest' if is_lowest_gplc else 'highest' if is_highest_gplc else ''}">{gplc_value:.3f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("</div>", unsafe_allow_html=True)


# Render the data
data = filter_data(df_prix, st.session_state.selected_date)
render_data(data)
