#Goal: Track bio_age_5_17 over time to find "Admission Season" spikes.

import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load ALL Excel files from the Biometric folder
file_list = glob.glob('biometric_data/*.xlsx') 

# Efficiently combine them into one DataFrame
df_list = []
for file in file_list:
    # Read only columns we need to save memory
    temp_df = pd.read_excel(file, usecols=['date', 'state', 'district', 'bio_age_5_17'])
    df_list.append(temp_df)

df_bio = pd.concat(df_list, ignore_index=True)
df_bio = df_bio[df_bio['state'] == 'Gujarat'] #Comment this line if want to see overall

# 2. Preprocessing
# Convert date column to datetime objects (assuming DD/MM/YYYY format)
df_bio['date'] = pd.to_datetime(df_bio['date'], dayfirst=True)

# Extract Month-Year for aggregation (e.g., "2025-03")
df_bio['month_year'] = df_bio['date'].dt.to_period('M')

# 3. Aggregation
# Group by Month and sum the updates
monthly_trend = df_bio.groupby('month_year')['bio_age_5_17'].sum().reset_index()

# Convert month_year back to string for plotting
monthly_trend['month_year'] = monthly_trend['month_year'].astype(str)

# --- VISUALIZATION ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_trend, x='month_year', y='bio_age_5_17', marker='o', linewidth=2.5, color='blue')

plt.title('The "School Compliance" Pulse: Mandatory Biometric Updates (Age 5-17)', fontsize=16)
plt.ylabel('Number of Updates', fontsize=12)
plt.xlabel('Timeline', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()




"""How to Read the Graph:
The Spike: You are looking for a sharp peak around April, May, June.
The Flatline: If the line is flat during these months, that is your anomaly."""