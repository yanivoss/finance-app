import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import yfinance as yf

# הגדרת דף
st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

# --- פונקציות עזר ---
def clean_val(value):
    if isinstance(value, (int, float)): return float(value)
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        try: return float(clean)
        except: return 0.0
    return 0.0

def get_market_data(ticker_symbol):
    """מושך נתוני שוק חיים"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="2d")
        if len(data) < 2:
            return 0, 0, "#666", ""
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        color = "#4CAF50" if change_pct >= 0 else "#F44336"
        arrow = "▲" if change_pct >= 0 else "▼"
        return current_price, change_pct, color, arrow
    except:
        return 0, 0, "#666", ""

# --- לוגיקת ריענון ---
with st.sidebar:
    if st.button('🔄 רענן נתונים'):
        st.cache_data.clear()
        st.rerun()

# נתונים קבועים
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
USD_RATE = 3.7

# --- עיצוב CSS מעודכן לאיזון גבהים ---
st.markdown("""
    <style>
    .ticker-box { 
        background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; 
        padding: 8px 10px; text-align: center; min-width: 120px;
        min-height: 70px; display: flex; flex-direction: column; justify-content: center;
    }
    .t-label { font-size: 0.75rem; color: #666; font-weight: bold; margin-bottom: 2px; }
    .t-val { font-size: 1rem; font-weight: 800; color: #333; }
    .t-delta { font-size: 0.75rem; font-weight: bold; margin-top: 2px; }
    
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 115px; display: flex; flex-direction: column; justify-content: center; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.1rem; font-weight: 700; color: #333; margin-top: 2px; }
    .sub-label { font-size: 0.85rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 4px; border-top: 1px solid #eee; padding-top: 4px; }
    .ltv-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; margin-top: 5px; }
    .update-time { text-align: center; color: #999; font-size: 0.8rem; margin-top: 5px; margin-bottom: 20px; }
    h1 { text-align: center; font-size: 1.8rem; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

try:
    # טעינת נתונים
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    
    # שליפת נתוני שוק
    sp_p, sp_c, sp_col, sp_a = get_market_data("^GSPC")
    btc_p, btc_c, btc_col, btc_a = get_market_data("BTC-USD")
    
    # זמן ירושלים
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    last_update = datetime.now(jerusalem_tz).strftime("%H:%M %d/%m/%Y")

    # כותרת ושורת מדדים
    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)
    
    _, m1, m2, m3, _ = st.columns([1, 2, 2, 2, 1])
    with m1:
        st.markdown(f'''<div class="ticker-box">
            <div class="t-label">💵 דולר/שקל</div>
            <div class="t-val">₪{USD_RATE}</div>
            <div class="t-delta" style="color: transparent;">-</div>
        </div>''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''<div class="ticker-box">
            <div class="t-label">📈 S&P 500</div>
            <div class="t-val">{sp_p:,.0f}</div>
            <div class="t-delta" style="color: {sp_col};">{sp_a} {abs(sp_c):.1f}%</div>
        </div>''', unsafe_allow_html=True)
    with m3:
        st.markdown(f'''<div class="ticker-box">
            <div class="t-label">₿ Bitcoin</div>
            <div class="t-val">${btc_p:,.0f}</div>
            <div class="t-delta" style="color: {btc_col};">{btc_a} {abs(btc_c):.1f}%</div>
        </div>''', unsafe_allow_html=True)

    st.markdown(f'<div class="update-time">נתונים מעודכנים ליום: {last_update}</div>', unsafe_allow_html=True)

    # נתונים מהשיטס
    net_now = clean_val(df_s.iloc[13, 2])
    mortgage = abs(clean_val(df_s.iloc[11, 2]))
    loan = abs(clean_val(df_s.iloc[12, 2]))
    debt_total = mortgage + loan
    house_val = clean_val(df_s.iloc[10, 2])

    # חישוב LTV
    ltv = (mortgage / house_val * 100) if house_val > 0 else 0
    ltv_color = "#4CAF50" if ltv < 45 else "#FF9800" if ltv < 65 else "#F44336"
    ltv_status = "תקין" if ltv < 45 else "בינוני" if ltv < 65 else "גבוה"

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div class="sub-label" style="color:white; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div class="sub-label" style="color:white; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_total:,.0f}</div></div>', unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2)
        py, pm = clean_val(df_s.iloc[4, 2]), clean_val(df_s.iloc[6, 2])
        r1c1.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{py+pm:,.0f}</div><div class="split-text">יניב: ₪{py:,.0f} | מיכל: ₪{pm:,.0f}</div></div>', unsafe_allow_html=True)
        sy, sm = clean_val(df_s.iloc[5, 2]), clean_val(df_s.iloc[7, 2])
        r1c2.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{sy+sm:,.0f}</div><div class="split-text">יניב: ₪{sy:,.0f} | מיכל: ₪{sm:,.0f}</div></div>', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        exc, int_usd = clean_val(df_s.iloc[1, 2]), clean_val(df_s.iloc[2, 2])
        r2c1.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{exc+(int_usd*USD_RATE):,.0f}</div><div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ${int_usd:,.0f}</div></div>', unsafe_allow_html=True)
        parents = clean_val(df_d.iloc[5, 15]) + clean_val(df_d.iloc[6, 15]) + clean_val(df_d.iloc[11, 15])
        r2c2.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות הורים</div><div class="sub-val">₪{parents:,.0f}</div><div class="split-text">נזיל</div></div>', unsafe_allow_html=True)

        r3c1, r3c2 = st.columns(2)
        kids_total = clean_val(df_s.iloc[9, 2])
        r3c1.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חיסכון ילדים</div><div class="sub-val">₪{kids_total:,.0f}</div><div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        vacation = clean_val(df_d.iloc[10, 15])
        r3c2.markdown(f'<div class="sub-card" style="border-right: 4px solid #1E88E5;"><div class="sub-label">🏖️ חיסכון לחופשה</div><div class="sub-val" style="color: #1E88E5;">₪{vacation:,.0f}</div><div class="split-text">לטיול הבא שלנו</div></div>', unsafe_allow_html=True)

        r4c1, r4c2 = st.columns(2)
        r4c1.markdown(f'<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{house_val:,.0f}</div><div class="ltv-badge" style="background-color: {ltv_color}22; color: {ltv_color};">LTV: {ltv:.1f}% | {ltv_status}</div></div>', unsafe_allow_html=True)
        ista = clean_val(df_s.iloc[3, 2])
        r4c2.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{ista:,.0f}</div><div class="split-text">ממתין למימוש</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה בטעינת נתונים: {e}")
