#Goal: Find PIN codes with High Adult Updates (demo_age_17_) but Low New Enrolments (age_18_greater).

import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- LOAD DEMOGRAPHIC DATA (Updates) ---
demo_files = glob.glob('demographic_data/*.xlsx')
df_demo_list = []
for file in demo_files:
    temp = pd.read_excel(file, usecols=['pincode', 'demo_age_17_'])
    df_demo_list.append(temp)
df_demo = pd.concat(df_demo_list)

# Group by PINCODE to get total updates per area
demo_grouped = df_demo.groupby('pincode')['demo_age_17_'].sum().reset_index()

# --- LOAD ENROLMENT DATA (New Entries) ---
enrol_files = glob.glob('enrolment_data/*.xlsx')
df_enrol_list = []
for file in enrol_files:
    temp = pd.read_excel(file, usecols=['pincode', 'age_18_greater'])
    df_enrol_list.append(temp)
df_enrol = pd.concat(df_enrol_list)

# Group by PINCODE to get total new enrolments per area
enrol_grouped = df_enrol.groupby('pincode')['age_18_greater'].sum().reset_index()

# --- MERGE DATASETS ---
# Combine them on PIN Code
merged_df = pd.merge(demo_grouped, enrol_grouped, on='pincode', how='inner')

# Calculate the "Migration Ratio" (Updates / New Enrolments)
# Adding +1 to denominator to avoid division by zero errors
merged_df['migration_ratio'] = merged_df['demo_age_17_'] / (merged_df['age_18_greater'] + 1)

# Sort to find the Top 10 "Migrant Hubs" (High Updates, Low Enrolment)
top_hubs = merged_df.sort_values(by='migration_ratio', ascending=False).head(10)

# Make PIN code a string so it doesn't look like a number on the chart
top_hubs['pincode'] = top_hubs['pincode'].astype(str)

"""if want to see green bar(log values)
# --- VISUALIZATION WITH LOG SCALE ---
plt.figure(figsize=(12, 6))

# Plot Orange (Updates)
sns.barplot(data=top_hubs, x='pincode', y='demo_age_17_', color='orange', label='Updates (Migrants)')

# Plot Green (New Enrolments) - distinct color to ensure visibility
sns.barplot(data=top_hubs, x='pincode', y='age_18_greater', color='darkgreen', alpha=1.0, label='New Enrolments (Locals)')

# KEY FIX: Set Y-axis to Logarithmic Scale
plt.yscale('log') 

plt.title('Top 10 Migrant Worker Hubs (Log Scale)', fontsize=16)
plt.ylabel('Count of Activities (Log Scale)', fontsize=12)
plt.xlabel('PIN Code', fontsize=12)
plt.legend()

# Optional: Add text labels on top of the green bars so you can read the tiny values
for index, row in top_hubs.iterrows():
    # This places the number right above the tiny bar
    plt.text(index, row['age_18_greater'], f"{int(row['age_18_greater'])}", 
             color='black', ha="center", va="bottom", fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()"""

# --- VISUALIZATION ---
plt.figure(figsize=(12, 6))

# Create a Bar Chart
sns.barplot(data=top_hubs, x='pincode', y='demo_age_17_', color='orange', label='Updates (Migrants)')
# Overlay New Enrolments to show the gap
sns.barplot(data=top_hubs, x='pincode', y='age_18_greater', color='green', alpha=0.6, label='New Enrolments (Locals)')

plt.title('Top 10 Migrant Worker Hubs (High Updates vs Low New Entries)', fontsize=16)
plt.ylabel('Count of Activities', fontsize=12)
plt.xlabel('PIN Code', fontsize=12)
plt.legend()

plt.tight_layout()
plt.show()

#shows the most migrated pin