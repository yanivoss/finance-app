import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="דשבורד פיננסי משפחתי", layout="wide", initial_sidebar_state="collapsed")

# פונקציה לניקוי מספרים (מסירה סימני ₪ ופסיקים)
def clean_currency(value):
    if isinstance(value, str):
        return float(value.replace('₪', '').replace(',', '').strip())
    return value

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTl6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?output=csv"

# טעינת נתונים
df = pd.read_csv(SHEET_URL)

# כותרת
st.title("💰 ניהול פיננסי חכם - משפחת נודלמן")
st.markdown("---")

# ניקוי העמודות הרלוונטיות (נבחר את עמודות השווי)
cols_to_clean = ['שווי', 'שווי.1', 'שווי.2', 'שווי.3']
for col in cols_to_clean:
    df[col] = df[col].apply(clean_currency)

# חישוב סכומים לכל שנה
total_2023 = df['שווי'].sum()
total_2024 = df['שווי.1'].sum()
total_2025 = df['שווי.2'].sum()
total_2026 = df['שווי.3'].sum()

# תצוגת מדדים עליונה
col1, col2, col3, col4 = st.columns(4)
col1.metric("סה"כ 2023", f"₪{total_2023:,.0f}")
col2.metric("סה"כ 2024", f"₪{total_2024:,.0f}", f"{((total_2024/total_2023)-1)*100:.1f}%")
col3.metric("סה"כ 2025", f"₪{total_2025:,.0f}", f"{((total_2025/total_2024)-1)*100:.1f}%")
col4.metric("תחזית 2026", f"₪{total_2026:,.0f}", f"{((total_2026/total_2025)-1)*100:.1f}%")

st.markdown("### צמיחת הון לאורך זמן")
# הכנת נתונים לגרף
chart_data = pd.DataFrame({
    'שנה': ['2023', '2024', '2025', '2026'],
    'סה"כ הון': [total_2023, total_2024, total_2025, total_2026]
})
fig_growth = px.bar(chart_data, x='שנה', y='סה"כ הון', text_auto='.2s', color='שנה', color_discrete_sequence=px.colors.sequential.Greens_r)
st.plotly_chart(fig_growth, use_container_width=True)

# פילוח לפי חוסך
st.markdown("### חלוקת נכסים לפי חוסך (2025)")
fig_pie = px.pie(df, values='שווי.2', names='שם החוסך', hole=0.4, title="פילוח שווי 2025")
st.plotly_chart(fig_pie)

# הצגת הטבלה המלאה בסוף למי שרוצה פרטים
with st.expander("לצפייה בטבלה המלאה"):
    st.dataframe(df)
