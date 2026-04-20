import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

# פונקציית ניקוי ערכים
def clean_val(value):
    if isinstance(value, (int, float)): return float(value)
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        try: return float(clean)
        except: return 0.0
    return 0.0

def get_trend_html(current, previous, invert=False):
    """יוצר אינדיקטור ויזואלי לשינוי כולל אחוזים"""
    diff = current - previous
    if abs(diff) < 1: return "" 
    
    percent = (diff / previous * 100) if previous != 0 else 0
    
    is_positive = diff > 0 if not invert else diff < 0
    color = "#4CAF50" if is_positive else "#F44336"
    icon = "🔼" if diff > 0 else "🔽"
    
    return f'''
        <div style="color: {color}; font-size: 0.82rem; font-weight: bold; margin-top: 2px;">
            {icon} ₪{abs(diff):,.0f} ({abs(percent):.1f}%)
        </div>
    '''

# כפתור ריענון ב-Sidebar
with st.sidebar:
    if st.button('🔄 רענן נתונים'):
        st.cache_data.clear()
        st.rerun()

URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

# עיצוב CSS
st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 125px; display: flex; flex-direction: column; justify-content: center; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.1rem; font-weight: 700; color: #333; margin-top: 2px; }
    .sub-label { font-size: 0.85rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 4px; border-top: 1px solid #eee; padding-top: 4px; }
    .ltv-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; margin-top: 5px; }
    .update-time { text-align: center; color: #999; font-size: 0.8rem; margin-top: -10px; margin-bottom: 20px; }
    h1 { text-align: center; font-size: 1.8rem; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    # עמודות נוכחיות (C בסיכום, P במעקב) מול קודמות (D בסיכום, O במעקב)
    C_NOW, C_PREV = 2, 3
    P_NOW, P_PREV = 15, 14
    
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    last_update = datetime.now(jerusalem_tz).strftime("%d/%m/%Y %H:%M")
    
    # שליפת נתונים וחישוב טרנדים
    net_now, net_prev = clean_val(df_s.iloc[13, C_NOW]), clean_val(df_s.iloc[13, C_PREV])
    mort_now, mort_prev = abs(clean_val(df_s.iloc[11, C_NOW])), abs(clean_val(df_s.iloc[11, C_PREV]))
    loan_now, loan_prev = abs(clean_val(df_s.iloc[12, C_NOW])), abs(clean_val(df_s.iloc[12, C_PREV]))
    debt_now, debt_prev = mort_now + loan_now, mort_prev + loan_prev
    house_val = clean_val(df_s.iloc[10, C_NOW])

    # חישוב LTV
    ltv = (mort_now / house_val * 100) if house_val > 0 else 0
    ltv_color = "#4CAF50" if ltv < 45 else "#FF9800" if ltv < 65 else "#F44336"
    ltv_status = "תקין" if ltv < 45 else "בינוני" if ltv < 65 else "גבוה"

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="update-time">נתונים מעודכנים ליום: {last_update} (זמן ירושלים)</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div class="sub-label" style="color:white; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div>{get_trend_html(net_now, net_prev)}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div class="sub-label" style="color:white; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_now:,.0f}</div>{get_trend_html(debt_now, debt_prev, invert=True)}</div>', unsafe_allow_html=True)

        # שורה 1: פנסיות והשתלמות
        r1c1, r1c2 = st.columns(2)
        py, pm = clean_val(df_s.iloc[4, C_NOW]), clean_val(df_s.iloc[6, C_NOW])
        py_p, pm_p = clean_val(df_s.iloc[4, C_PREV]), clean_val(df_s.iloc[6, C_PREV])
        r1c1.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{py+pm:,.0f}</div>{get_trend_html(py+pm, py_p+pm_p)}<div class="split-text">יניב: ₪{py:,.0f} | מיכל: ₪{pm:,.0f}</div></div>', unsafe_allow_html=True)
        
        sy, sm = clean_val(df_s.iloc[5, C_NOW]), clean_val(df_s.iloc[7, C_NOW])
        sy_p, sm_p = clean_val(df_s.iloc[5, C_PREV]), clean_val(df_s.iloc[7, C_PREV])
        r1c2.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{sy+sm:,.0f}</div>{get_trend_html(sy+sm, sy_p+sm_p)}<div class="split-text">יניב: ₪{sy:,.0f} | מיכל: ₪{sm:,.0f}</div></div>', unsafe_allow_html=True)

        # שורה 2: תיק מסחר וחסכונות הורים
        r2c1, r2c2 = st.columns(2)
        exc, int_usd = clean_val(df_s.iloc[1, C_NOW]), clean_val(df_s.iloc[2, C_NOW])
        exc_p, int_usd_p = clean_val(df_s.iloc[1, C_PREV]), clean_val(df_s.iloc[2, C_PREV])
        trade_now, trade_prev = exc+(int_usd*USD_RATE), exc_p+(int_usd_p*USD_RATE)
        r2c1.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{trade_now:,.0f}</div>{get_trend_html(trade_now, trade_prev)}<div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        
        p_now = clean_val(df_d.iloc[5, P_NOW]) + clean_val(df_d.iloc[6, P_NOW]) + clean_val(df_d.iloc[11, P_NOW])
        p_prev = clean_val(df_d.iloc[5, P_PREV]) + clean_val(df_d.iloc[6, P_PREV]) + clean_val(df_d.iloc[11, P_PREV])
        r2c2.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{p_now:,.0f}</div>{get_trend_html(p_now, p_prev)}<div class="split-text">נזיל</div></div>', unsafe_allow_html=True)

        # שורה 3: ילדים וחופשה
        r3c1, r3c2 = st.columns(2)
        k_now, k_prev = clean_val(df_s.iloc[9, C_NOW]), clean_val(df_s.iloc[9, C_PREV])
        r3c1.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{k_now:,.0f}</div>{get_trend_html(k_now, k_prev)}<div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        
        v_now, v_prev = clean_val(df_d.iloc[10, P_NOW]), clean_val(df_d.iloc[10, P_PREV])
        r3c2.markdown(f'<div class="sub-card" style="border-right: 4px solid #1E88E5;"><div class="sub-label">🏖️ חיסכון לחופשה</div><div class="sub-val" style="color: #1E88E5;">₪{v_now:,.0f}</div>{get_trend_html(v_now, v_prev)}<div class="split-text">לטיול הבא שלנו</div></div>', unsafe_allow_html=True)

        # שורה 4: נדל"ן ואיסתא
        r4c1, r4c2 = st.columns(2)
        r4c1.markdown(f"""
            <div class="sub-card">
                <div class="sub-label">🏠 נדל"ן</div>
                <div class="sub-val">₪{house_val:,.0f}</div>
                <div class="ltv-badge" style="background-color: {ltv_color}22; color: {ltv_color};">
                    LTV: {ltv:.1f}% | {ltv_status}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        ista_now, ista_prev = clean_val(df_s.iloc[3, C_NOW]), clean_val(df_s.iloc[3, C_PREV])
        r4c2.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{ista_now:,.0f}</div>{get_trend_html(ista_now, ista_prev)}<div class="split-text">ממתין למימוש</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
