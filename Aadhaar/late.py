"""Goal: Find PIN codes with high new enrolments for adults (age_18_greater). These are "Digital Dark Zones" just coming online."""

import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. LOAD ENROLMENT DATA ---
enrol_files = glob.glob('enrolment_data/*.xlsx')
df_enrol_list = []

for file in enrol_files:
    # Focus strictly on Adult New Enrolments
    temp = pd.read_excel(file, usecols=['pincode', 'age_18_greater'])
    df_enrol_list.append(temp)

df_enrol = pd.concat(df_enrol_list)

# --- 2. AGGREGATE ---
# Sum by PIN Code to find hotspots
pin_enrol = df_enrol.groupby('pincode')['age_18_greater'].sum().reset_index()

# Find Top 15 "Late Adopter" PIN Codes
top_late_adopters = pin_enrol.sort_values(by='age_18_greater', ascending=False).head(15)

# Convert PIN to string for better plotting
top_late_adopters['pincode'] = top_late_adopters['pincode'].astype(str)

# --- 3. VISUALIZATION ---
plt.figure(figsize=(14, 7))

# Create Bar Chart
sns.barplot(data=top_late_adopters, x='pincode', y='age_18_greater', color='purple')

plt.title('The "Late Adopter" Heatmap: PIN Codes with Highest Adult New Enrolments', fontsize=16)
plt.ylabel('New Adult Enrolments (Count)', fontsize=12)
plt.xlabel('PIN Code', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Add text explanation on plot
plt.figtext(0.5, 0.01, "Insight: These areas are prime targets for opening new Jan Dhan Accounts.", 
            ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

plt.tight_layout()
plt.show()