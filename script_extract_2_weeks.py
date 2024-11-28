import pandas as pd
from pathlib import Path

# Load data

df_prix = pd.read_csv(Path.cwd() / "data" / "origin" / "Prix_2024.csv")

# Remove NaN values

df_prix.dropna(inplace=True)

# Convert date column to datetime

df_prix["Date"] = pd.to_datetime(df_prix["Date"], format="%Y-%m-%d")

# Extract data from the last 2 weeks

df_prix_2_weeks = df_prix[
    df_prix["Date"] >= df_prix["Date"].max() - pd.Timedelta(weeks=2)
]

# Save the extracted data

df_prix_2_weeks.to_csv(
    Path.cwd() / "data" / "processed" / "Prix_2_weeks.csv", index=False
)
