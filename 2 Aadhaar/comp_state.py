# ============================================
# Aadhaar Child Biometric Disadvantage vs Adults
# STATE-WISE ANALYSIS (FINAL FIXED VERSION)
# ============================================

import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# ---------- UTF-8 FIX ----------
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("\n========== STATE-WISE SCRIPT STARTED ==========")

# ============================================
# 1. LOAD DATA
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "biometric_data")

files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))

if not files:
    raise FileNotFoundError("❌ No Excel files found")

df = pd.concat(
    (pd.read_excel(f) for f in files),
    ignore_index=True
)

print("✔ Data Loaded:", df.shape)

# ============================================
# 2. RENAME COLUMNS
# ============================================

df.rename(columns={
    'bio_age_5_17': 'child_updates',
    'bio_age_17_': 'adult_updates'
}, inplace=True)

# ============================================
# 3. FILTER INVALID ROWS
# ============================================

df = df[
    (df['adult_updates'] > 0) &
    (df['child_updates'] >= 0)
]

# ============================================
# 4. SAFE COMPLIANCE RATIO
# ============================================

df['child_compliance_ratio'] = (
    df['child_updates'] / df['adult_updates']
).clip(lower=0)

# ============================================
# 5. 🔥 BULLETPROOF STATE NORMALIZATION 🔥
# ============================================

def normalize_state(s):
    s = str(s)
    s = s.replace('\xa0', ' ')          # remove non-breaking spaces
    s = re.sub(r'\s+', ' ', s)          # collapse multiple spaces
    s = s.strip().lower()               # trim + lowercase
    return s

df['state'] = df['state'].apply(normalize_state)

state_map = {
    'west bengal': 'West Bengal',
    'uttaranchal': 'Uttarakhand',
    'orissa': 'Odisha',
    'nct of delhi': 'Delhi',
    'delhi nct': 'Delhi',
    'dadra & nagar haveli': 'Dadra And Nagar Haveli And Daman And Diu',
    'daman & diu': 'Dadra And Nagar Haveli And Daman And Diu',
    'dadra and nagar haveli and daman and diu':
        'Dadra And Nagar Haveli And Daman And Diu',
    'jammu & kashmir': 'Jammu And Kashmir'
}

df['state'] = df['state'].replace(state_map)
df['state'] = df['state'].str.title()

print("✔ State Names Fully Normalized")

# ============================================
# 6. STATE-WISE AGGREGATION (NOW SAFE)
# ============================================

state_summary = (
    df.groupby('state', as_index=False)
      .agg(avg_child_compliance=('child_compliance_ratio', 'mean'))
)

top_problem_states = (
    state_summary
    .sort_values(by='avg_child_compliance')
    .head(10)
)

print("\nTOP LOW COMPLIANCE STATES")
print(top_problem_states)

# ============================================
# 7. VISUALIZATION (CLEAR & HONEST)
# ============================================

plt.figure(figsize=(13, 7))

# Risk zones
plt.axvspan(0.0, 0.30, color='red', alpha=0.12, label='Critical gap')
plt.axvspan(0.30, 0.60, color='orange', alpha=0.12, label='Moderate gap')
plt.axvspan(0.60, 1.0, color='green', alpha=0.12, label='Acceptable')

sns.barplot(
    data=top_problem_states,
    x='avg_child_compliance',
    y='state',
    color='darkred'
)

plt.title(
    'Child Biometric Disadvantage vs Adults\nState-wise (Age 5–17)',
    fontsize=16
)
plt.xlabel('Child to Adult Biometric Ratio (Lower = Worse)', fontsize=12)
plt.ylabel('State', fontsize=12)

plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.legend(loc='lower right')

plt.figtext(
    0.5, -0.12,
    "Lower ratio = children lag further behind adults.\n"
    "Focus areas: school drives, mobile kits, rural outreach.",
    ha='center',
    fontsize=11,
    color='darkred'
)

plt.tight_layout()
plt.show()

print("\n✅ FINAL GRAPH GENERATED — NO DUPLICATE STATES")
# ============================================
# Aadhaar Child Biometric Disadvantage vs Adults
# STATE-WISE ANALYSIS (FINAL CLEAN VERSION)
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

print("\n========== STATE-WISE SCRIPT STARTED ==========")

