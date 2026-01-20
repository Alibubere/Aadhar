"""Goal: Identify Labor Migration Hubs using the ratio of Updates vs. New Enrolments. Includes the Log-Scale Fix."""

import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. LOAD DEMOGRAPHIC (Updates) ---
files_demo = glob.glob('demographic_data/*.xlsx')
df_demo = pd.concat([pd.read_excel(f, usecols=['pincode', 'demo_age_17_']) for f in files_demo])
grouped_demo = df_demo.groupby('pincode')['demo_age_17_'].sum().reset_index()

# --- 2. LOAD ENROLMENT (New Entries) ---
files_enrol = glob.glob('enrolment_data/*.xlsx')
df_enrol = pd.concat([pd.read_excel(f, usecols=['pincode', 'age_18_greater']) for f in files_enrol])
grouped_enrol = df_enrol.groupby('pincode')['age_18_greater'].sum().reset_index()

# --- 3. MERGE & CALCULATE MIGRATION SCORE ---
merged = pd.merge(grouped_demo, grouped_enrol, on='pincode', how='inner')

# Score = Updates / New Enrolments
merged['migration_score'] = merged['demo_age_17_'] / (merged['age_18_greater'] + 1)

# Filter for statistically significant volume (ignore tiny villages)
merged = merged[merged['demo_age_17_'] > 1000]

# Get Top 10 Magnets
top_magnets = merged.sort_values(by='migration_score', ascending=False).head(10)
top_magnets['pincode'] = top_magnets['pincode'].astype(str)

# --- 4. VISUALIZATION (With Log Scale) ---
plt.figure(figsize=(12, 6))

# Stacked logic visualization manually
# Bar 1: The Migrants (Updates)
sns.barplot(data=top_magnets, x='pincode', y='demo_age_17_', color='orange', label='Migrants (Updates)')
# Bar 2: The Locals (New Enrolment)
sns.barplot(data=top_magnets, x='pincode', y='age_18_greater', color='green', label='Locals (New Enrolments)')

# CRITICAL: LOG SCALE
plt.yscale('log')

plt.title('The "Workforce Magnet" Index (Log Scale)', fontsize=16)
plt.ylabel('Volume of People (Log Scale)', fontsize=12)
plt.xlabel('PIN Code (Destination Hub)', fontsize=12)
plt.legend()

plt.tight_layout()
plt.show()