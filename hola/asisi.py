import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# =============================================================================
# PART 1: DATA INGESTION & SIMULATION (The "Mock" Layer)
# =============================================================================
# NOTE: In production, replace the 'data' dictionaries below with pd.read_csv()
# matching your file paths.

def get_census_data():
    """
    Simulates the 2011 Census Dataset based on your specific columns.
    We are using the exact column names you provided.
    """
    data = {
        'State name': ['JAMMU AND KASHMIR', 'JAMMU AND KASHMIR', 'MAHARASHTRA', 'UTTAR PRADESH', 'BIHAR', 'KARNATAKA', 'KERALA'],
        'District name': ['Kupwara', 'Badgam', 'Mumbai Suburban', 'Ghaziabad', 'Patna', 'Bangalore Urban', 'Wayanad'],
        'Population': [870354, 753745, 9356962, 4681645, 5838465, 9621551, 817420], # 2011 Actuals
        'Rural_Households': [101642, 90000, 500, 200000, 400000, 100000, 150000],
        'Urban_Households': [99947, 40000, 2000000, 800000, 600000, 2300000, 50000]
    }
    return pd.DataFrame(data)

def get_aadhaar_logs():
    """
    Simulates the daily Aadhaar logs (Enrolment, Updates) AND generates the 
    missing 'Auth Volumes' and 'Historical Load' required for ASISI.
    """
    # 1. Base Logs (What you have)
    data = {
        'state': ['JAMMU AND KASHMIR', 'JAMMU AND KASHMIR', 'MAHARASHTRA', 'UTTAR PRADESH', 'BIHAR', 'KARNATAKA', 'KERALA'],
        'district': ['Kupwara', 'Badgam', 'Mumbai Suburban', 'Ghaziabad', 'Patna', 'Bangalore Urban', 'Wayanad'],
        'enrolment_volume': [150, 120, 4500, 1200, 2300, 3100, 400],
        'demo_update_volume': [400, 350, 8000, 3000, 5000, 7500, 600],
        'bio_update_volume': [200, 180, 2100, 900, 1500, 2200, 300],
    }
    df = pd.DataFrame(data)
    
    # 2. MISSING DATA GENERATION (Required for full ASISI)
    np.random.seed(42) # Ensure consistent results
    
    # A. Auth Volumes (Usually high volume, low processing time)
    # Logic: Auth is often 5x-10x of updates in busy districts
    df['auth_volume'] = (df['demo_update_volume'] * np.random.uniform(2, 5, len(df))).astype(int)
    
    # B. Historical Load (Required for 'Resilience/Recovery' Analysis)
    # We simulate the Total Transactions for the last 7 days to check if backlog is growing.
    # Format: A list of 7 integers for each district.
    
    historical_trends = []
    trends_type = ['recovering', 'spiking', 'chaotic', 'stable', 'crashing', 'spiking', 'stable']
    
    for i, trend in enumerate(trends_type):
        base_load = df.loc[i, 'enrolment_volume'] + df.loc[i, 'demo_update_volume']
        if trend == 'recovering':
            # Load decreases over 7 days (Good Resilience)
            hist = [int(base_load * (1.5 - x/10)) for x in range(7)] 
        elif trend == 'spiking':
            # Load increases over 7 days (Poor Resilience/Backlog)
            hist = [int(base_load * (1.0 + x/10)) for x in range(7)]
        elif trend == 'crashing':
             # Huge spike then crash
            hist = [int(base_load * 2), int(base_load * 2.1), int(base_load * 2.2), int(base_load*2.3), int(base_load*2.4), int(base_load*2.5), int(base_load*2.6)]
        else:
            # Stable noise
            hist = [int(base_load * np.random.uniform(0.9, 1.1)) for x in range(7)]
            
        historical_trends.append(hist)
        
    df['history_7_days'] = historical_trends
    return df

# =============================================================================
# PART 2: THE ASISI ENGINE (The Logic Layer)
# =============================================================================

