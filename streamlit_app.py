import streamlit as st
import pandas as pd

# הגדרות עמוד
st.set_page_config(page_title="Noodelman Finance", layout="wide")

# פונקציית ניקוי נתונים
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        # מנקה הכל חוץ ממספרים, נקודה עשרונית וסימן מינוס
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# טעינת נתונים
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"
df = pd.read_csv(SHEET_URL)

# מיפוי עמודות (לפי הגיליון שלך)
# שם חוסך=0, אפיק=1, 2024=עמודה 6 (G), 2025=עמודה 11 (L)
cols_idx = {'name': 0, '2024': 6, '2025': 11}

# עיצוב CSS
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 20px; border-radius: 15px; text-align: center; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 2.5rem !important; font-weight: 700; color: #1E88E5; }
    [data-testid="stMetricLabel"] { justify-content: center; font-size: 1.2rem !important; }
    h1, h2, h3 { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 הון משפחת נודלמן")

# --- שליפת נתונים מדויקת מתא C15 (שנת 2025) ---
# באקסל שורה 15 היא אינדקס 13 ב-pandas (כי סופרים מ-0 ויש שורת כותרת)
# עמודה L (2025) היא אינדקס 11
raw_total_25 = df.iloc[13, cols_idx['2025']]
total_25 = clean_currency(raw_total_25)

# שליפת נתונים לשנת 2024 (עמודה G היא אינדקס 6)
raw_total_24 = df.iloc[13, cols_idx['2024']]
total_24 = clean_currency(raw_total_24)

# חישוב הבדלים
diff = total_25 - total_24
pct = (diff / total_24 * 100) if total_24 != 0 else 0

# טאבים
tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט נכסים"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.metric(label="סה\"כ הון נטו (2025)", value=f"₪{total_25:,.0f}", delta=f"{pct:.1f}% מ-2024")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="גידול שנתי", value=f"₪{diff:,.0f}")
    with c2:
        # סכימה של שורות 0-11 לפי שם חוסך (לא כולל שורות סיכום)
        temp_df = df.iloc[0:12].copy()
        temp_df[df.columns[cols_idx['2025']]] = temp_df[df.columns[cols_idx['2025']]].apply(clean_currency)
        
        yaniv = temp_df[temp_df[df.columns[0]] == 'יניב'][df.columns[cols_idx['2025']]].sum()
        michal = temp_df[temp_df[df.columns[0]] == 'מיכל'][df.columns[cols_idx['2025']]].sum()
        
        st.write(f"**יניב:** ₪{yaniv:,.0f}")
        st.write(f"**מיכל:** ₪{michal:,.0f}")

with tab2:
    # מציג רק את שורות הנכסים (ללא שורות סיכום מהאקסל)
    st.dataframe(df.iloc[0:12][[df.columns[0], df.columns[1], df.columns[11]]], use_container_width=True)
