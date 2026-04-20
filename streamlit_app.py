import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות עמוד למראה אפליקטיבי
st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

# פונקציית ניקוי נתונים
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# הלינק המנצח
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"

# טעינה וניקוי
df = pd.read_csv(SHEET_URL)
cols = {'name': df.columns[0], 'type': df.columns[1], '2023': df.columns[4], 
        '2024': df.columns[6], '2025': df.columns[11], '2026': df.columns[16]}

for c in ['2023', '2024', '2025', '2026']:
    df[cols[c]] = df[cols[c]].apply(clean_currency)

# --- עיצוב כותרת ממורכזת ---
st.markdown("""
    <style>
    .main-title { text-align: center; color: #1E88E5; font-size: 2.2rem; font-weight: bold; margin-bottom: 0px; }
    .sub-title { text-align: center; color: gray; font-size: 1rem; margin-top: 0px; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    </style>
    <div class="main-title">💰 הון משפחת נודלמן</div>
    <div class="sub-title">ניהול פיננסי חכם בזמן אמת</div>
    <br>
""", unsafe_allow_html=True)

# --- יצירת טאבים (עמודים בתוך האפליקציה) ---
tab1, tab2, tab3 = st.tabs(["🏠 מבט על", "👤 אישי", "📊 פירוט"])

with tab1:
    # חישובים
    total_25 = df[cols['2025']].sum()
    total_24 = df[cols['2024']].sum()
    diff = total_25 - total_24
    growth = (diff / total_24 * 100) if total_24 != 0 else 0

    # מדדים ראשיים
    st.metric("סה\"כ הון (2025)", f"₪{total_25:,.0f}", f"{growth:.1f}%")
    
    st.markdown("---")
    st.write("**התפתחות שנתית**")
    hist_data = pd.DataFrame({
        'שנה': ['23', '24', '25'],
        'הון': [df[cols['2023']].sum(), df[cols['2024']].sum(), total_25]
    })
    fig_line = px.line(hist_data, x='שנה', y='הון', markers=True)
    fig_line.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

with tab2:
    st.subheader("פילוח לפי חוסך")
    yaniv = df[df[cols['name']] == 'יניב'][cols['2025']].sum()
    michal = df[df[cols['name']] == 'מיכל'][cols['2025']].sum()
    
    col_y, col_m = st.columns(2)
    col_y.metric("יניב", f"₪{yaniv:,.0f}")
    col_m.metric("מיכל", f"₪{michal:,.0f}")
    
    st.markdown("---")
    st.write("**איפה הכסף מושקע?**")
    fig_pie = px.pie(df, values=cols['2025'], names=cols['type'], hole=0.4)
    fig_pie.update_layout(margin=dict(l=20, r=20, t=0, b=0), height=350, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.subheader("כל הנכסים")
    # טבלה נקייה וקריאה
    display_df = df[[cols['name'], cols['type'], cols['2025']]].copy()
    display_df.columns = ['חוסך', 'אפיק', 'שווי 2025']
    st.dataframe(display_df.sort_values('שווי 2025', ascending=False), use_container_width=True)
