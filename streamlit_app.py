import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="דשבורד פיננסי משפחתי", layout="wide")

# פונקציה לניקוי מספרים (מסירה סימני מטבע ופסיקים)
def clean_currency(value):
    if isinstance(value, str):
        # מנקה כל מה שאינו מספר או נקודה עשרונית
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.')
        return float(clean_val) if clean_val else 0.0
    return float(value) if value else 0.0

SHEET_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"

# טעינת נתונים
df = pd.read_csv(SHEET_URL)

# כותרת
st.title("💰 ניהול פיננסי חכם - משפחת נודלמן")
st.markdown("---")

# ניקוי העמודות (לפי השמות שראינו בטבלה שלך)
# עמודה 4 = 2023, עמודה 6 = 2024, עמודה 11 = 2025, עמודה 16 = 2026
cols = {
    '2023': df.columns[4],
    '2024': df.columns[6],
    '2025': df.columns[11],
    '2026': df.columns[16]
}

for col_name in cols.values():
    df[col_name] = df[col_name].apply(clean_currency)

# חישוב סכומים
t23 = df[cols['2023']].sum()
t24 = df[cols['2024']].sum()
t25 = df[cols['2025']].sum()
t26 = df[cols['2026']].sum()

# תצוגת מדדים עליונה - כאן תיקנתי את השגיאה של השקל
c1, c2, c3, c4 = st.columns(4)
c1.metric("סה\"כ 2023", f"₪{t23:,.0f}")
c2.metric("סה\"כ 2024", f"₪{t24:,.0f}", f"{((t24/t23)-1)*100:.1f}%" if t23 != 0 else None)
c3.metric("סה\"כ 2025", f"₪{t25:,.0f}", f"{((t25/t24)-1)*100:.1f}%" if t24 != 0 else None)
c4.metric("תחזית 2026", f"₪{t26:,.0f}", f"{((t26/t25)-1)*100:.1f}%" if t25 != 0 else None)

st.markdown("### צמיחת הון לאורך זמן")
chart_data = pd.DataFrame({
    'שנה': ['2023', '2024', '2025', '2026'],
    'סה"כ הון': [t23, t24, t25, t26]
})
fig_growth = px.bar(chart_data, x='שנה', y='סה"כ הון', color='שנה', 
                 color_discrete_sequence=px.colors.sequential.Greens_r)
st.plotly_chart(fig_growth, use_container_width=True)

st.markdown("### חלוקת נכסים לפי חוסך (2025)")
# פילוח לפי שם החוסך (עמודה 0)
fig_pie = px.pie(df, values=cols['2025'], names=df.columns[0], hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

with st.expander("לצפייה בטבלה המלאה"):
    st.dataframe(df)
