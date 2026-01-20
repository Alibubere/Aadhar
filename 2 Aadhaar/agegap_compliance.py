# ============================================
# Aadhaar Biometric Age-Gap Compliance Monitor
# ============================================

import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- UTF-8 FIX ----------
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("\n========== SCRIPT STARTED ==========")

# ============================================
# 1. LOAD FILES (FAST)
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "biometric_data")

files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))

if not files:
    raise FileNotFoundError("❌ No Excel files found")

df = pd.concat(
    (pd.read_excel(
        f,
        usecols=['state', 'district', 'pincode', 'bio_age_5_17', 'bio_age_17_']
    ) for f in files),
    ignore_index=True
)

print("✔ Files Loaded | Rows:", len(df))

# ============================================
# 2. RENAME COLUMNS (SAME AS YOUR CODE)
# ============================================

df.rename(columns={
    'bio_age_5_17': 'child_updates',
    'bio_age_17_': 'adult_updates'
}, inplace=True)

# ============================================
# 3. DATA SANITY FILTER (VERY IMPORTANT)
# ============================================

df = df[
    (df['child_updates'] >= 0) &
    (df['adult_updates'] > 0)   # 🚀 THIS FIXES ZERO DIVISION
]

# ============================================
# 4. COMPLIANCE RATIO (SAFE)
# ============================================

df['child_compliance_ratio'] = (
    df['child_updates'] / df['adult_updates']
).clip(lower=0)

print("✔ Ratio Computed")

# ============================================
# 5. DISTRICT LEVEL AGGREGATION (FAST & CORRECT)
# ============================================

district_summary = (
    df.groupby(['state', 'district'], as_index=False)
      .agg(
          avg_child_compliance=('child_compliance_ratio', 'mean'),
          affected_pincodes=('pincode', 'nunique')
      )
)

# 🚨 This is why second graph was blank earlier
district_summary = district_summary[
    district_summary['avg_child_compliance'] > 0
]

top_problem_districts = (
    district_summary
    .sort_values('avg_child_compliance')
    .head(10)
)

print("\nTOP LOW COMPLIANCE DISTRICTS")
print(top_problem_districts)

# ============================================
# 6. VISUALIZATION (CLEAR & MISREAD-PROOF)
# ============================================

plt.figure(figsize=(12, 6))

sns.barplot(
    data=top_problem_districts,
    x='avg_child_compliance',
    y='district',
    color='#c0392b'  # strong red = bad
)

# --- Visual guidance zones ---
plt.axvspan(0, 0.05, color='green', alpha=0.15, label='Acceptable gap')
plt.axvspan(0.05, 0.15, color='orange', alpha=0.15, label='Warning')
plt.axvspan(0.15, top_problem_districts['avg_child_compliance'].max(),
            color='red', alpha=0.10, label='Critical')

plt.title(
    'Child Disadvantage vs Adults (Biometric Usage)\nDistrict-wise',
    fontsize=16
)

plt.xlabel(
    'Child disadvantage ratio (Lower = Better, 0 = Equal to adults)',
    fontsize=12
)
plt.ylabel('District', fontsize=12)

plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.legend()

plt.tight_layout()
plt.show()
