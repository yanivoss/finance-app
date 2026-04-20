import streamlit as st
import pandas as pd

# הגדרות עמוד למראה אפליקטיבי
st.set_page_config(page_title="Noodelman Finance", layout="wide")

# פונקציית ניקוי נתונים (מטפלת ב-₪, פסיקים, רווחים וערכים ריקים)
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# הגדרת הלינקים לפי ה-GID שסיפקת
BASE_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"
GID_SUMMARY = "1388477026"  # גיליון App_Summary
GID_DATA = "152067713"      # גיליון מעקב הון עצמי

# טעינת הנתונים
df_summary = pd.read_csv(f"{BASE_URL}&gid={GID_SUMMARY}")
df_data = pd.read_csv(f"{BASE_URL}&gid={GID_DATA}")

# עיצוב CSS למרכוז ושיפור הנראות בנייד
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 15px; text-align: center; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 2.2rem !important; font-weight: bold; color: #1E88E5; }
    [data-testid="stMetricLabel"] { justify-content: center; font-size: 1.1rem !important; }
    h1, h3 { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

# טאבים
tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט נכסים"])

with tab1:
    # שליפת נתונים מדויקת מתא C15 בגיליון App_Summary
    # שורה 15 באקסל = אינדקס 13 | עמודה C = אינדקס 2
    try:
        net_worth_2025 = clean_currency(df_summary.iloc[13, 2])
        # שליפת נתון 2024 (נניח שהוא בעמודה אחת לפני או לפי המיקום בגיליון)
        # אם 2024 נמצא בעמודה B, זה יהיה אינדקס 1
        net_worth_2024 = clean_currency(df_summary.iloc[13, 1]) 
        
        diff = net_worth_2025 - net_worth_2024
        pct = (diff / net_worth_2024 * 100) if net_worth_2024 != 0 else 0

        st.markdown("<br>", unsafe_allow_html=True)
        st.metric(label="סה\"כ הון נטו (2025)", value=f"₪{net_worth_2025:,.0f}", delta=f"{pct:.1f}%")
        
        st.divider()
        
        # חלוקה מהירה (סכימה מגיליון המעקב כדי לוודא שזה מעודכן)
        # נניח ששנת 2025 היא עמודה 11 בגיליון המעקב
        col_2025_idx = 11
        df_data[df_data.columns[col_2025_idx]] = df_data[df_data.columns[col_2025_idx]].apply(clean_currency)
        
        yaniv = df_data[df_data[df_data.columns[0]] == 'יניב'][df_data.columns[col_2025_idx]].sum()
        michal = df_data[df_data[df_data.columns[0]] == 'מיכל'][df_data.columns[col_2025_idx]].sum()

        c1, c2 = st.columns(2)
        c1.metric("יניב", f"₪{yaniv:,.0f}")
        c2.metric("מיכל", f"₪{michal:,.0f}")

    except Exception as e:
        st.error("שגיאה בשליפת נתון C15. וודא שהמבנה ב-App_Summary תקין.")

with tab2:
    st.subheader("פירוט נכסים מלא")
    # הצגת גיליון המעקב בצורה נקייה
    st.dataframe(df_data.iloc[:, [0, 1, 11]], use_container_width=True)
