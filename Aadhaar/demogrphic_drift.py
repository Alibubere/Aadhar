"""Goal: Distinguish between Family Zones (Kids updating) and Worker/Transient Zones (Adults updating)."""


import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. LOAD DEMOGRAPHIC DATA (Adult Activity) ---
demo_files = glob.glob('demographic_data/*.xlsx')
df_demo_list = []
for file in demo_files:
    temp = pd.read_excel(file, usecols=['pincode', 'demo_age_17_'])
    df_demo_list.append(temp)
df_demo = pd.concat(df_demo_list).groupby('pincode')['demo_age_17_'].sum().reset_index()

# --- 2. LOAD BIOMETRIC DATA (Child Activity) ---
bio_files = glob.glob('biometric_data/*.xlsx')
df_bio_list = []
for file in bio_files:
    temp = pd.read_excel(file, usecols=['pincode', 'bio_age_5_17'])
    df_bio_list.append(temp)
df_bio = pd.concat(df_bio_list).groupby('pincode')['bio_age_5_17'].sum().reset_index()

# --- 3. MERGE & CALCULATE DRIFT SCORE ---
merged_df = pd.merge(df_demo, df_bio, on='pincode', how='inner')

# Formula: Drift Score = Adult Updates / (Child Updates + 1)
# (+1 prevents division by zero if an area has 0 child updates)
merged_df['drift_score'] = merged_df['demo_age_17_'] / (merged_df['bio_age_5_17'] + 1)

# Filter: We only want significant PIN codes (e.g., at least 100 activities) to avoid noise
merged_df = merged_df[merged_df['demo_age_17_'] > 100]

# Get Top 10 "Transient/Worker Zones" (High Drift Score)
transient_zones = merged_df.sort_values(by='drift_score', ascending=False).head(10)
transient_zones['pincode'] = transient_zones['pincode'].astype(str)

# --- 4. VISUALIZATION ---
plt.figure(figsize=(12, 6))

# We use a Scatter Plot to show the separation
sns.scatterplot(data=merged_df, x='bio_age_5_17', y='demo_age_17_', alpha=0.5, size='drift_score', sizes=(20, 200))

# Highlight the Top 10 Transient Zones
plt.scatter(transient_zones['bio_age_5_17'], transient_zones['demo_age_17_'], color='red', s=100, label='High Drift (Worker Zones)')

plt.title('Demographic Drift: Family Zones (Low Drift) vs. Worker Zones (High Drift)', fontsize=16)
plt.xlabel('Child Biometric Updates (Family Indicator)', fontsize=12)
plt.ylabel('Adult Demographic Updates (Worker Indicator)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

"""How to Interpret the "Drift" Graph:
Dots near the Bottom-Right: High Child Updates, Low Adult Updates. These are Residential/Family Areas (Safe for schools/parks).

Dots near the Top-Left (Red): Low Child Updates, High Adult Updates. These are Industrial/Bachelor Hubs (Need night shelters/transport)."""