import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import yfinance as yf

# הגדרת דף
st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed", page_icon="💰")

# --- פונקציות עזר ---
def clean_val(value):
    if isinstance(value, (int, float)): return float(value)
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        try: return float(clean)
        except: return 0.0
    return 0.0

def get_delta_html(current, start, show_NIS=True):
    """מייצרת מחרוזת שינוי מעוצבת"""
    if start == 0: return ""
    diff = current - start
    pct = (diff / start) * 100
    color = "#4CAF50" if diff >= 0 else "#F44336"
    arrow = "▲" if diff >= 0 else "▼"
    nis_text = f" (₪{abs(diff):,.0f})" if show_NIS else ""
    return f'<span style="color: {color}; font-size: 0.75rem; font-weight: bold;">{arrow} {abs(pct):.1f}%{nis_text}</span>'

# --- נתונים ועיצוב ---
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-card { padding: 20px; border-radius: 18px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .sub-card { 
        background: white; padding: 15px; border-radius: 16px; text-align: center; margin-bottom: 12px; 
        min-height: 150px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        display: flex; flex-direction: column; justify-content: center;
    }
    .sub-val { font-size: 1.2rem; font-weight: 800; color: #1a1a1a; margin-bottom: 2px; }
    .split-text { font-size: 0.75rem; color: #666; margin-top: 8px; border-top: 1px solid #f0f0f0; padding-top: 8px; line-height: 1.4; }
    .delta-inline { font-size: 0.7rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    st.markdown("<h1 style='text-align:center;'>הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    # 1. הון נטו - חישוב דלתא מדויק
    net_now = clean_val(df_s.iloc[13, 2])
    net_start = clean_val(df_s.iloc[13, 4])
    
    # 2. שליפת נתוני פירוט (עבור הפרדה בשינוי)
    # פנסיות
    py_n, py_s = clean_val(df_s.iloc[4, 2]), clean_val(df_s.iloc[4, 4])
    pm_n, pm_s = clean_val(df_s.iloc[6, 2]), clean_val(df_s.iloc[6, 4])
    # השתלמות
    sy_n, sy_s = clean_val(df_s.iloc[5, 2]), clean_val(df_s.iloc[5, 4])
    sm_n, sm_s = clean_val(df_s.iloc[7, 2]), clean_val(df_s.iloc[7, 4])
    # תיק מסחר
    exc_n, exc_s = clean_val(df_s.iloc[1, 2]), clean_val(df_s.iloc[1, 4])
    int_n, int_s = clean_val(df_s.iloc[2, 2]), clean_val(df_s.iloc[2, 4]) # בדולר
    
    # חסכונות הורים (מתוך גיליון DATA - נניח עמודה 15 היא הנוכחי ו-14 היא תחילת שנה לצורך הדוגמה)
    # אם בגיליון DATA אין עמודת "תחילת שנה", נשווה לערך קודם ידוע או נמשוך מטור אחר
    p_now = clean_val(df_d.iloc[5, 15]) + clean_val(df_d.iloc[6, 15]) + clean_val(df_d.iloc[11, 15])
    p_start = clean_val(df_d.iloc[5, 14]) + clean_val(df_d.iloc[6, 14]) + clean_val(df_d.iloc[11, 14])

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        # שורת הון והתחייבויות
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'''<div class="main-card" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);">
                <div style="font-size:0.85rem; opacity:0.8;">הון נטו</div>
                <div style="font-size:1.8rem; font-weight:800;">₪{net_now:,.0f}</div>
                {get_delta_html(net_now, net_start)}
            </div>''', unsafe_allow_html=True)
        
        with c2:
            mortgage_n = abs(clean_val(df_s.iloc[11, 2]))
            loan_n = abs(clean_val(df_s.iloc[12, 2]))
            total_debt = mortgage_n + loan_n
            # נחשב ידנית לוגיקת חוב (ירידה = ירוק)
            st.markdown(f'''<div class="main-card" style="background: linear-gradient(135deg, #ef4444, #b91c1c);">
                <div style="font-size:0.85rem; opacity:0.8;">התחייבויות</div>
                <div style="font-size:1.8rem; font-weight:800;">₪{total_debt:,.0f}</div>
                <div style="font-size:0.75rem;">ניהול סיכונים פעיל</div>
            </div>''', unsafe_allow_html=True)

        # פירוט נכסים
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown(f'''<div class="sub-card">
                <div class="sub-label">🏦 פנסיות</div>
                <div class="sub-val">₪{py_n+pm_n:,.0f}</div>
                {get_delta_html(py_n+pm_n, py_s+pm_s)}
                <div class="split-text">
                    יניב: ₪{py_n:,.0f} {get_delta_html(py_n, py_s, False)}<br>
                    מיכל: ₪{pm_n:,.0f} {get_delta_html(pm_n, pm_s, False)}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r1c2:
            st.markdown(f'''<div class="sub-card">
                <div class="sub-label">📈 השתלמות</div>
                <div class="sub-val">₪{sy_n+sm_n:,.0f}</div>
                {get_delta_html(sy_n+sm_n, sy_s+sm_s)}
                <div class="split-text">
                    יניב: ₪{sy_n:,.0f} {get_delta_html(sy_n, sy_s, False)}<br>
                    מיכל: ₪{sm_n:,.0f} {get_delta_html(sm_n, sm_s, False)}
                </div>
            </div>''', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            total_tr_n = exc_n + (int_n * USD_RATE)
            total_tr_s = exc_s + (int_s * USD_RATE)
            st.markdown(f'''<div class="sub-card">
                <div class="sub-label">💎 תיק מסחר</div>
                <div class="sub-val">₪{total_tr_n:,.0f}</div>
                {get_delta_html(total_tr_n, total_tr_s)}
                <div class="split-text">
                    אקסלנס: ₪{exc_n:,.0f} {get_delta_html(exc_n, exc_s, False)}<br>
                    אינטראקטיב: ${int_n:,.0f} {get_delta_html(int_n, int_s, False)}
                </div>
            </div>''', unsafe_allow_html=True)
            
        with r2c2:
            st.markdown(f'''<div class="sub-card">
                <div class="sub-label">💰 חסכונות הורים</div>
                <div class="sub-val">₪{p_now:,.0f}</div>
                {get_delta_html(p_now, p_start)}
                <div class="split-text">נזיל וזמין</div>
            </div>''', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
