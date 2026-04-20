import streamlit as st
import pandas as pd
import urllib.request
import io

st.set_page_config(page_title="Noodelman Finance", layout="wide")

# פונקציה לטעינת נתונים שעוקפת חסימות HTTP
def load_data_from_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return pd.read_csv(io.StringIO(response.read().decode('utf-8')))

def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# הגדרות
BASE_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"
GID_SUMMARY = "1388477026"
GID_DATA = "152067713"

try:
    # טעינה עם ה"עקיפה"
    df_summary = load_data_from_url(f"{BASE_URL}&gid={GID_SUMMARY}")
    df_data = load_data_from_url(f"{BASE_URL}&gid={GID_DATA}")

    st.title("💰 הון משפחת נודלמן")

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט נכסים"])

    with tab1:
        # שליפת C15 (אינדקס 13, עמודה 2)
        total_25 = clean_currency(df_summary.iloc[13, 2])
        # שליפת 2024 (נניח עמודה B, אינדקס 1)
        total_24 = clean_currency(df_summary.iloc[13, 1])
        
        diff = total_25 - total_24
        pct = (diff / total_24 * 100) if total_24 != 0 else 0

        st.metric(label="סה\"כ הון נטו (מעודכן)", value=f"₪{total_25:,.0f}", delta=f"{pct:.1f}%")
        
        st.divider()
        
        # חישוב יניב/מיכל מגיליון המעקב
        col_25_name = df_data.columns[11]
        df_data[col_25_name] = df_data[col_25_name].apply(clean_currency)
        
        y_val = df_data[df_data[df_data.columns[0]] == 'יניב'][col_25_name].sum()
        m_val = df_data[df_data[df_data.columns[0]] == 'מיכל'][col_25_name].sum()

        c1, c2 = st.columns(2)
        c1.metric("יניב", f"₪{y_val:,.0f}")
        c2.metric("מיכל", f"₪{m_val:,.0f}")

    with tab2:
        st.dataframe(df_data.iloc[:, [0, 1, 11]], use_container_width=True)

except Exception as e:
    st.error(f"עדיין יש בעיית גישה לנתונים. שגיאה: {e}")
    st.info("וודא שהגדרת 'Anyone with the link' ב-Share בגוגל שיטס.")
