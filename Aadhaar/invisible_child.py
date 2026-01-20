"""Goal: Identify districts where the number of children updating biometrics (Age 5/15) is suspiciously low compared to the number of children enrolled at birth.

Note on Data: Since we only have 2025 data, this script compares Current Enrolments (0-5) vs Current Updates (5-17).

Ideally: we would load a "2020 Enrolment File" for the age_0_5 part.

Current Fix: We use the current file as a placeholder so the code works."""


import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. LOAD ENROLMENT DATA (The "Birth Cohort") ---
# Ideally, this should be data from 5 years ago. 
# We are using current data as a placeholder for the code structure.
enrol_files = glob.glob('enrolment_data/*.xlsx')
df_enrol_list = []
for file in enrol_files:
    # We sum by District
    temp = pd.read_excel(file, usecols=['state', 'district', 'age_0_5'])
    df_enrol_list.append(temp)
    
df_enrol = pd.concat(df_enrol_list)
# Group by District to get total infants enrolled
dist_enrol = df_enrol.groupby(['state', 'district'])['age_0_5'].sum().reset_index()

# --- 2. LOAD BIOMETRIC DATA (The "Update Cohort") ---
bio_files = glob.glob('biometric_data/*.xlsx')
df_bio_list = []
for file in bio_files:
    temp = pd.read_excel(file, usecols=['state', 'district', 'bio_age_5_17'])
    df_bio_list.append(temp)

df_bio = pd.concat(df_bio_list)
# Group by District to get total children updating
dist_bio = df_bio.groupby(['state', 'district'])['bio_age_5_17'].sum().reset_index()

# --- 3. MERGE & ANALYZE ---
# Combine datasets on State and District
merged_df = pd.merge(dist_enrol, dist_bio, on=['state', 'district'], how='inner')

# Calculate the "Gap"
# Logic: If Enrolments (Past/Proxy) > Updates (Current), we have a drop-off.
merged_df['missing_children_gap'] = merged_df['age_0_5'] - merged_df['bio_age_5_17']

# Filter for "Red Flag" Districts (Positive Gap = Missing Kids)
red_flags = merged_df[merged_df['missing_children_gap'] > 0].sort_values(by='missing_children_gap', ascending=False).head(10)

# --- 4. VISUALIZATION ---
plt.figure(figsize=(12, 6))

# Plotting the Gap
sns.barplot(data=red_flags, x='missing_children_gap', y='district', palette='Reds_r')

plt.title('The "Invisible Child": Districts with Highest Drop-off (Enrolment vs Updates)', fontsize=16)
plt.xlabel('Estimated Number of Missing Updates', fontsize=12)
plt.ylabel('District', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()