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
URL_DEBTS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1414631518&single=true&output=csv"
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

    # הזרקת CSS לשינוי עיצוב הטאבים למראה נקי ומותאם למובייל
    # הזרקת CSS מתוקן ליישור מוחלט לימין
    st.markdown("""
        <style>
            /* הגדרת כל אזור הטאבים כימין לשמאל */
            div[data-testid="stTabs"] {
                direction: rtl !important;
            }

            /* יישור רצועת הכפתורים עצמה */
            div[data-testid="stTabs"] [data-baseweb="tab-list"] {
                display: flex;
                justify-content: flex-start !important;
                flex-direction: row !important; /* direction:rtl כבר דואג להיפוך */
                gap: 8px;
            }

            /* עיצוב הטקסט בתוך הטאבים */
            div[data-testid="stTabs"] button [data-testid="stMarkdownContainer"] p {
                color: black !important;
                font-weight: 500 !important;
                font-size: 0.9rem !important;
                white-space: nowrap;
            }

            /* הדגשת הקו התחתון של הטאב הנבחר בשחור */
            div[data-testid="stTabs"] button[aria-selected="true"] {
                border-bottom-color: black !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏠 מבט על", "📋 פירוט", "🚀 מחשבון פרישה"])
    
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
            "✈️ חיסכון לחופשה": [10], 
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
                    asset_name = str(row.iloc[1])
                    v_now = clean_val(row.iloc[15])   # עמודה K
                    v_start = clean_val(row.iloc[10])  # עמודה F
                    v_depo = clean_val(row.iloc[16])  # עמודה L

                    # לוגיקה נקודתית לאינטראקטיב:
                    display_currency = "₪"
                    if "אינטראקטיב" in asset_name:
                        v_now = v_now * USD_RATE
                        d_html = get_delta_html(v_now, v_start, v_depo, is_main_card=False)
                    else:
                        d_html = get_delta_html(v_now, v_start, v_depo, is_main_card=False)
                        
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

        # הפרדה ויזואלית
        st.markdown("<br><hr style='border-top: 2px dashed #e2e8f0;'><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:right;color: #e11d48;'>📉 פירוט התחייבויות</h2>", unsafe_allow_html=True)

        try:
            df_debts = pd.read_csv(URL_DEBTS)
            debt_indices = [2, 0] 
            
            # חישוב סכומים לסיכום הכותרת
            total_debt_now = 0
            total_debt_prev = 0
            valid_debts = []

            for idx in debt_indices:
                if idx < len(df_debts):
                    row = df_debts.iloc[idx]
                    d_val = clean_val(row.iloc[10])
                    d_val_prev = clean_val(row.iloc[7])
                    if d_val > 0:
                        total_debt_now += d_val
                        total_debt_prev += d_val_prev
                        valid_debts.append((row, d_val, d_val_prev))

            # יצירת כותרת עם סיכום (כמו בנכסים)
            debt_diff = total_debt_now - total_debt_prev
            debt_pct = (debt_diff / total_debt_prev * 100) if total_debt_prev != 0 else 0
            
            # בחוב: אם ירד (שלילי) זה ירוק, אם עלה זה אדום
            debt_indicator = "🟢" if debt_diff <= 0 else "🔴"
            debt_header = f"ריכוז התחייבויות | ₪{total_debt_now:,.0f} {debt_indicator} ({debt_pct:+.1f}%)"

            # יצירת ה-Expander
            with st.expander(debt_header, expanded=True):
                for row, d_val, d_val_prev in valid_debts:
                    d_name = str(row.iloc[1])
                    diff = d_val - d_val_prev
                    pct = (diff / d_val_prev * 100) if d_val_prev != 0 else 0
                    color = "#4CAF50" if diff <= 0 else "#e11d48"
                    arrow = "▼" if diff <= 0 else "▲"

                    debt_html = f"""
                        <div style='background: white; padding: 20px; border-radius: 20px; 
                                    box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 16px; 
                                    border-right: 8px solid #e11d48; direction: rtl; text-align: right;'>
                            <div style='display: flex; justify-content: space-between; align-items: start;'>
                                <div>
                                    <div style='font-size: 1.2rem; font-weight: 800; color: #1e293b;'>{d_name}</div>
                                    <div style='font-size: 0.85rem; color: #64748b;'>הוחזר השנה</div>
                                </div>
                                <div style='text-align: left; direction: ltr;'>
                                    <div style='font-size: 1.5rem; font-weight: 900; color: #1e293b;'>₪{d_val:,.0f}</div>
                                    <div style='color: {color}; font-size: 0.9rem; font-weight: 600; margin-top: 4px;'>
                                        {arrow} ₪{abs(diff):,.0f} ({abs(pct):.1f}%)
                                    </div>
                                </div>
                            </div>
                            <div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; direction: rtl;'>
                                <span style='font-size: 0.8rem; color: #64748b;'>📅 יתרה ב-2025: <b>₪{d_val_prev:,.0f}</b></span>
                                <span style='font-size: 0.8rem; color: #64748b;'>📉 שינוי שנתי</span>
                            </div>
                        </div>
                    """
                    st.markdown(debt_card_html, unsafe_allow_html=True)
                        
        except Exception as e:
            st.info(f"ממתין לעדכון נתוני התחייבויות...")

    # כאן מתחיל טאב 3 - שים לב שהוא באותה רמת הזחה (רווחים) כמו with tab2
    with tab3:
        # בלוק CSS מאוחד - נקי וממוקד
        # בלוק CSS מאוחד ומדויק
        st.markdown("""
            <style>
                /* 1. טקסט שחור לכותרות */
                div[data-testid="stWidgetLabel"] p {
                    color: black !important;
                    font-weight: bold !important;
                    text-align: right;
                }
                
                /* 2. כפתור לא נבחר - רקע בהיר, טקסט שחור */
                button[data-testid="stBaseButton-secondaryPill"] {
                    background-color: #f0f2f6 !important; /* אפור בהיר נקי */
                    color: black !important; /* שיניתי מאדום לשחור */
                    border: 1px solid #d1d5db !important;
                    border-radius: 10px !important;
                }
                
                /* 3. כפתור נבחר - רקע שחור, טקסט לבן */
                button[data-testid="stBaseButton-secondaryPill"][aria-checked="true"] {
                    background-color: black !important;
                    color: white !important;
                    border-color: black !important;
                    font-weight: bold !important;
                }

                /* 4. יישור לימין של הכפתורים */
                div[data-testid="stPills"] > div {
                    justify-content: flex-end !important;
                    flex-direction: row-reverse !important;
                }
                
                /* 5. עיצוב הודעת ההצלחה */
                div.stSuccess {
                    background-color: #f0fdf4;
                    color: #166534;
                    border: 1px solid #bbf7d0;
                    border-radius: 12px;
                    text-align: right;
                    direction: rtl;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:right; color: black;'>🚀 מחשבון חופש כלכלי (FIRE)</h3>", unsafe_allow_html=True)
        
        # במובייל עדיף אחד מתחת לשני כדי שהכפתורים לא יחתכו
        st.markdown("<p style='color: black; font-weight: bold; text-align: right; margin-bottom: 5px;'>הוצאה חודשית מבוקשת (₪)</p>", unsafe_allow_html=True)
        monthly_expenses_fire = st.number_input("", value=15000, step=500, key="fire_input_exp_final", label_visibility="collapsed")
        
        # כותרת שחורה וברורה
        st.markdown("<p style='color: black; font-weight: bold; text-align: right; margin-top: 15px; margin-bottom: 5px;'>תשואה שנתית משוערת (%)</p>", unsafe_allow_html=True)
        
        # שימוש בתיבת בחירה - הכי בטוח למובייל, תמיד קריא ושחור
        return_options = [4, 5, 6, 7, 8, 9, 10, 11, 12]
        expected_return_fire = st.selectbox("", return_options, index=3, key="fire_ret_select", label_visibility="collapsed")

        # חישוב יעד
        fire_target = monthly_expenses_fire * 12 * 25
        
        try:
            current_net = float(str(n_now).replace('₪', '').replace(',', '').strip()) if 'n_now' in locals() else 0
        except:
            current_net = 0

        progress = min(current_net / fire_target, 1.0) if fire_target > 0 else 0
        
        # כרטיסי מידע
        st.markdown(f"""
            <div style="display: flex; gap: 12px; direction: rtl; margin-top: 20px;">
                <div style="flex: 1; background: white; padding: 18px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-right: 6px solid #10b981; text-align: right;">
                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px; font-weight: 500;">הון נוכחי</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">₪{current_net:,.0f}</div>
                </div>
                <div style="flex: 1; background: white; padding: 18px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-right: 6px solid #3b82f6; text-align: right;">
                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px; font-weight: 500;">יעד פרישה</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">₪{fire_target:,.0f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div style='text-align: right; margin-top: 20px; font-weight: bold; color: black;'>אחוז כיסוי מהיעד: {progress:.1%}</div>", unsafe_allow_html=True)
        st.progress(progress)

        st.markdown("<hr style='border: 0.5px solid black; margin-top: 25px; margin-bottom: 25px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: right; color: black;'>🗓️ מתי נגיע ליעד?</h3>", unsafe_allow_html=True)
        
        monthly_contribution = 5000 
        
        years_left = 0
        temp_net = current_net
        if temp_net < fire_target:
            while temp_net < fire_target and years_left < 50:
                temp_net = (temp_net * (1 + expected_return_fire/100)) + (monthly_contribution * 12)
                years_left += 1
            st.success(f"בהנחה של הפקדה חודשית של ₪{monthly_contribution:,.0f}, תגיע ליעד בעוד כ-**{years_left} שנים**.")
        else:
            st.balloons()
            st.success("אתה כבר שם! ההון שלך מספיק לכיסוי ההוצאות לפי חוק ה-4%.")
        # --- סימולטור פרישה ל-6 מיליון ש"ח (הון מושקע בלבד) ---
        st.markdown("<hr style='border: 0.5px solid black; margin-top: 25px; margin-bottom: 25px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: right; color: black;'>🎯 הדרך ליעד המחמיר (6 מיליון ש\"ח)</h3>", unsafe_allow_html=True)
        
        # חישוב הון עצמי ללא נדל"ן (מבוסס על הנתונים מהגיליון שלך)
        # אנחנו לוקחים רק פנסיות, גמל, השתלמות וחיסכון נזיל
        invested_net = current_net # כאן תוודא שהמשתנה current_net בטאבים הקודמים מופרד מהנדל"ן
        target_6m = 6000000
        monthly_savings = 5000 
        
        # חישוב שנים
        years_to_6m = 0
        future_value = invested_net
        
        if future_value < target_6m:
            while future_value < target_6m and years_left < 50:
                future_value = (future_value * (1 + expected_return_fire/100)) + (monthly_savings * 12)
                years_to_6m += 1
            
            # טקסט שחור בתוך תיבה (info-box) מותאמת למובייל
            st.markdown(f"""
                <div style="background-color: #f1f5f9; padding: 15px; border-radius: 12px; border: 1px solid #cbd5e1; direction: rtl; text-align: right;">
                    <p style="color: black; font-weight: bold; margin: 0;">
                        בהתבסס על הון מושקע של ₪{invested_net:,.0f} (ללא נדל"ן) ותשואה של {expected_return_fire}%, 
                        תגיעו ליעד של 6 מיליון ש"ח בעוד כ-<b>{years_to_6m} שנים</b>.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # יישור לימין של כותרת התקדמות וטקסט שחור
            progress_6m = min(invested_net / target_6m, 1.0)
            st.markdown(f"<p style='text-align: right; color: black; font-weight: bold; margin-top: 15px;'>השלמתם {progress_6m:.1%} מהדרך ליעד (הון מושקע):</p>", unsafe_allow_html=True)
            st.progress(progress_6m)
        else:
            st.balloons()
            st.success("מדהים! ההון המושקע שלכם כבר עבר את רף ה-6 מיליון.")

        # תובנה סופית בטקסט שחור בולט
        st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 10px; border-right: 5px solid black; border-left: 1px solid #e2e8f0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; direction: rtl; text-align: right; margin-top: 20px;">
                <p style="color: black; margin: 0;">
                    💡 <b>תובנה לפרישה:</b> החישוב כאן מתעלם משווי הדירה כי היא לא מייצרת קצבה חודשית (אלא אם תמכרו או תעברו למודל של "משכנתא הפוכה"). 
                    כדי להגיע ל-₪20,000 בחודש, המנוע העיקרי הוא התיק ב-<b>Interactive</b> ו-<b>Excellence</b>.
                </p>
            </div>
        """, unsafe_allow_html=True)
            
except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
