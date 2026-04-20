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
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

# עיצוב CSS נקי ללא קווי הפרדה
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
    
    # ניקוי עמודת הערכים הנוכחית בגיליון המעקב (עמודה 11)
    col_now_idx = 11
    df_d.iloc[:, col_now_idx] = df_d.iloc[:, col_now_idx].apply(clean_currency)

    # --- נתונים ראשיים ---
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

        # שורה 1: פנסיות והשתלמות
        col1, col2 = st.columns(2)
        p_y, p_m = clean_currency(df_s.iloc[4, 2]), clean_currency(df_s.iloc[6, 2])
        with col1:
            st.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{p_y + p_m:,.0f}</div><div class="split-text">יניב: ₪{p_y:,.0f} | מיכל: ₪{p_m:,.0f}</div></div>', unsafe_allow_html=True)
        
        s_y, s_m = clean_currency(df_s.iloc[5, 2]), clean_currency(df_s.iloc[7, 2])
        with col2:
            st.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{s_y + s_m:,.0f}</div><div class="split-text">יניב: ₪{s_y:,.0f} | מיכל: ₪{s_m:,.0f}</div></div>', unsafe_allow_html=True)

        # שורה 2: מסחר וחיסכון הורים (תוקן ל-C10)
        col3, col4 = st.columns(2)
        exc = clean_currency(df_s.iloc[1, 2])
        int_usd = clean_currency(df_s.iloc[2, 2])
        with col3:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{exc + (int_usd * USD_RATE):,.0f}</div><div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        
        parent_savings = clean_currency(df_s.iloc[8, 2]) # תא C10 (אינדקס 8)
        with col4:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{parent_savings:,.0f}</div><div class="split-text">יניב ומיכל</div></div>', unsafe_allow_html=True)

        # שורה 3: חיסכון ילדים (חישוב מורכב)
        col5, col6 = st.columns(2)
        
        # חישוב קופת גמל (שורה 16 בגיליון מעקב = אינדקס 14) חלקי 2
        provident_fund_half = clean_currency(df_d.iloc[14, col_now_idx]) / 2
        # עמית (נניח שורה 14 במעקב) | נועם (נניח שורה 15 במעקב)
        amit_base = clean_currency(df_d[df_d.iloc[:,1].str.contains("עמית", na=False)].iloc[:, col_now_idx].sum())
        noam_base = clean_currency(df_d[df_d.iloc[:,1].str.contains("נועם", na=False)].iloc[:, col_now_idx].sum())
        
        total_amit = amit_base + provident_fund_half
        total_noam = noam_base + provident_fund_half
        
        with col5:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">👦👧 חיסכון ילדים</div>
                    <div class="sub-val">₪{total_amit + total_noam:,.0f}</div>
                    <div class="split-text">עמית: ₪{total_amit:,.0f} | נועם: ₪{total_noam:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        # שורה 4: הפרדת נדל"ן ואיסתא
        house = clean_currency(df_s.iloc[10, 2]) # שורה 12
        with col6:
             st.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{house:,.0f}</div><div class="split-text">ערך הבית</div></div>', unsafe_allow_html=True)

        col7, col8 = st.columns(2)
        ista = clean_currency(df_s.iloc[3, 2]) # שורה 5
        with col7:
            st.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{ista:,.0f}</div><div class="split-text">Ista Options</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
