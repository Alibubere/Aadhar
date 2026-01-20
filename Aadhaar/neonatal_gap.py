"""Goal: Identify PINs with high infant enrolment (age_0_5) but zero healthcare access. Note: Since you don't have the external hospital file yet, I have included a few lines to create a "Dummy Hospital Dataset" so the code runs immediately."""


import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. LOAD ENROLMENT DATA (Infants) ---
files = glob.glob('enrolment_data/*.xlsx')
df_list = []
for file in files:
    temp = pd.read_excel(file, usecols=['pincode', 'age_0_5'])
    df_list.append(temp)
df_enrol = pd.concat(df_list).groupby('pincode')['age_0_5'].sum().reset_index()

# --- 2. LOAD/CREATE EXTERNAL HOSPITAL DATA ---
# Since you likely don't have this file yet, we will SIMULATE it for the code to work.
# In reality, you would do: df_hospitals = pd.read_excel('hospital_locations.xlsx')

# [SIMULATION START]
unique_pins = df_enrol['pincode'].unique()
# Randomly assign 0 or 1 hospital to PINs for demonstration
hospital_data = {'pincode': unique_pins, 'hospital_count': np.random.choice([0, 1, 2], size=len(unique_pins), p=[0.7, 0.2, 0.1])}
df_hospitals = pd.DataFrame(hospital_data)
# [SIMULATION END]

# --- 3. MERGE & IDENTIFY "RISK ZONES" ---
merged_df = pd.merge(df_enrol, df_hospitals, on='pincode', how='left').fillna(0)

# LOGIC: High Kids (> 500) AND Zero Hospitals
risk_zones = merged_df[(merged_df['age_0_5'] > 500) & (merged_df['hospital_count'] == 0)]
top_risk_zones = risk_zones.sort_values(by='age_0_5', ascending=False).head(10)
top_risk_zones['pincode'] = top_risk_zones['pincode'].astype(str)

# --- 4. VISUALIZATION ---
plt.figure(figsize=(12, 6))

# We plot the number of infants in these "Medical Deserts"
sns.barplot(data=top_risk_zones, x='pincode', y='age_0_5', palette='Reds_r')

plt.title('The "Neonatal Gap": Top Areas with High Infant Enrolment but ZERO Hospitals', fontsize=16)
plt.ylabel('Infant Count (Age 0-5)', fontsize=12)
plt.xlabel('PIN Code (Risk Zone)', fontsize=12)
plt.axhline(0, color='black', linewidth=1)

# Add Annotation
plt.figtext(0.5, 0.01, "Action: Deploy Mobile Medical Vans to these PIN codes immediately.", 
            ha="center", fontsize=10, bbox={"facecolor":"yellow", "alpha":0.3})

plt.tight_layout()
plt.show()