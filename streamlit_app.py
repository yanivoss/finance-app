import streamlit as st
import pandas as pd

st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

def clean_currency(value):
    # אם זה כבר מספר (float/int), פשוט תחזיר אותו
    if isinstance(value, (int, float)): return float(value)
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return 0.0

URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 105px; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.15rem; font-weight: 700; color: #333; margin-top: 2px; }
    .sub-label { font-size: 0.85rem; color: #666; font-weight: bold; margin-bottom: 2px; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 4px; padding-top: 2px; }
    h1 { text-align: center; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    # עמודת הערך הנוכחי (2025) היא אינדקס 11
    col_now_idx = 11

    # --- נתונים ראשיים מסיכום ---
    net_now = clean_currency(df_s.iloc[13, 2])
    debt_total = abs(clean_currency(df_s.iloc[11, 2])) + abs(clean_currency(df_s.iloc[12, 2]))

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div class="sub-label" style="color:white; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div class="sub-label" style="color:white; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_total:,.0f}</div></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        # פנסיות
        p_y, p_m = clean_currency(df_s.iloc[4, 2]), clean_currency(df_s.iloc[6, 2])
        with col1:
            st.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{p_y + p_m:,.0f}</div><div class="split-text">יניב: ₪{p_y:,.0f} | מיכל: ₪{p_m:,.0f}</div></div>', unsafe_allow_html=True)
        # השתלמות
        s_y, s_m = clean_currency(df_s.iloc[5, 2]), clean_currency(df_s.iloc[7, 2])
        with col2:
            st.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{s_y + s_m:,.0f}</div><div class="split-text">יניב: ₪{s_y:,.0f} | מיכל: ₪{s_m:,.0f}</div></div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        # מסחר
        exc = clean_currency(df_s.iloc[1, 2])
        int_usd = clean_currency(df_s.iloc[2, 2])
        with col3:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{exc + (int_usd * USD_RATE):,.0f}</div><div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        # חסכונות הורים (C10)
        parent_savings = clean_currency(df_s.iloc[8, 2])
        with col4:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{parent_savings:,.0f}</div><div class="split-text">יניב ומיכל</div></div>', unsafe_allow_html=True)

        # --- חיסכון ילדים ---
        col5, col6 = st.columns(2)
        
        # קופת גמל - שורה 16 במעקב (אינדקס 14)
        provident_val = clean_currency(df_d.iloc[14, col_now_idx]) / 2
        
        # חיפוש ספציפי לפי טקסט בעמודה השנייה (B) וסכימה של עמודה L (אינדקס 11)
        amit_total = df_d[df_d.iloc[:, 1].str.contains("עמית", na=False, case=False)].iloc[:, col_now_idx].apply(clean_currency).sum() + provident_val
        noam_total = df_d[df_d.iloc[:, 1].str.contains("נועם", na=False, case=False)].iloc[:, col_now_idx].apply(clean_currency).sum() + provident_val
        
        with col5:
            st.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{amit_total + noam_total:,.0f}</div><div class="split-text">עמית: ₪{amit_total:,.0f} | נועם: ₪{noam_total:,.0f}</div></div>', unsafe_allow_html=True)
            
        # נדל"ן
        house = clean_currency(df_s.iloc[10, 2])
        with col6:
             st.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{house:,.0f}</div><div class="split-text">ערך הבית</div></div>', unsafe_allow_html=True)

        col7, col8 = st.columns(2)
        # איסתא
        ista = clean_currency(df_s.iloc[3, 2])
        with col7:
            st.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{ista:,.0f}</div><div class="split-text">Ista Options</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
