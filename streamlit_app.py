import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import yfinance as yf

# הגדרת דף
st.set_page_config(
    page_title="Noodelman Finance", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="💰"
)

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
    """חישוב שינוי עם ניקוי ערכים מובנה"""
    c, s = clean_val(current), clean_val(start)
    if s == 0: return ""
    diff = c - s
    pct = (diff / s) * 100
    color = "#4CAF50" if diff >= 0 else "#F44336"
    arrow = "▲" if diff >= 0 else "▼"
    nis_text = f" (₪{abs(diff):,.0f})" if show_NIS else ""
    return f'<div style="color: {color}; font-size: 0.75rem; font-weight: bold; margin-top: 2px;">{arrow} {abs(pct):.1f}%{nis_text}</div>'

def get_market_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="2d")
        if len(data) < 2: return 0, 0, "#666", ""
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        color = "#4CAF50" if change_pct >= 0 else "#F44336"
        arrow = "▲" if change_pct >= 0 else "▼"
        return current_price, change_pct, color, arrow
    except:
        return 0, 0, "#666", ""

# נתונים קבועים
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

# --- עיצוב CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .ticker-box { 
        background: white; border: none; border-radius: 12px; padding: 10px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-height: 85px; display: flex; flex-direction: column; justify-content: center;
    }
    .t-label { font-size: 0.75rem; color: #888; font-weight: 600; text-transform: uppercase; margin-bottom: 2px; }
    .t-val { font-size: 1rem; font-weight: 800; color: #222; }
    .main-card { padding: 20px; border-radius: 18px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .sub-card { 
        background: white; border: none; padding: 15px; border-radius: 16px; text-align: center; margin-bottom: 12px; 
        min-height: 145px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        display: flex; flex-direction: column; justify-content: center;
    }
    .sub-val { font-size: 1.2rem; font-weight: 800; color: #1a1a1a; margin-top: 4px; }
    .split-text { font-size: 0.75rem; color: #999; margin-top: 8px; border-top: 1px solid #f0f0f0; padding-top: 8px; }
    .update-time { text-align: center; color: #94a3b8; font-size: 0.8rem; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    sp_p, sp_c, sp_col, sp_a = get_market_data("^GSPC")
    btc_p, btc_c, btc_col, btc_a = get_market_data("BTC-USD")
    
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    last_update = datetime.now(jerusalem_tz).strftime("%H:%M %d/%m/%Y")

    st.markdown("<h1 style='text-align:center;'>הון משפחת נודלמן</h1>", unsafe_allow_html=True)
    
    # שורת מדדים
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="ticker-box"><div class="t-label">💵 דולר/שקל</div><div class="t-val">₪{USD_RATE}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="ticker-box"><div class="t-label">📈 S&P 500</div><div class="t-val">{sp_p:,.0f}</div><div style="color:{sp_col}; font-size:0.75rem; font-weight:bold;">{sp_a} {abs(sp_c):.1f}%</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="ticker-box"><div class="t-label">₿ Bitcoin</div><div class="t-val">${btc_p:,.0f}</div><div style="color:{btc_col}; font-size:0.75rem; font-weight:bold;">{btc_a} {abs(btc_c):.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="update-time">עודכן לאחרונה: {last_update}</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        # --- הון נטו והתחייבויות ---
        c1, c2 = st.columns(2)
        n_now, n_start = clean_val(df_s.iloc[13, 2]), clean_val(df_s.iloc[13, 4])
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);"><div style="font-size:0.85rem; opacity:0.8;">הון נטו</div><div style="font-size:1.8rem; font-weight:800;">₪{n_now:,.0f}</div>{get_delta_html(n_now, n_start)}</div>', unsafe_allow_html=True)
        with c2:
            mort, loan = abs(clean_val(df_s.iloc[11, 2])), abs(clean_val(df_s.iloc[12, 2]))
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #ef4444, #b91c1c);"><div style="font-size:0.85rem; opacity:0.8;">התחייבויות</div><div style="font-size:1.8rem; font-weight:800;">₪{mort+loan:,.0f}</div><div style="font-size:0.75rem; font-weight:bold; margin-top:2px;">ניהול חוב פעיל</div></div>', unsafe_allow_html=True)

        # --- שורה 1: פנסיות והשתלמות ---
        r1c1, r1c2 = st.columns(2)
        py_n, py_s = clean_val(df_s.iloc[4, 2]), clean_val(df_s.iloc[4, 4])
        pm_n, pm_s = clean_val(df_s.iloc[6, 2]), clean_val(df_s.iloc[6, 4])
        r1c1.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{py_n+pm_n:,.0f}</div>{get_delta_html(py_n+pm_n, py_s+pm_s)}<div class="split-text">יניב: ₪{py_n:,.0f} {get_delta_html(py_n, py_s, False)} | מיכל: ₪{pm_n:,.0f} {get_delta_html(pm_n, pm_s, False)}</div></div>', unsafe_allow_html=True)
        
        sy_n, sy_s = clean_val(df_s.iloc[5, 2]), clean_val(df_s.iloc[5, 4])
        sm_n, sm_s = clean_val(df_s.iloc[7, 2]), clean_val(df_s.iloc[7, 4])
        r1c2.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{sy_n+sm_n:,.0f}</div>{get_delta_html(sy_n+sm_n, sy_s+sm_s)}<div class="split-text">יניב: ₪{sy_n:,.0f} {get_delta_html(sy_n, sy_s, False)} | מיכל: ₪{sm_n:,.0f} {get_delta_html(sm_n, sm_s, False)}</div></div>', unsafe_allow_html=True)

        # --- שורה 2: תיק מסחר והורים ---
        r2c1, r2c2 = st.columns(2)
        exc_n, exc_s = clean_val(df_s.iloc[1, 2]), clean_val(df_s.iloc[1, 4])
        int_n, int_s = clean_val(df_s.iloc[2, 2]), clean_val(df_s.iloc[2, 4])
        tr_n, tr_s = exc_n + (int_n * USD_RATE), exc_s + (int_s * USD_RATE)
        r2c1.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{tr_n:,.0f}</div>{get_delta_html(tr_n, tr_s)}<div class="split-text">אקסלנס: ₪{exc_n:,.0f} {get_delta_html(exc_n, exc_s, False)} | אינטראקטיב: ${int_n:,.0f} {get_delta_html(int_n, int_s, False)}</div></div>', unsafe_allow_html=True)
        
        p_n = clean_val(df_d.iloc[5, 15]) + clean_val(df_d.iloc[6, 15]) + clean_val(df_d.iloc[11, 15])
        p_s = clean_val(df_d.iloc[5, 14]) + clean_val(df_d.iloc[6, 14]) + clean_val(df_d.iloc[11, 14])
        r2c2.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{p_n:,.0f}</div>{get_delta_html(p_n, p_s)}<div class="split-text">נזיל</div></div>', unsafe_allow_html=True)

        # --- שורה 3: ילדים וחופשה ---
        r3c1, r3c2 = st.columns(2)
        k_n, k_s = clean_val(df_s.iloc[9, 2]), clean_val(df_s.iloc[9, 4])
        r3c1.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{k_n:,.0f}</div>{get_delta_html(k_n, k_s)}<div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        
        vacation = clean_val(df_d.iloc[10, 15])
        r3c2.markdown(f'<div class="sub-card" style="border-right: 5px solid #3b82f6;"><div class="sub-label">🏖️ חופשה</div><div class="sub-val" style="color: #3b82f6;">₪{vacation:,.0f}</div><div class="split-text">טיול 2027</div></div>', unsafe_allow_html=True)

        # --- שורה 4: נדל"ן ואיסתא ---
        r4c1, r4c2 = st.columns(2)
        h_n, h_s = clean_val(df_s.iloc[10, 2]), clean_val(df_s.iloc[10, 4])
        ltv = (mort / h_n * 100) if h_n > 0 else 0
        r4c1.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{h_n:,.0f}</div>{get_delta_html(h_n, h_s)}<div style="font-size:0.7rem; font-weight:bold; color:#888; margin-top:5px;">LTV: {ltv:.1f}%</div></div>', unsafe_allow_html=True)
        
        ista_n, ista_s = clean_val(df_s.iloc[3, 2]), clean_val(df_s.iloc[3, 4])
        r4c2.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{ista_n:,.0f}</div>{get_delta_html(ista_n, ista_s)}<div class="split-text">ממתין למימוש</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
