import streamlit as st
import pandas as pd

st.set_page_config(page_title="Noodelman Finance", layout="wide")

# פונקציית ניקוי
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# הקישורים הישירים (שים לב למבנה השונה מעט)
url_summary = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTl6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
url_data = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTl6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=152067713&single=true&output=csv"

st.title("💰 הון משפחת נודלמן")

try:
    # טעינה ישירה של פנדס - הוספתי הגנה למקרה שהקובץ ריק
    df_summary = pd.read_csv(url_summary)
    df_data = pd.read_csv(url_data)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט נכסים"])

    with tab1:
        # בדיקה אם אנחנו בשורה הנכונה (C15 בסיכום)
        # שורה 15 באקסל היא אינדקס 13 ב-DataFrame
        total_25 = clean_currency(df_summary.iloc[13, 2])
        total_24 = clean_currency(df_summary.iloc[13, 1])
        
        diff = total_25 - total_24
        pct = (diff / total_24 * 100) if total_24 != 0 else 0

        st.metric(label="סה\"כ הון נטו", value=f"₪{total_25:,.0f}", delta=f"{pct:.1f}%")
        st.divider()

        # חישוב יניב/מיכל מגיליון המעקב (עמודה 11 היא 2025)
        col_25 = df_data.columns[11]
        df_data[col_25] = df_data[col_25].apply(clean_currency)
        y_val = df_data[df_data[df_data.columns[0]] == 'יניב'][col_25].sum()
        m_val = df_data[df_data[df_data.columns[0]] == 'מיכל'][col_25].sum()

        c1, c2 = st.columns(2)
        c1.metric("יניב", f"₪{y_val:,.0f}")
        c2.metric("מיכל", f"₪{m_val:,.0f}")

    with tab2:
        st.dataframe(df_data.iloc[:, [0, 1, 11]], use_container_width=True)

except Exception as e:
    st.error(f"שגיאה בחיבור: {e}")
    st.write("בדיקה זמנית - מה הקישור רואה?")
    st.write(url_summary)