def run_asisi_analysis():
    print(">>> 1. Ingesting Data...")
    df_census = get_census_data()
    df_aadhaar = get_aadhaar_logs()

    print(">>> 2. Projecting Population to 2025...")
    # Formula: Pop2011 * (1.012 ^ 14 years)
    growth_factor = (1.012) ** 14
    df_census['Pop_2025'] = (df_census['Population'] * growth_factor).astype(int)

    print(">>> 3. Estimating Infrastructure (Supply Side)...")
    # Logic: Estimate 1 center per 20k people + random variance for reality
    df_census['Est_Centers'] = (df_census['Pop_2025'] / np.random.randint(18000, 22000, len(df_census))).astype(int)

    # MERGE DATASETS
    # Normalize names to ensure clean join
    df_census['key'] = df_census['District name'].str.lower().str.strip()
    df_aadhaar['key'] = df_aadhaar['district'].str.lower().str.strip()
    df = pd.merge(df_census, df_aadhaar, on='key', how='inner')

    print(">>> 4. calculating Core Metrics...")
    
    # 4.1 TOTAL LOAD (The Volume Pressure)
    # Weighted Load: Updates take longer than Auth. We weight them.
    # Enrolment (1.0) | Update (0.8) | Bio (0.8) | Auth (0.1)
    df['Weighted_Load'] = (
        (df['enrolment_volume'] * 1.0) + 
        (df['demo_update_volume'] * 0.8) + 
        (df['bio_update_volume'] * 0.8) + 
        (df['auth_volume'] * 0.1)
    )
    
    # 4.2 QUALITY STRESS (Rejection Rate)
    # Logic: Rural areas often have higher biometric rejection.
    rural_ratio = df['Rural_Households'] / (df['Rural_Households'] + df['Urban_Households'])
    # Base 3% rejection + penalty for high rural (infrastructure gaps) + noise
    df['Rejection_Rate'] = 0.03 + (0.05 * rural_ratio) + np.random.uniform(0, 0.02, len(df))

    # 4.3 RESILIENCE (Recovery Slope) - THE MISSING PIECE
    # We calculate the slope of the last 7 days.
    # Positive Slope (>0) = Backlog is building (BAD)
    # Negative Slope (<0) = Backlog is clearing (GOOD)
    def get_slope(history_list):
        days = np.array(range(len(history_list)))
        loads = np.array(history_list)
        # Linear regression (Polyfit degree 1)
        slope, _ = np.polyfit(days, loads, 1)
        return slope
    
    df['Recovery_Slope'] = df['history_7_days'].apply(get_slope)

    # 4.4 SATURATION (Centers per 10k people)
    df['Centers_Per_10k'] = (df['Est_Centers'] / df['Pop_2025']) * 10000

    print(">>> 5. Computing ASISI Score...")
    
    scaler = MinMaxScaler()
    
    # Normalize Inputs (All scaled 0-1)
    # 1. Load Stress (Higher is Worse)
    s_load = scaler.fit_transform(df[['Weighted_Load']])
    
    # 2. Quality Stress (Higher Rejection is Worse)
    s_quality = scaler.fit_transform(df[['Rejection_Rate']])
    
    # 3. Resilience Stress (Higher Slope is Worse/Building Backlog)
    s_resilience = scaler.fit_transform(df[['Recovery_Slope']])
    
    # 4. Saturation Stress (LOWER centers is Worse, so we invert)
    s_saturation = 1 - scaler.fit_transform(df[['Centers_Per_10k']])

    # === THE ASISI FORMULA ===
    # Weights: 
    # Load (35%) - Immediate pressure
    # Quality (25%) - Data integrity
    # Resilience (25%) - Can they handle it?
    # Saturation (15%) - Structural capacity
    
    df['ASISI_Score'] = (
        (0.35 * s_load) + 
        (0.25 * s_quality) + 
        (0.25 * s_resilience) + 
        (0.15 * s_saturation)
    )

    # Categorize
    def get_status(x):
        if x > 0.7: return 'RED (Critical)'
        if x > 0.45: return 'YELLOW (Warning)'
        return 'GREEN (Stable)'
    
    df['Status'] = df['ASISI_Score'].apply(get_status)
    
    return df

# =============================================================================
# PART 3: VISUALIZATION & REPORTING
# =============================================================================

def visualize_results(df):
    sns.set_theme(style="whitegrid")
    
    # Fig 1: Main ASISI Scoreboard
    plt.figure(figsize=(12, 6))
    colors = {'RED (Critical)': '#ff4d4d', 'YELLOW (Warning)': '#ffcc00', 'GREEN (Stable)': '#2ecc71'}
    
    sns.barplot(
        x='ASISI_Score', 
        y='District name', 
        data=df.sort_values('ASISI_Score', ascending=False),
        hue='Status',
        palette=colors,
        dodge=False
    )
    plt.axvline(0.7, color='red', linestyle='--', label='Critical Threshold')
    plt.title('ASISI: District Stress Index (Combined Score)')
    plt.xlabel('Stress Score (0 = Healthy, 1 = Collapse)')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()

    # Fig 2: The "Why is it breaking?" Analysis (Resilience vs Load)
    plt.figure(figsize=(10, 6))
    
    # We want to see: Is it breaking because of volume (Load) or inability to process (Slope)?
    sns.scatterplot(
        x='Weighted_Load', 
        y='Recovery_Slope', 
        hue='Status', 
        size='Pop_2025',
        sizes=(100, 1000),
        palette=colors,
        data=df
    )
    plt.axhline(0, color='grey', linestyle='--', alpha=0.5)
    plt.text(df['Weighted_Load'].min(), 10, "BACKLOG BUILDING (Bad Resilience)", verticalalignment='bottom')
    plt.text(df['Weighted_Load'].min(), -10, "CLEARING RUSH (Good Resilience)", verticalalignment='top')
    
    plt.title('Resilience Matrix: Load vs. Recovery Ability')
    plt.ylabel('Recovery Slope (7-Day Trend)')
    plt.xlabel('Current Weighted Load')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

# =============================================================================
# EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Run Analysis
    final_df = run_asisi_analysis()
    
    # Print Text Report
    print("\n" + "="*50)
    print("ASISI INTELLIGENCE REPORT")
    print("="*50)
    
    cols = ['District name', 'Pop_2025', 'Weighted_Load', 'Recovery_Slope', 'ASISI_Score', 'Status']
    print(final_df[cols].sort_values('ASISI_Score', ascending=False).to_string(index=False))
    
    print("\n[ACTIONABLE INSIGHTS]")
    critical = final_df[final_df['Status'] == 'RED (Critical)']
    if not critical.empty:
        for index, row in critical.iterrows():
            print(f"⚠️  ALERT: {row['District name']} is CRITICAL.")
            if row['Recovery_Slope'] > 0:
                print(f"   -> Problem: Backlog is growing (Slope: {row['Recovery_Slope']:.2f}). Open emergency centers immediately.")
            if row['Rejection_Rate'] > 0.08:
                print(f"   -> Problem: High Rejection Rate ({row['Rejection_Rate']*100:.1f}%). Audit Registrar devices.")
    else:
        print("✅ No districts are currently in Critical state.")
        
    # Launch Graphs
    visualize_results(final_df)