"""Goal: Detect suspicious spikes in Adult Demographic Updates (demo_age_17_) within short time windows (e.g., specific months)."""


import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. LOAD DEMOGRAPHIC DATA ---
files = glob.glob('demographic_data/*.xlsx')
df_list = []

for file in files:
    # We need Date and PIN Code
    temp = pd.read_excel(file, usecols=['date', 'pincode', 'demo_age_17_'])
    df_list.append(temp)

df_demo = pd.concat(df_list)

# --- 2. PREPROCESSING ---
# Convert date column to datetime
df_demo['date'] = pd.to_datetime(df_demo['date'], dayfirst=True)
# Extract Month-Year for grouping (e.g., "2025-02")
df_demo['month_year'] = df_demo['date'].dt.to_period('M')

# --- 3. ANALYSIS: CALCULATE VELOCITY ---
# Sum updates by PIN Code and Month
monthly_activity = df_demo.groupby(['pincode', 'month_year'])['demo_age_17_'].sum().reset_index()

# Calculate the "Average Monthly Activity" per PIN to find the baseline
pin_baseline = monthly_activity.groupby('pincode')['demo_age_17_'].mean().reset_index()
pin_baseline.rename(columns={'demo_age_17_': 'avg_updates'}, inplace=True)

# Merge back to compare current month vs average
analysis_df = pd.merge(monthly_activity, pin_baseline, on='pincode')

# TRIGGER: Find instances where activity is > 5x the average (400% spike)
# Filter for meaningful volume (ignore spikes from 1 to 5)
analysis_df = analysis_df[analysis_df['avg_updates'] > 50] 
spikes = analysis_df[analysis_df['demo_age_17_'] > (analysis_df['avg_updates'] * 5)]

# Sort by the magnitude of the spike
top_phantom_clusters = spikes.sort_values(by='demo_age_17_', ascending=False).head(5)

print("--- ALERT: TOP 5 PHANTOM CLUSTERS DETECTED ---")
print(top_phantom_clusters)

# --- 4. VISUALIZATION ---
if not top_phantom_clusters.empty:
    # Pick the #1 worst offender PIN code to visualize
    target_pin = top_phantom_clusters.iloc[0]['pincode']
    
    # Filter data for just that PIN
    pin_data = monthly_activity[monthly_activity['pincode'] == target_pin]
    pin_data['month_year'] = pin_data['month_year'].astype(str)

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=pin_data, x='month_year', y='demo_age_17_', marker='o', color='red', linewidth=3)
    
    plt.title(f'Phantom Cluster Detection: Suspicious Spike in PIN {target_pin}', fontsize=16)
    plt.xlabel('Timeline', fontsize=12)
    plt.ylabel('Adult Demographic Updates', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
else:
    print("No suspicious clusters found with current threshold.")