import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

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

def get_delta_html(current, start, deposits=0, is_main_card=True, show_NIS=True):
    curr = clean_val(current)
    strt = clean_val(start)
    depo = clean_val(deposits)
    total_invested = strt + depo
    if abs(total_invested) <= 10: return '<span style="display:block; height:20px;"></span>'
    profit_loss = curr - total_invested
    pct = (profit_loss / abs(total_invested)) * 100 
    arrow = "▲" if profit_loss >= 0 else "▼"
    nis_text = f" (₪{abs(profit_loss):,.0f})" if show_NIS else ""
    if is_main_card:
        arrow_color = "#4ade80" if profit_loss >= 0 else "#ff8787" 
        return f'''
        <div style="background-color: rgba(255, 255, 255, 0.22); color: white; font-size: 0.85rem; font-weight: 800; 
             margin: 10px auto 0 auto; padding: 5px 14px; border-radius: 20px; width: fit-content; 
             border: 1px solid rgba(255, 255, 255, 0.25); display: flex; align-items: center; gap: 4px;">
            <span style="color: {arrow_color};">{arrow}</span>
            <span>{abs(pct):.1f}%</span>
            <span style="font-size: 0.75rem; font-weight: 400; opacity: 0.9;">{nis_text}</span>
        </div>
        '''
    else:
        status_color = "#16a34a" if profit_loss >= 0 else "#dc2626"
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
    except: return 0, 0, "#666", ""

# נתונים
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"
# קריאה לפונקציה שלך כדי לקבל את שער הדולר העדכני
# אנחנו משתמשים בטיקר "ILS=X" שהוא הסימול לדולר/שקל ב-Yahoo Finance
current_usd, change_pct, color, arrow = get_market_data("ILS=X")

# עדכון המשתנה הגלובלי שבו כל האפליקציה משתמשת
if current_usd > 0:
    USD_RATE = round(current_usd, 2)
else:
    USD_RATE = 3.00  # גיבוי למקרה שהפונקציה החזירה 0 (שגיאה)

# --- CSS ---
st.markdown("""
    <style>
    /* רקע כללי וכיווניות */
    .stApp { 
        background-color: #f4f7f9; 
        direction: rtl; 
    }
    
    /* כותרת H1 - הפיכה לשחור בולט עם ריווח טוב */
    h1 {
        color: #0f172a !important; /* כחול-כהה עמוק, כמעט שחור */
        font-weight: 800 !important;
        padding: 25px 0 !important;
        text-align: center;
        text-shadow: none !important; /* ביטול הצל למראה נקי ובולט */
    }

    /* תיקון הטיקרים (הקופסאות הלבנות למעלה) */
    .ticker-box { 
        background: white; 
        border-radius: 14px; 
        padding: 12px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
        min-height: 95px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        margin-bottom: 10px;
    }

    /* הפיכת הטקסט בתוך הטיקרים לכהה וברור */
    .ticker-box div {
        color: #1e293b !important; /* צבע כהה לכל הטקסט */
    }

    /* התאמה ספציפית למובייל - כאן קורה הקסם */
    @media (max-width: 640px) {
        h1 { 
            font-size: 1.8rem !important; 
            padding: 15px 0 !important;
        }
        .ticker-box {
            min-height: 80px;
            padding: 8px;
        }
        /* הקטנת פונטים במובייל כדי שלא יחרגו מהקופסה */
        .ticker-box div[style*="font-size:0.75rem"] {
            font-size: 0.7rem !important;
            color: #64748b !important; /* אפור כהה לכותרות הקטנות */
        }
        .ticker-box div[style*="font-size:1.1rem"] {
            font-size: 1rem !important; /* המספר המרכזי */
            font-weight: 800 !important;
        }
    }

    /* עיצוב הכרטיסים הראשיים (הון נטו והתחייבויות) */
    .main-card { 
        padding: 25px 20px; 
        border-radius: 20px; 
        text-align: center; 
        color: white; 
        margin-bottom: 15px; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
    }
    
    .sub-card { 
        background: white; 
        padding: 18px; 
        border-radius: 18px; 
        text-align: center; 
        margin-bottom: 15px; 
        min-height: 170px; 
        box-shadow: 0 2px 12px rgba(0,0,0,0.04); 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        position: relative; 
        overflow: hidden; 
    }

    .sub-val { font-size: 1.3rem; font-weight: 800; color: #1e293b; margin: 5px 0; }
    .sub-label { font-size: 0.95rem; color: #64748b; font-weight: 700; }
    
    .split-text { 
        font-size: 0.8rem; 
        color: #475569; 
        margin-top: 15px; 
        border-top: 1px solid #f1f5f9; 
        padding-top: 12px; 
        display: flex; 
        justify-content: space-around; 
        align-items: center; 
    }
    
    .ltv-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 8px; }
    </style>
""", unsafe_allow_html=True)