# ============================================
# 1. LOAD DATA
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "biometric_data")

files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))

if not files:
    raise FileNotFoundError("❌ No Excel files found in biometric_data folder")

df = pd.concat(
    (pd.read_excel(f) for f in files),
    ignore_index=True
)

print("✔ Data Loaded:", df.shape)

# ============================================
# 2. RENAME COLUMNS (UIDAI FORMAT)
# ============================================

df.rename(columns={
    'bio_age_5_17': 'child_updates',
    'bio_age_17_': 'adult_updates'
}, inplace=True)

required_cols = {'state', 'child_updates', 'adult_updates'}
missing = required_cols - set(df.columns)

if missing:
    raise ValueError(f"❌ Missing columns: {missing}")

# ============================================
# 3. SANITY FILTER (NO ZERO / NEGATIVE DIVISION)
# ============================================

df = df[
    (df['adult_updates'] > 0) &
    (df['child_updates'] >= 0)
]

# ============================================
# 4. SAFE COMPLIANCE RATIO
# ============================================

df['child_compliance_ratio'] = (
    df['child_updates'] / df['adult_updates']
).clip(lower=0)

print("✔ Compliance Ratio Calculated")

# ============================================
# 5. STRONG STATE NAME NORMALIZATION (FINAL FIX)
# ============================================

df['state'] = (
    df['state']
    .astype(str)
    .str.strip()
    .str.lower()
)

state_map = {
    # West Bengal
    'west bengal': 'West Bengal',
    'westbengal': 'West Bengal',
    'west bangal': 'West Bengal',

    # Uttarakhand
    'uttaranchal': 'Uttarakhand',
    'uttarakhand': 'Uttarakhand',

    # Odisha
    'orissa': 'Odisha',
    'odisha': 'Odisha',

    # Dadra & Daman
    'dadra & nagar haveli': 'Dadra And Nagar Haveli And Daman And Diu',
    'daman & diu': 'Dadra And Nagar Haveli And Daman And Diu',
    'dadra and nagar haveli and daman and diu':
        'Dadra And Nagar Haveli And Daman And Diu',

    # Delhi
    'nct of delhi': 'Delhi',
    'delhi nct': 'Delhi',
    'delhi': 'Delhi',

    # Jammu & Kashmir
    'jammu & kashmir': 'Jammu And Kashmir',
    'jammu and kashmir': 'Jammu And Kashmir'
}

df['state'] = df['state'].replace(state_map)
df['state'] = df['state'].str.title()

print("✔ State Names Normalized")

# ============================================
# 6. STATE-WISE AGGREGATION
# ============================================

state_summary = (
    df.groupby('state', as_index=False)
      .agg(
          avg_child_compliance=('child_compliance_ratio', 'mean'),
          total_pincodes=('adult_updates', 'count')
      )
)

# Lowest ratio = highest disadvantage
top_problem_states = (
    state_summary
    .sort_values(by='avg_child_compliance')
    .head(10)
)

print("\nTOP LOW COMPLIANCE STATES")
print(top_problem_states)

# ============================================
# 7. VISUALIZATION (CLEAR & UNAMBIGUOUS)
# ============================================

plt.figure(figsize=(13, 7))

# Risk zones
plt.axvspan(0.0, 0.30, color='red', alpha=0.12, label='Critical gap')
plt.axvspan(0.30, 0.60, color='orange', alpha=0.12, label='Moderate gap')
plt.axvspan(0.60, 1.0, color='green', alpha=0.12, label='Acceptable')

sns.barplot(
    data=top_problem_states,
    x='avg_child_compliance',
    y='state',
    color='darkred'
)

plt.title(
    'Child Biometric Disadvantage vs Adults\nState-wise (Age 5–17)',
    fontsize=16
)
plt.xlabel('Child to Adult Biometric Ratio (Lower = Worse)', fontsize=12)
plt.ylabel('State', fontsize=12)

plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.legend(loc='lower right')

plt.figtext(
    0.5, -0.12,
    "Interpretation: Lower values indicate children lagging behind adults in biometric updates.\n"
    "Policy focus: school enrolment drives, mobile kits, rural outreach.",
    ha='center',
    fontsize=11,
    color='darkred'
)

plt.tight_layout()
plt.show()

print("\n✅ STATE-WISE GRAPH GENERATED SUCCESSFULLY")