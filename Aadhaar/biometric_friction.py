"""Goal: Identify areas with failing fingerprint sensors by looking for high voluntary adult biometric updates (bio_age_17_)."""


import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. LOAD BIOMETRIC DATA ---
files = glob.glob('biometric_data/*.xlsx')
df_list = []

for file in files:
    # We focus on ADULT biometric updates (Age 17+)
    temp = pd.read_excel(file, usecols=['state', 'district', 'bio_age_17_'])
    df_list.append(temp)

df_bio = pd.concat(df_list)

# --- 2. AGGREGATE ---
# Group by District (District level is better for hardware procurement)
friction_districts = df_bio.groupby(['state', 'district'])['bio_age_17_'].sum().reset_index()

# Sort to find the "Most Frustrated" Districts
top_friction = friction_districts.sort_values(by='bio_age_17_', ascending=False).head(10)

# --- 3. VISUALIZATION ---
plt.figure(figsize=(12, 6))

# Heatmap-style Bar Chart
sns.barplot(data=top_friction, x='bio_age_17_', y='district', palette='magma')

plt.title('The "Biometric Friction" Indicator: Districts with High Adult Biometric Updates', fontsize=16)
plt.xlabel('Number of Voluntary Adult Updates (Likely Authentication Failures)', fontsize=12)
plt.ylabel('District', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.6)

# Add Recommendation Text
plt.figtext(0.5, -0.05, "Recommendation: Prioritize these districts for Iris Scanners/Face Auth devices.", 
            ha="center", fontsize=11, fontweight='bold', color='darkred')

plt.tight_layout()
plt.show()