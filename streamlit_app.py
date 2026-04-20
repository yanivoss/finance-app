import streamlit as st
import pandas as pd

# הגדרות עמוד למראה אפליקטיבי
st.set_page_config(page_title="Noodelman Finance", layout="wide")

# פונקציית ניקוי נתונים
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        # מנקה הכל חוץ ממספרים, נקודה וסימן מינוס
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# הלינקים המדויקים ששלחת
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"

# עיצוב כותרת ו-Metrics
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 15px; border-radius: 15px; text-align: center; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 2.2rem !important; font-weight: 700; color: #1E88E5; }
    [data-testid="stMetricLabel"] { justify-content: center; font-size: 1.1rem !important; }
    h1, h2, h3 { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 הון משפחת נודלמן")

try:
    # טעינת הנתונים
    df_summary = pd.read_csv(URL_SUMMARY)
    df_data = pd.read_csv(URL_DATA)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט נכסים"])

    with tab1:
        # שליפת נתון C15 מגיליון App_Summary
        # שורה 15 באקסל = אינדקס 13 | עמודה C = אינדקס 2
        val_2025 = clean_currency(df_summary.iloc[13, 2])
        # שליפת נתון 2024 (עמודה B = אינדקס 1)
        val_2024 = clean_currency(df_summary.iloc[13, 1])
        
        diff = val_2025 - val_2024
        pct = (diff / val_2024 * 100) if val_2024 != 0 else 0

        st.markdown("<br>", unsafe_allow_html=True)
        st.metric(label="סה\"כ הון נטו (2025)", value=f"₪{val_2025:,.0f}", delta=f"{pct:.1f}%")
        
        st.divider()
        
        # חישוב יניב ומיכל מתוך גיליון המעקב (URL_DATA)
        # נשתמש בעמודה האחרונה של 2025 (בדרך כלל עמודה 11 או האחרונה שקיימת)
        col_25_idx = 11 if len(df_data.columns) > 11 else -1
        df_data.iloc[:, col_25_idx] = df_data.iloc[:, col_25_idx].apply(clean_currency)
        
        yaniv = df_data[df_data.iloc[:, 0] == 'יניב'].iloc[:, col_25_idx].sum()
        michal = df_data[df_data.iloc[:, 0] == 'מיכל'].iloc[:, col_25_idx].sum()

        c1, c2 = st.columns(2)
        c1.metric("יניב", f"₪{yaniv:,.0f}")
        c2.metric("מיכל", f"₪{michal:,.0f}")

    with tab2:
        st.subheader("פירוט נכסים מגיליון המעקב")
        # הצגת עמודות: חוסך, אפיק, ושנת 2025
        st.dataframe(df_data.iloc[0:12, [0, 1, col_25_idx]], use_container_width=True)

except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
    st.info("וודא שהגדרת 'Anyone with the link' ופרסמת את כל הגיליונות (Entire Document).")
