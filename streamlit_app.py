import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import yfinance as yf

# הגדרת דף
st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed", page_icon="💰")

# --- פונקציות עזר ---
def clean_val(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        clean = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        try: return float(clean)
        except: return 0.0
    return 0.0

def get_delta_html(current, start, is_main_card=True, show_NIS=True):
    """עיצוב דלתא - שימוש ב-SPAN למניעת שבירת DIV"""
    curr = clean_val(current)
    strt = clean_val(start)
    
    if strt == 0: 
        return '<span style="display:block; height:20px;"></span>'
    
    diff = curr - strt
    pct = (diff / abs(strt)) * 100 
    
    # צבעים
    pos_color = "#4ade80" # ירוק בהיר לכרטיס כהה
    neg_color = "#f87171" # אדום בהיר לכרטיס כהה
    pos_dark = "#16a34a"  # ירוק כהה לכרטיס לבן
    neg_dark = "#dc2626"  # אדום כהה לכרטיס לבן
    
    arrow = "▲" if diff >= 0 else "▼"
    nis_text = f" (₪{abs(diff):,.0f})" if show_NIS else ""
    
    if is_main_card:
        # בועה לכרטיסים הראשיים
        status_color = pos_color if diff >= 0 else neg_color
        return f'''
        <div style="background-color: rgba(255, 255, 255, 0.15); color: {status_color}; 
             font-size: 0.85rem; font-weight: bold; margin: 10px auto 0 auto; 
             padding: 4px 12px; border-radius: 20px; width: fit-content; border: 1px solid rgba(255, 255, 255, 0.1);">
            {arrow} {abs(pct):.1f}% <span style="font-size: 0.75rem; opacity: 0.8;">{nis_text}</span>
        </div>
        '''
    else:
        # טקסט פשוט לכרטיסים המשניים - משתמש ב-SPAN
        status_color = pos_dark if diff >= 0 else neg_dark
        return f'<span style="color: {status_color}; font-size: 0.75rem; font-weight: bold; display: block; margin-top: 2px;">{arrow} {abs(pct):.1f}%{nis_text}</span>'

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

# נתונים
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

# --- עיצוב CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .ticker-box { background: white; border-radius: 12px; padding: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-height: 85px; display: flex; flex-direction: column; justify-content: center; }
    .main-card { padding: 25px 20px; border-radius: 20px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 6px 20px rgba(0,0,0,0.15); }
    .sub-card { background: white; padding: 15px; border-radius: 16px; text-align: center; margin-bottom: 12px; min-height: 155px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: center; }
    .sub-val { font-size: 1.15rem; font-weight: 800; color: #1e293b; margin: 2px 0; }
    .sub-label { font-size: 0.85rem; color: #64748b; font-weight: 600; }
    .split-text { font-size: 0.75rem; color: #475569; margin-top: 12px; border-top: 1px solid #f1f5f9; padding-top: 10px; display: flex; justify-content: space-between; align-items: center; }
    .split-item { width: 45%; display: flex; flex-direction: column; align-items: center; }
    .update-time { text-align: center; color: #94a3b8; font-size: 0.8rem; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    sp_p, sp_c, sp_col, sp_a = get_market_data("^GSPC")
    btc_p, btc_c, btc_col, btc_a = get_market_data("BTC-USD")
    last_update = datetime.now(pytz.timezone('Asia/Jerusalem')).strftime("%H:%M %d/%m/%Y")

    st.markdown("<h1 style='text-align:center;'>הון משפחת נודלמן</h1>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="ticker-box"><div style="font-size:0.75rem; color:#888;">💵 דולר/שקל</div><div style="font-size:1rem; font-weight:800;">₪{USD_RATE}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="ticker-box"><div style="font-size:0.75rem; color:#888;">📈 S&P 500</div><div style="font-size:1rem; font-weight:800;">{sp_p:,.0f}</div><div style="color:{sp_col}; font-size:0.75rem; font-weight:bold;">{sp_a} {abs(sp_c):.1f}%</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="ticker-box"><div style="font-size:0.75rem; color:#888;">₿ Bitcoin</div><div style="font-size:1rem; font-weight:800;">${btc_p:,.0f}</div><div style="color:{btc_col}; font-size:0.75rem; font-weight:bold;">{btc_a} {abs(btc_c):.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="update-time">עודכן: {last_update}</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        n_now, n_start = df_s.iloc[13, 2], df_s.iloc[13, 4]
        with c1: 
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"><div class="sub-label" style="color:white; opacity:0.9;">הון נטו</div><div style="font-size:2.2rem; font-weight:800;">₪{clean_val(n_now):,.0f}</div>{get_delta_html(n_now, n_start, True)}</div>', unsafe_allow_html=True)
        
        debt_now = abs(clean_val(df_s.iloc[11, 2])) + abs(clean_val(df_s.iloc[12, 2]))
        debt_start = abs(clean_val(df_s.iloc[11, 4])) + abs(clean_val(df_s.iloc[12, 4]))
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #dc2626, #b91c1c);"><div class="sub-label" style="color:white; opacity:0.9;">התחייבויות</div><div style="font-size:2.2rem; font-weight:800;">₪{debt_now:,.0f}</div>{get_delta_html(debt_now, debt_start, True)}</div>', unsafe_allow_html=True)

        # --- כרטיסים משניים ---
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            py_n, py_s = df_s.iloc[4, 2], df_s.iloc[4, 4]
            pm_n, pm_s = df_s.iloc[6, 2], df_s.iloc[6, 4]
            st.markdown(f'''<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{clean_val(py_n)+clean_val(pm_n):,.0f}</div>{get_delta_html(clean_val(py_n)+clean_val(pm_n), clean_val(py_s)+clean_val(pm_s), False)}
                <div class="split-text">
                    <div class="split-item">יניב: ₪{clean_val(py_n):,.0f}{get_delta_html(py_n, py_s, False, False)}</div>
                    <div style="border-left: 1px solid #eee; height: 30px;"></div>
                    <div class="split-item">מיכל: ₪{clean_val(pm_n):,.0f}{get_delta_html(pm_n, pm_s, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)
        with r1c2:
            sy_n, sy_s = df_s.iloc[5, 2], df_s.iloc[5, 4]
            sm_n, sm_s = df_s.iloc[7, 2], df_s.iloc[7, 4]
            st.markdown(f'''<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{clean_val(sy_n)+clean_val(sm_n):,.0f}</div>{get_delta_html(clean_val(sy_n)+clean_val(sm_n), clean_val(sy_s)+clean_val(sm_s), False)}
                <div class="split-text">
                    <div class="split-item">יניב: ₪{clean_val(sy_n):,.0f}{get_delta_html(sy_n, sy_s, False, False)}</div>
                    <div style="border-left: 1px solid #eee; height: 30px;"></div>
                    <div class="split-item">מיכל: ₪{clean_val(sm_n):,.0f}{get_delta_html(sm_n, sm_s, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            exc_n, exc_s = df_s.iloc[1, 2], df_s.iloc[1, 4]
            int_n, int_s = df_s.iloc[2, 2], df_s.iloc[2, 4]
            tr_n, tr_s = clean_val(exc_n) + (clean_val(int_n) * USD_RATE), clean_val(exc_s) + (clean_val(int_s) * USD_RATE)
            st.markdown(f'''<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{tr_n:,.0f}</div>{get_delta_html(tr_n, tr_s, False)}
                <div class="split-text">
                    <div class="split-item">אקסלנס: ₪{clean_val(exc_n):,.0f}{get_delta_html(exc_n, exc_s, False, False)}</div>
                    <div style="border-left: 1px solid #eee; height: 30px;"></div>
                    <div class="split-item">אינטר': ${clean_val(int_n):,.0f}{get_delta_html(int_n, int_s, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)
        with r2c2:
            p_n = clean_val(df_d.iloc[5, 15]) + clean_val(df_d.iloc[6, 15]) + clean_val(df_d.iloc[11, 15])
            p_s = clean_val(df_d.iloc[5, 14]) + clean_val(df_d.iloc[6, 14]) + clean_val(df_d.iloc[11, 14])
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 הורים</div><div class="sub-val">₪{p_n:,.0f}</div>{get_delta_html(p_n, p_s, False)}<div class="split-text">נזיל וזמין</div></div>', unsafe_allow_html=True)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            k_n, k_s = df_s.iloc[9, 2], df_s.iloc[9, 4]
            st.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 ילדים</div><div class="sub-val">₪{clean_val(k_n):,.0f}</div>{get_delta_html(k_n, k_s, False)}<div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        with r3c2:
            vac = clean_val(df_d.iloc[10, 15])
            vac_s = clean_val(df_d.iloc[10, 14])
            st.markdown(f'<div class="sub-card" style="border-right: 5px solid #3b82f6;"><div class="sub-label">🏖️ חופשה</div><div class="sub-val" style="color: #3b82f6;">₪{vac:,.0f}</div>{get_delta_html(vac, vac_s, False)}<div class="split-text">ארה"ב ומקסיקו 2027</div></div>', unsafe_allow_html=True)

        r4c1, r4c2 = st.columns(2)
        with r4c1:
            h_n, h_s = df_s.iloc[10, 2], df_s.iloc[10, 4]
            ltv = (abs(clean_val(df_s.iloc[11, 2])) / clean_val(h_n) * 100) if clean_val(h_n) > 0 else 0
            st.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{clean_val(h_n):,.0f}</div>{get_delta_html(h_n, h_s, False)}<div style="font-size:0.7rem; color:#999; margin-top:5px; font-weight:bold;">LTV: {ltv:.1f}%</div></div>', unsafe_allow_html=True)
        with r4c2:
            i_n, i_s = df_s.iloc[3, 2], df_s.iloc[3, 4]
            st.markdown(f'<div class="sub-card"><div class="sub-label">✈️ איסתא</div><div class="sub-val">₪{clean_val(i_n):,.0f}</div>{get_delta_html(i_n, i_s, False)}<div class="split-text">אופציות מנהלים</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
