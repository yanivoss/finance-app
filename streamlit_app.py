import streamlit as st
import pandas as pd

st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

def clean_val(value):
    """פונקציה חסינה לניקוי ערכים כספיים"""
    if isinstance(value, (int, float)): return float(value)
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        try: return float(clean)
        except: return 0.0
    return 0.0

URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 100px; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.1rem; font-weight: 700; color: #333; margin-top: 2px; }
    .sub-label { font-size: 0.85rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 4px; }
    h1 { text-align: center; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    # עמודת ערך נוכחי בגיליון מעקב (עמודה L = אינדקס 11)
    VAL_COL = 11

    # נתונים מ-App_Summary
    net_now = clean_val(df_s.iloc[13, 2])
    debt = abs(clean_val(df_s.iloc[11, 2])) + abs(clean_val(df_s.iloc[12, 2]))

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div class="sub-label" style="color:white; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div class="sub-label" style="color:white; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt:,.0f}</div></div>', unsafe_allow_html=True)

        # פנסיות והשתלמות
        r1c1, r1c2 = st.columns(2)
        py, pm = clean_val(df_s.iloc[4, 2]), clean_val(df_s.iloc[6, 2])
        r1c1.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{py+pm:,.0f}</div><div class="split-text">יניב: ₪{py:,.0f} | מיכל: ₪{pm:,.0f}</div></div>', unsafe_allow_html=True)
        
        sy, sm = clean_val(df_s.iloc[5, 2]), clean_val(df_s.iloc[7, 2])
        r1c2.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{sy+sm:,.0f}</div><div class="split-text">יניב: ₪{sy:,.0f} | מיכל: ₪{sm:,.0f}</div></div>', unsafe_allow_html=True)

        # מסחר וחיסכון הורים (C10)
        r2c1, r2c2 = st.columns(2)
        exc = clean_val(df_s.iloc[1, 2])
        int_usd = clean_val(df_s.iloc[2, 2])
        r2c1.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{exc+(int_usd*USD_RATE):,.0f}</div><div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        
        parent_s = clean_val(df_s.iloc[8, 2]) # תא C10
        r2c2.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{parent_s:,.0f}</div><div class="split-text">יניב ומיכל</div></div>', unsafe_allow_html=True)

        # ילדים (סריקה מגיליון מעקב + קופת גמל שורה 16)
        r3c1, r3c2 = st.columns(2)
        provident_half = clean_val(df_d.iloc[14, VAL_COL]) / 2 # שורה 16
        
        def get_kid_sum(name):
            mask = df_d.iloc[:, 1].astype(str).str.contains(name, na=False, case=False)
            return df_d[mask].iloc[:, VAL_COL].apply(clean_val).sum()

        amit = get_kid_sum("עמית") + provident_half
        noam = get_kid_sum("נועם") + provident_half
        
        r3c1.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{amit+noam:,.0f}</div><div class="split-text">עמית: ₪{amit:,.0f} | נועם: ₪{noam:,.0f}</div></div>', unsafe_allow_html=True)
        
        house = clean_val(df_s.iloc[10, 2]) # שורה 12
        r3c2.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{house:,.0f}</div><div class="split-text">ערך הבית</div></div>', unsafe_allow_html=True)

        # אופציות איסתא
        r4c1, _ = st.columns(2)
        ista = clean_val(df_s.iloc[3, 2]) # שורה 5
        r4c1.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{ista:,.0f}</div><div class="split-text">Ista Options</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה בעדכון הנתונים: {e}")
