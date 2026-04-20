import streamlit as st
import pandas as pd
import plotly.express as px # החזרתי אותה כדי שלא יצעק על הגרפים בטאב 2

# הגדרות עמוד
st.set_page_config(page_title="Noodelman Finance", layout="wide")

# פונקציית ניקוי - הפעם הוספתי טיפול גם בערכים ריקים (NaN)
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# טעינת נתונים
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"
df = pd.read_csv(SHEET_URL)

# מיפוי עמודות (לפי הסדר בגיליון שלך)
# 4=2023, 6=2024, 11=2025
cols = {'name': df.columns[0], 'type': df.columns[1], '2024': df.columns[6], '2025': df.columns[11]}
for c in ['2024', '2025']:
    df[cols[c]] = df[cols[c]].apply(clean_currency)

# עיצוב CSS למרכז הכל ולהגדיל מספרים
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 2.5rem !important; font-weight: 700; color: #1E88E5; }
    [data-testid="stMetricLabel"] { justify-content: center; font-size: 1.2rem !important; }
    h1, h2, h3 { text-align: center !important; color: #31333F; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 הון משפחת נודלמן")

# טאבים
tab1, tab2, tab3 = st.tabs(["🏠 מבט על", "📊 פילוח נכסים", "📋 רשימה מלאה"])

with tab1:
    total_25 = df[cols['2025']].sum()
    total_24 = df[cols['2024']].sum()
    diff = total_25 - total_24
    pct = (diff / total_24 * 100) if total_24 != 0 else 0

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric(label="סה\"כ הון נטו (2025)", value=f"₪{total_25:,.0f}", delta=f"{pct:.1f}% מ-2024")
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="גידול שנתי", value=f"₪{diff:,.0f}")
    with c2:
        # חלוקה בין יניב למיכל כבר בדף הראשי במספרים
        yaniv = df[df[cols['name']] == 'יניב'][cols['2025']].sum()
        michal = df[df[cols['name']] == 'מיכל'][cols['2025']].sum()
        st.write(f"**יניב:** ₪{yaniv:,.0f}")
        st.write(f"**מיכל:** ₪{michal:,.0f}")

with tab2:
    # כאן נשאיר את הגרף עוגה כי הוא טוב להבנת "איפה הכסף"
    fig = px.pie(df, values=cols['2025'], names=cols['type'], hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(df[[cols['name'], cols['type'], cols['2025']]].sort_values(by=cols['2025'], ascending=False), use_container_width=True)
