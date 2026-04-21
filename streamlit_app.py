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

def format_delta(current, start_year):
    """מחשבת שינוי ומחזירה HTML מעוצב"""
    if start_year == 0: return ""
    diff = current - start_year
    pct = (diff / start_year) * 100
    color = "#4CAF50" if diff >= 0 else "#F44336"
    arrow = "▲" if diff >= 0 else "▼"
    return f'<div style="color: {color}; font-size: 0.8rem; font-weight: bold;">{arrow} {abs(pct):.1f}% (₪{abs(diff):,.00f})</div>'

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
        background: white; border-radius: 12px; padding: 10px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-height: 85px; display: flex; flex-direction: column; justify-content: center;
    }
    .main-card { padding: 20px; border-radius: 18px; text-align: center; color: white; margin-bottom: 15px; }
    .sub-card { 
        background: white; padding: 15px; border-radius: 16px; text-align: center; margin-bottom: 12px; 
        min-height: 140px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        display: flex; flex-direction: column; justify-content: center;
    }
    .sub-val { font-size: 1.2rem; font-weight: 800; color: #1a1a1a; }
    .sub-label { font-size: 0.85rem; color: #777; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #999; margin-top: 5px; border-top: 1px solid #f0f0f0; padding-top: 5px; }
    h1 { text-align: center; font-weight: 900; color: #1e293b; }
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

    st.markdown("<h1>הון משפחת נודלמן</h1>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="ticker-box"><div class="t-label">💵 דולר/שקל</div><div class="t-val">₪{USD_RATE}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="ticker-box"><div class="t-label">📈 S&P 500</div><div class="t-val">{sp_p:,.0f}</div><div style="color:{sp_col}; font-size:0.8rem;">{sp_a} {abs(sp_c):.1f}%</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="ticker-box"><div class="t-label">₿ Bitcoin</div><div class="t-val">${btc_p:,.0f}</div><div style="color:{btc_col}; font-size:0.8rem;">{btc_a} {abs(btc_c):.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="update-time">נתונים מעודכנים ליום: {last_update}</div>', unsafe_allow_html=True)

    # נתונים וחישובי דלתא (עמודה 2 = נוכחי, עמודה 4 = תחילת שנה)
    net_now = clean_val(df_s.iloc[13, 2])
    net_start = clean_val(df_s.iloc[13, 4])
    
    mortgage = abs(clean_val(df_s.iloc[11, 2]))
    mortgage_start = abs(clean_val(df_s.iloc[11, 4]))
    
    loan = abs(clean_val(df_s.iloc[12, 2]))
    loan_start = abs(clean_val(df_s.iloc[12, 4]))
    
    debt_total = mortgage + loan
    debt_start = mortgage_start + loan_start
    
    house_val = clean_val(df_s.iloc[10, 2])
    house_start = clean_val(df_s.iloc[10, 4])

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            delta_net = format_delta(net_now, net_start)
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);"><div class="sub-label" style="color:white; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div>{delta_net}</div>', unsafe_allow_html=True)
        with c2:
            # בהתחייבויות, ירידה היא דבר חיובי (צבע ירוק)
            diff_debt = debt_start - debt_total
            debt_color = "#4CAF50" if diff_debt >= 0 else "#F44336"
            debt_arrow = "▼" if diff_debt >= 0 else "▲"
            debt_pct = (abs(diff_debt)/debt_start*100) if debt_start > 0 else 0
            st.markdown(f'''<div class="main-card" style="background: linear-gradient(135deg, #ef4444, #b91c1c);">
                <div class="sub-label" style="color:white; opacity:0.8;">התחייבויות</div>
                <div class="main-val">₪{debt_total:,.0f}</div>
                <div style="color:white; font-size:0.8rem; font-weight:bold;">{debt_arrow} {debt_pct:.1f}% (₪{abs(diff_debt):,.0f})</div>
            </div>''', unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2)
        # פנסיות
        py, pm = clean_val(df_s.iloc[4, 2]), clean_val(df_s.iloc[6, 2])
        py_s, pm_s = clean_val(df_s.iloc[4, 4]), clean_val(df_s.iloc[6, 4])
        r1c1.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{py+pm:,.0f}</div>{format_delta(py+pm, py_s+pm_s)}<div class="split-text">יניב: ₪{py:,.0f} | מיכל: ₪{pm:,.0f}</div></div>', unsafe_allow_html=True)
        
        # השתלמות
        sy, sm = clean_val(df_s.iloc[5, 2]), clean_val(df_s.iloc[7, 2])
        sy_s, sm_s = clean_val(df_s.iloc[5, 4]), clean_val(df_s.iloc[7, 4])
        r1c2.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{sy+sm:,.0f}</div>{format_delta(sy+sm, sy_s+sm_s)}<div class="split-text">יניב: ₪{sy:,.0f} | מיכל: ₪{sm:,.0f}</div></div>', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        # תיק מסחר
        exc, int_usd = clean_val(df_s.iloc[1, 2]), clean_val(df_s.iloc[2, 2])
        exc_s, int_s = clean_val(df_s.iloc[1, 4]), clean_val(df_s.iloc[2, 4])
        total_trade = exc + (int_usd * USD_RATE)
        total_trade_s = exc_s + (int_s * USD_RATE)
        r2c1.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{total_trade:,.0f}</div>{format_delta(total_trade, total_trade_s)}<div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        
        # חסכונות הורים (נזיל)
        parents = clean_val(df_d.iloc[5, 15]) + clean_val(df_d.iloc[6, 15]) + clean_val(df_d.iloc[11, 15])
        r2c2.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{parents:,.0f}</div><div class="split-text">נזיל</div></div>', unsafe_allow_html=True)

        r3c1, r3c2 = st.columns(2)
        # ילדים
        kids_now = clean_val(df_s.iloc[9, 2])
        kids_start = clean_val(df_s.iloc[9, 4])
        r3c1.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{kids_now:,.0f}</div>{format_delta(kids_now, kids_start)}<div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        
        # נדל"ן
        ltv = (mortgage / house_val * 100) if house_val > 0 else 0
        ltv_color = "#4CAF50" if ltv < 45 else "#FF9800" if ltv < 65 else "#F44336"
        r3c2.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{house_val:,.0f}</div>{format_delta(house_val, house_start)}<div class="ltv-badge" style="background-color: {ltv_color}22; color: {ltv_color}; font-size:0.7rem; margin-top:5px; font-weight:bold;">LTV: {ltv:.1f}%</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה בטעינת נתונים: {e}")
