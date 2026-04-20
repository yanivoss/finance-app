import streamlit as st
import pandas as pd

st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
USD_RATE = 3.7 # שער דולר מוערך

st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 110px; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.15rem; font-weight: 700; color: #333; }
    .sub-label { font-size: 0.85rem; color: #666; font-weight: bold; margin-bottom: 4px; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 4px; border-top: 1px solid #eee; padding-top: 4px; }
    h1 { text-align: center; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

try:
    df = pd.read_csv(URL_SUMMARY)

    # --- נתונים ראשיים ---
    net_now = clean_currency(df.iloc[13, 2]) # שורה 15
    debt_total = abs(clean_currency(df.iloc[11, 2])) + abs(clean_currency(df.iloc[12, 2])) # משכנתא+הלוואה

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        # כותרות ראשיות
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div class="sub-label" style="color:white; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div class="sub-label" style="color:white; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_total:,.0f}</div></div>', unsafe_allow_html=True)

        # שורת אפיקים 1: פנסיה והשתלמות
        col1, col2 = st.columns(2)
        p_y, p_m = clean_currency(df.iloc[4, 2]), clean_currency(df.iloc[6, 2])
        with col1:
            st.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{p_y + p_m:,.0f}</div><div class="split-text">יניב: ₪{p_y:,.0f} | מיכל: ₪{p_m:,.0f}</div></div>', unsafe_allow_html=True)
        
        s_y, s_m = clean_currency(df.iloc[5, 2]), clean_currency(df.iloc[7, 2])
        with col2:
            st.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{s_y + s_m:,.0f}</div><div class="split-text">יניב: ₪{s_y:,.0f} | מיכל: ₪{s_m:,.0f}</div></div>', unsafe_allow_html=True)

        # שורת אפיקים 2: מסחר וחיסכון הורים
        col3, col4 = st.columns(2)
        exc = clean_currency(df.iloc[1, 2])
        int_usd = clean_currency(df.iloc[2, 2])
        with col3:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{exc + (int_usd * USD_RATE):,.0f}</div><div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        
        parent_savings = clean_currency(df.iloc[0, 2]) # עו"ש פועלים
        with col4:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{parent_savings:,.0f}</div><div class="split-text">יניב ומיכל</div></div>', unsafe_allow_html=True)

        # שורת אפיקים 3: ילדים ונדל"ן
        col5, col6 = st.columns(2)
        kids_total = clean_currency(df.iloc[9, 2]) # שורה 11 באקסל
        with col5:
            st.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{kids_total:,.0f}</div><div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        
        house = clean_currency(df.iloc[10, 2]) # שורה 12 (דירה)
        ista = clean_currency(df.iloc[3, 2])  # שורה 5 (איסתא)
        with col6:
            st.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן ואופציות</div><div class="sub-val">₪{house + ista:,.0f}</div><div class="split-text">בית: ₪{house:,.0f} | איסתא: ₪{ista:,.0f}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