try:
    df_s = pd.read_csv(URL_SUMMARY)
    df_d = pd.read_csv(URL_DATA)
    sp_p, sp_c, sp_col, sp_a = get_market_data("^GSPC")
    btc_p, btc_c, btc_col, btc_a = get_market_data("BTC-USD")

    st.markdown("<h1 style='text-align:center;'>הון משפחת נודלמן</h1>", unsafe_allow_html=True)
    
    # טיקרים
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="ticker-box"><div style="font-size:0.75rem; color:#black;">💵 דולר/שקל</div><div style="font-size:1.1rem; font-weight:800;">₪{USD_RATE}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="ticker-box"><div style="font-size:0.75rem; color:#black;">📈 S&P 500</div><div style="font-size:1.1rem; font-weight:800;">{sp_p:,.0f}</div><div style="color:{sp_col}; font-size:0.75rem; font-weight:bold;">{sp_a} {abs(sp_c):.1f}%</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="ticker-box"><div style="font-size:0.75rem; color:#black;">₿ Bitcoin</div><div style="font-size:1.1rem; font-weight:800;">${btc_p:,.0f}</div><div style="color:{btc_col}; font-size:0.75rem; font-weight:bold;">{btc_a} {abs(btc_c):.1f}%</div></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        c1, c2 = st.columns(2)
        # הון נטו
        n_now, n_start, n_depo = df_s.iloc[13, 2], df_s.iloc[13, 4], df_s.iloc[13, 5]
        with c1: st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"><div class="sub-label" style="color:white; opacity:0.9;">הון נטו</div><div style="font-size:2.3rem; font-weight:800;">₪{clean_val(n_now):,.0f}</div>{get_delta_html(n_now, n_start, n_depo, True)}</div>', unsafe_allow_html=True)
        # התחייבויות
        debt_now = abs(clean_val(df_s.iloc[11, 2])) + abs(clean_val(df_s.iloc[12, 2]))
        debt_start = abs(clean_val(df_s.iloc[11, 4])) + abs(clean_val(df_s.iloc[12, 4]))
        with c2: st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #dc2626, #b91c1c);"><div class="sub-label" style="color:white; opacity:0.9;">התחייבויות</div><div style="font-size:2.3rem; font-weight:800;">₪{debt_now:,.0f}</div>{get_delta_html(debt_now, debt_start, 0, True)}</div>', unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            py_n, py_s, py_d = df_s.iloc[4, 2], df_s.iloc[4, 4], df_s.iloc[4, 5]
            pm_n, pm_s, pm_d = df_s.iloc[6, 2], df_s.iloc[6, 4], df_s.iloc[6, 5]
            st.markdown(f'''<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{clean_val(py_n)+clean_val(pm_n):,.0f}</div>{get_delta_html(clean_val(py_n)+clean_val(pm_n), clean_val(py_s)+clean_val(pm_s), clean_val(py_d)+clean_val(pm_d), False)}
                <div class="split-text">
                    <div class="split-item">יניב: ₪{clean_val(py_n):,.0f}{get_delta_html(py_n, py_s, py_d, False, False)}</div>
                    <div style="border-left: 1px solid #f1f5f9; height: 30px;"></div>
                    <div class="split-item">מיכל: ₪{clean_val(pm_n):,.0f}{get_delta_html(pm_n, pm_s, pm_d, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)
        with r1c2:
            sy_n, sy_s, sy_d = df_s.iloc[5, 2], df_s.iloc[5, 4], df_s.iloc[5, 5]
            sm_n, sm_s, sm_d = df_s.iloc[7, 2], df_s.iloc[7, 4], df_s.iloc[7, 5]
            st.markdown(f'''<div class="sub-card"><div class="sub-label">📈 קרנות השתלמות</div><div class="sub-val">₪{clean_val(sy_n)+clean_val(sm_n):,.0f}</div>{get_delta_html(clean_val(sy_n)+clean_val(sm_n), clean_val(sy_s)+clean_val(sm_s), clean_val(sy_d)+clean_val(sm_d), False)}
                <div class="split-text">
                    <div class="split-item">יניב: ₪{clean_val(sy_n):,.0f}{get_delta_html(sy_n, sy_s, sy_d, False, False)}</div>
                    <div style="border-left: 1px solid #f1f5f9; height: 30px;"></div>
                    <div class="split-item">מיכל: ₪{clean_val(sm_n):,.0f}{get_delta_html(sm_n, sm_s, sm_d, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            exc_n, exc_s, exc_d = df_s.iloc[1, 2], df_s.iloc[1, 4], df_s.iloc[1, 5]
            int_n, int_s, int_d = df_s.iloc[2, 2], df_s.iloc[2, 4], df_s.iloc[2, 5]
            tr_n = clean_val(exc_n) + (clean_val(int_n) * USD_RATE)
            tr_s = clean_val(exc_s) + (clean_val(int_s) * USD_RATE)
            tr_d = clean_val(exc_d) + (clean_val(int_d) * USD_RATE)
            st.markdown(f'''<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{tr_n:,.0f}</div>{get_delta_html(tr_n, tr_s, tr_d, False)}
                <div class="split-text">
                    <div class="split-item">אקסלנס: ₪{clean_val(exc_n):,.0f}{get_delta_html(exc_n, exc_s, exc_d, False, False)}</div>
                    <div style="border-left: 1px solid #f1f5f9; height: 30px;"></div>
                    <div class="split-item">אינטר': ₪{clean_val(int_n) * USD_RATE:,.0f}{get_delta_html(clean_val(int_n) * USD_RATE, clean_val(int_s) * USD_RATE, clean_val(int_d) * USD_RATE, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)
        with r2c2:
            p_n, p_s, p_d = df_s.iloc[8, 2], df_s.iloc[8, 4], df_s.iloc[8, 5]
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות נזילים</div><div class="sub-val">₪{clean_val(p_n):,.0f}</div>{get_delta_html(p_n, p_s, p_d, False)}<div class="split-text"><div style="height: 40px; text-align: center;"> יניב ומיכל</div></div>', unsafe_allow_html=True)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            k_n, k_s, k_d = df_s.iloc[9, 2], df_s.iloc[9, 4], df_s.iloc[9, 5]
            st.markdown(f'<div class="sub-card"><div class="sub-label">👦👧 חסכונות ילדים</div><div class="sub-val">₪{clean_val(k_n):,.0f}</div>{get_delta_html(k_n, k_s, k_d, False)}<div class="split-text">עמית ונועם</div></div>', unsafe_allow_html=True)
        with r3c2:
            v_n, v_s, v_d = clean_val(df_d.iloc[10, 15]), clean_val(df_d.iloc[10, 10]), clean_val(df_d.iloc[10, 16])
            st.markdown(f'<div class="sub-card" style="border-right: 5px solid #3b82f6;"><div class="sub-label">🏖️ חיסכון לחופשה</div><div class="sub-val" style="color: #3b82f6;">₪{clean_val(v_n):,.0f}</div>{get_delta_html(v_n, v_s, v_d, False)}<div class="split-text">לחופשה הבאה שלנו</div></div>', unsafe_allow_html=True)

        r4c1, r4c2 = st.columns(2)
        with r4c1:
            h_n, h_s = df_s.iloc[10, 2], df_s.iloc[10, 4]
            mortgage = abs(clean_val(df_s.iloc[11, 2]))
            ltv = (mortgage / clean_val(h_n) * 100) if clean_val(h_n) > 0 else 0
            ltv_color = "#16a34a" if ltv < 60 else "#ea580c"
            st.markdown(f'''<div class="sub-card"><div class="sub-label">🏠 נדל"ן</div><div class="sub-val">₪{clean_val(h_n):,.0f}</div>{get_delta_html(h_n, h_s, 0, False)}
                <div style="font-size:0.8rem; margin-top:10px; font-weight:bold; color:{ltv_color};">LTV: {ltv:.1f}%</div>
                <div class="ltv-bar" style="background-color: {ltv_color};"></div></div>''', unsafe_allow_html=True)
        with r4c2:
            i_n, i_s, i_d = df_s.iloc[3, 2], df_s.iloc[3, 4], df_s.iloc[3, 5]
            st.markdown(f'<div class="sub-card"><div class="sub-label">✈️ אופציות איסתא</div><div class="sub-val">₪{clean_val(i_n):,.0f}</div>{get_delta_html(i_n, i_s, i_d, False)}<div class="split-text">ממתין למימוש </div></div>', unsafe_allow_html=True)
    with tab2:
        st.markdown("<h2 style='text-align:right;color: black;'>📋 פירוט תיק הנכסים</h2>", unsafe_allow_html=True)
        
        # פונקציה פנימית לעיצוב הכרטיס - כולל נתוני הפקדות ותחילת שנה
        def asset_card(name, owner, val_now, val_start, deposits, delta_html, currency="₪"):
            st.markdown(f"""
                <div style="background: white; padding: 16px; border-radius: 16px; 
                            box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 12px; 
                            border-right: 6px solid #2563eb; direction: rtl;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="text-align: right;">
                            <div style="font-size: 1.1rem; font-weight: 800; color: #1e293b;">{name}</div>
                            <div style="font-size: 0.85rem; color: #444;">מחזיק: {owner}</div>
                        </div>
                        <div style="text-align: left;">
                            <div style="font-size: 1.25rem; font-weight: 800; color: #1e293b;">₪{val_now:,.0f}</div>
                            {delta_html}
                        </div>
                    </div>
                    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #f1f5f9; 
                                display: flex; justify-content: space-between; font-size: 0.8rem; color: #444;">
                        <span>💰 הפקדות השנה: <b>₪{deposits:,.0f}</b></span>
                        <span>📅 תחילת שנה: <b>₪{val_start:,.0f}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # הגדרת הקבוצות לפי אינדקסים בגיליון DATA
        groups = {
            "🏦 קרנות פנסיה": [0, 1, 3],
            "📈 קרנות השתלמות": [2, 4],
            "💎 תיק השקעות ומסחר": [7, 8, 9],
            "👦 חיסכון לילדים": [12, 13, 14],
            "🏥 נזיל וקופות גמל": [5, 6, 11, 15],
            "✈️ חיסכון לחופשה": [19], 
        }

        # טעינת נתונים גולמיים מהגיליון
        raw_data = df_d.iloc[0:16].copy()

        for group_name, row_indices in groups.items():
            # חישוב סיכומים לקבוצה (עבור הכותרת)
            g_now, g_start, g_depo = 0, 0, 0
            valid_rows = []

            for idx in row_indices:
                if idx < len(raw_data):
                    row = raw_data.iloc[idx]
                    v_now = clean_val(row.iloc[15])   # עמודה K
                    v_start = clean_val(row.iloc[10])  # עמודה F
                    v_depo = clean_val(row.iloc[16])  # עמודה L
                    # 1. קודם כל מגדירים את שם הנכס מהעמודה השנייה (B)
                    asset_name = str(row.iloc[1])

                    # לוגיקה נקודתית לאינטראקטיב:
                    display_currency = "₪"
                    if "אינטראקטיב" in asset_name:
                        profit_usd = v_now - v_start - v_depo
                        profit_pct = (profit_usd / v_start * 100) if v_start != 0 else 0
                        profit_ils = profit_usd * USD_RATE
                        d_html = f"""
                            <div style="color: {'#4CAF50' if profit_usd >= 0 else '#F44336'}; font-size: 0.9rem; font-weight: 600;">
                                {'▲' if profit_usd >= 0 else '▼'} (₪{profit_ils:,.0f}) {profit_pct:.1f}%
                            </div>
                        """                    
                    # בדיקה שהשורה לא ריקה ויש בה נתונים
                    if not pd.isna(row.iloc[1]) and (v_now != 0 or v_start != 0):
                        g_now += v_now
                        g_start += v_start
                        g_depo += v_depo
                        valid_rows.append((row, v_now, v_start, v_depo))

            # יצירת כותרת Expander עם סיכום כספי
            if g_now > 0:
                profit = g_now - g_start - g_depo
                # קביעת צבע (אמוג'י ירוק/אדום כפתרון פשוט ובולט לכותרת)
                indicator = "🟢" if profit >= 0 else "🔴"
                pct = (profit / g_start * 100) if g_start != 0 else 0
                
                # הכותרת החדשה עם אינדיקטור ויזואלי
                header_summary = f"{group_name} | ₪{g_now:,.0f} {indicator} ({pct:+.1f}%)"
            else:
                header_summary = group_name

            # הצגת ה-Expander והכרטיסים בתוכו
            with st.expander(header_summary, expanded=True):
                if not valid_rows:
                    st.write("אין נתונים להצגה בקבוצה זו.")
                for row, v_now, v_start, v_depo in valid_rows:
                    d_html = get_delta_html(v_now, v_start, v_depo, is_main_card=False)
                    asset_card(row.iloc[1], row.iloc[0], v_now, v_start, v_depo, d_html, display_currency)
   

except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
