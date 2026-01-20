# ============================================
# Aadhaar BIO vs DEMO Compliance Gap (FAST)
# ============================================

import os
import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- UTF-8 SAFE ----------
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("\n========== SCRIPT STARTED ==========")

# ============================================
# 1. PATH SETUP
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BIO_DIR = os.path.join(BASE_DIR, "biometric_data")
DEMO_DIR = os.path.join(BASE_DIR, "demographic_data")

bio_files = glob.glob(os.path.join(BIO_DIR, "*.xlsx"))
demo_files = glob.glob(os.path.join(DEMO_DIR, "*.xlsx"))

print("BIO files:", len(bio_files))
print("DEMO files:", len(demo_files))

if not bio_files or not demo_files:
    raise FileNotFoundError("BIO or DEMO Excel files missing")

# ============================================
# 2. LOAD BIOMETRIC DATA (ONLY REQUIRED COLS)
# ============================================

bio_cols = ['state', 'district', 'pincode', 'bio_age_5_17']

bio_df = pd.concat(
    [pd.read_excel(f, usecols=bio_cols) for f in bio_files],
    ignore_index=True
)

bio_df.rename(columns={'bio_age_5_17': 'bio_child'}, inplace=True)

# Optimize datatypes
bio_df['pincode'] = bio_df['pincode'].astype('int32')
bio_df['bio_child'] = bio_df['bio_child'].astype('int32')

print("BIO rows:", len(bio_df))

# ============================================
# 3. LOAD DEMOGRAPHIC DATA
# ============================================

demo_cols = ['state', 'district', 'pincode', 'demo_age_5_17']

demo_df = pd.concat(
    [pd.read_excel(f, usecols=demo_cols) for f in demo_files],
    ignore_index=True
)

demo_df.rename(columns={'demo_age_5_17': 'demo_child'}, inplace=True)

demo_df['pincode'] = demo_df['pincode'].astype('int32')
demo_df['demo_child'] = demo_df['demo_child'].astype('int32')

print("DEMO rows:", len(demo_df))

# ============================================
# 4. MERGE (PINCODE LEVEL)
# ============================================

df = pd.merge(
    bio_df,
    demo_df,
    on=['state', 'district', 'pincode'],
    how='inner'
)

print("Merged rows:", len(df))

# ============================================
# 5. FAST COMPLIANCE RATIO (NO APPLY)
# ============================================

df['bio_demo_ratio'] = (
    df['bio_child'] / df['demo_child']
).replace([float('inf')], 0).fillna(0)

# ============================================
# 6. COMPLIANCE CATEGORY
# ============================================

df['compliance_status'] = pd.cut(
    df['bio_demo_ratio'],
    bins=[-1, 0.30, 0.60, 10],
    labels=['High Risk', 'Moderate', 'Normal']
)

# ============================================
# 7. DISTRICT LEVEL SUMMARY
# ============================================

district_summary = df.groupby(
    ['state', 'district'],
    as_index=False
).agg(
    avg_bio_demo_ratio=('bio_demo_ratio', 'mean'),
    high_risk_pincodes=('compliance_status', lambda x: (x == 'High Risk').sum())
)

# Risk score (UIDAI-friendly)
district_summary['risk_score'] = (
    (1 - district_summary['avg_bio_demo_ratio']) *
    district_summary['high_risk_pincodes']
)

top_districts = district_summary.sort_values(
    by='risk_score',
    ascending=False
).head(10)

print("\nTOP RISK DISTRICTS")
print(top_districts)

# ============================================
# 8. VISUALIZATION (CLEAR & MISREAD-PROOF)
# ============================================

plt.figure(figsize=(12, 6))

sns.barplot(
    data=top_districts,
    x='avg_bio_demo_ratio',
    y='district',
    color='#c0392b'  # strong red = risk
)

# --- Risk guidance zones ---
plt.axvspan(0.0, 0.30, color='red', alpha=0.15, label='Critical gap')
plt.axvspan(0.30, 0.60, color='orange', alpha=0.15, label='Moderate gap')
plt.axvspan(0.60, 1.0, color='green', alpha=0.15, label='Acceptable')

plt.title(
    'Child Biometric Disadvantage vs Demographic Updates\nDistrict-wise (Age 5–17)',
    fontsize=16
)

plt.xlabel(
    'BIO to DEMO update ratio (Lower = Worse, 1 = Fully matched)',
    fontsize=12
)
plt.ylabel('District', fontsize=12)

plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.legend()

# --- Zero-thinking explanation ---
plt.figtext(
    0.5, -0.12,
    "Lower bars mean children exist in demographic records but lack biometric updates.\n"
    "Red zones require immediate enrollment drives.",
    ha='center',
    fontsize=11,
    color='black'
)

plt.tight_layout()
plt.show()
