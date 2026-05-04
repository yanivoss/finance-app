import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

# נתוני אופציות איסתא - קבועים
ISSTA_QTY = 1500
ISSTA_STRIKE = 81.3664
def get_issta_live_value():
    try:
        # משיכת מחיר מניה בזמן אמת מ-Yahoo Finance
        issta = yf.Ticker("ISTA.TA")
        current_price = issta.history(period="1d")['Close'].iloc[-1]
        
        # חישוב SAME DAY SALE: (מחיר נוכחי * כמות) - (מחיר מימוש * כמות)
        gross_value = (current_price * ISSTA_QTY) - (ISSTA_STRIKE * ISSTA_QTY)
        
        # אם המחיר מתחת למימוש, השווי הוא 0 (לא נממש בהפסד)
        return max(0, gross_value), current_price
    except Exception as e:
        return None, None

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

def get_issta_live_value():
    try:
        import yfinance as yf
        # ניסיון למשוך את הטיקר
        ticker_name = "ISTA.TA"
        issta = yf.Ticker(ticker_name)
        
        # ניסיון להוציא היסטוריה של יום אחד
        hist = issta.history(period="1d")
        
        if hist.empty:
            st.error(f"שגיאה: לא התקבלו נתונים עבור {ticker_name}. ייתכן שהבורסה סגורה או שהסימול שגוי.")
            return None, None
            
        current_price = hist['Close'].iloc[-1]
        
        # חישוב SAME DAY SALE
        gross_value = (current_price * ISSTA_QTY) - (ISSTA_STRIKE * ISSTA_QTY)
        return max(0, gross_value), current_price
        
    except Exception as e:
        st.error(f"קרסה הפונקציה של איסתא: {e}")
        return None, None

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
            py_n, py_s, py_d = df_s.iloc[4, 2], df_s.iloc[4, 4], df_s.iloc[4, 6]
            pm_n, pm_s, pm_d = df_s.iloc[6, 2], df_s.iloc[6, 4], df_s.iloc[6, 6]
            st.markdown(f'''<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{clean_val(py_n)+clean_val(pm_n):,.0f}</div>{get_delta_html(clean_val(py_n)+clean_val(pm_n), clean_val(py_s)+clean_val(pm_s), clean_val(py_d)+clean_val(pm_d), False)}
                <div class="split-text">
                    <div class="split-item">יניב: ₪{clean_val(py_n):,.0f}{get_delta_html(py_n, py_s, py_d, False, False)}</div>
                    <div style="border-left: 1px solid #f1f5f9; height: 30px;"></div>
                    <div class="split-item">מיכל: ₪{clean_val(pm_n):,.0f}{get_delta_html(pm_n, pm_s, pm_d, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)
        with r1c2:
            sy_n, sy_s, sy_d = df_s.iloc[5, 2], df_s.iloc[5, 4], df_s.iloc[5, 6]
            sm_n, sm_s, sm_d = df_s.iloc[7, 2], df_s.iloc[7, 4], df_s.iloc[7, 6]
            st.markdown(f'''<div class="sub-card"><div class="sub-label">📈 קרנות השתלמות</div><div class="sub-val">₪{clean_val(sy_n)+clean_val(sm_n):,.0f}</div>{get_delta_html(clean_val(sy_n)+clean_val(sm_n), clean_val(sy_s)+clean_val(sm_s), clean_val(sy_d)+clean_val(sm_d), False)}
                <div class="split-text">
                    <div class="split-item">יניב: ₪{clean_val(sy_n):,.0f}{get_delta_html(sy_n, sy_s, sy_d, False, False)}</div>
                    <div style="border-left: 1px solid #f1f5f9; height: 30px;"></div>
                    <div class="split-item">מיכל: ₪{clean_val(sm_n):,.0f}{get_delta_html(sm_n, sm_s, sm_d, False, False)}</div>
                </div></div>''', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            exc_n, exc_s, exc_d = df_s.iloc[1, 2], df_s.iloc[1, 4], df_s.iloc[1, 6]
            int_n, int_s, int_d = df_s.iloc[2, 2], df_s.iloc[2, 4], df_s.iloc[2, 6]
            tr_n = clean_val(exc_n) + clean_val(int_n) 
            tr_s = clean_val(exc_s) + clean_val(int_s)
            tr_d = clean_val(exc_d) + clean_val(int_d) 
            st.markdown(f'''<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{tr_n:,.0f}</div>{get_delta_html(tr_n, tr_s, tr_d, False)}
                <div class="split-text">
                    <div class="split-item">אקסלנס: ₪{clean_val(exc_n):,.0f}{get_delta_html(exc_n, exc_s, exc_d, False, False)}</div>
                    <div style="border-left: 1px solid #f1f5f9; height: 30px;"></div>
                    <div class="split-item">אינטר': ₪{clean_val(int_n):,.0f}{get_delta_html(clean_val(int_n), clean_val(int_s), clean_val(int_d), False, False)}</div>
                </div></div>''', unsafe_allow_html=True)
        with r2c2:
            p_n, p_s, p_d = df_s.iloc[8, 2], df_s.iloc[8, 4], df_s.iloc[8, 6]
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות נזילים</div><div class="sub-val">₪{clean_val(p_n):,.0f}</div>{get_delta_html(p_n, p_s, p_d, False)}<div class="split-text"><div style="height: 40px; text-align: center;"> יניב ומיכל</div></div>', unsafe_allow_html=True)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            k_n, k_s, k_d = df_s.iloc[9, 2], df_s.iloc[9, 4], df_s.iloc[9, 6]
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
            i_n, i_s, i_d = df_s.iloc[3, 2], df_s.iloc[3, 4], df_s.iloc[3, 6]
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
        # 1. הגדרת הקבוצות לפי הטקסט המדויק בעמודה I בגיליון ה-APP
        groups_config = {
            "קרנות פנסיה": "🏦 קרנות פנסיה",
            "קרנות השתלמות": "📈 קרנות השתלמות",
            "תיק השקעות ומסחר": "💎 תיק השקעות ומסחר",
            "חיסכון לילדים": "👦 חיסכון לילדים",
            "חיסכון הורים": "🏥חיסכון הורים",
            "חיסכון לחופשה": "✈️ חיסכון לחופשה"
        }

        # 2. לולאת ריצה על הקטגוריות
        for app_cat_name, display_name in groups_config.items():
            # סינון שורות ה-APP ששייכות לקטגוריה הנוכחית
            relevant_app_rows = df_s[df_s.iloc[:, 8].astype(str).str.strip() == app_cat_name].copy()
            
            if relevant_app_rows.empty:
                continue

            valid_rows = []
            total_now, total_invested = 0, 0

            # 3. לולאת ריצה על השורות בתוך הקטגוריה
            for _, app_row in relevant_app_rows.iterrows():
                # משיכת שם המחזיק ישירות מעמודה J (אינדקס 9) בגיליון ה-APP
                try:
                    owner = str(app_row.iloc[9]).strip() 
                    if owner == "nan" or owner == "":
                        owner = "משותף"
                except:
                    owner = "משותף"

                # נתונים כספיים מה-APP
                asset_name = str(app_row.iloc[1]).strip()
                v_now = clean_val(app_row.iloc[2])
                v_orig = clean_val(app_row.iloc[4])
                v_ytd_depo = clean_val(app_row.iloc[5])
                v_total_depo = clean_val(app_row.iloc[6])
                
                invested = v_orig + v_total_depo
                gain = v_now - invested
                
                total_now += v_now
                total_invested += invested
                
                valid_rows.append({
                    'owner': owner,
                    'name': asset_name,
                    'v_now': v_now,
                    'v_ytd_depo': v_ytd_depo,
                    'invested': invested,
                    'gain': gain
                })

            # 4. יצירת התצוגה (Expander)
            if valid_rows:
                g_pct = ((total_now - total_invested) / total_invested * 100) if total_invested != 0 else 0
                indicator = "🟢" if total_now >= total_invested else "🔴"
                header = f"{display_name} | ₪{total_now:,.0f} {indicator} ({g_pct:+.1f}%)"

                with st.expander(header, expanded=True):
                    for item in valid_rows:
                        pct = (item['gain'] / item['invested'] * 100) if item['invested'] != 0 else 0
                        color = "#4CAF50" if item['gain'] >= 0 else "#e11d48"
                        arrow = "▲" if item['gain'] >= 0 else "▼"
                        d_html = f"<span style='color: {color}; font-weight: 700;'>₪{item['gain']:,.0f} ({abs(pct):.1f}%) {arrow}</span>"
                        
                        asset_card(
                        item['name'], 
                        item['owner'],  # כאן הורדתי את ה-f"מחזיק: {item['owner']}"
                        item['v_now'], 
                        0, 
                        item['v_ytd_depo'], 
                        d_html, 
                        "₪"
                    )
        
        # הפרדה ויזואלית
        st.markdown("<br><hr style='border-top: 2px dashed #e2e8f0;'><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:right;color: #e11d48;'>📉 פירוט התחייבויות</h2>", unsafe_allow_html=True)

        try:
            df_debts = pd.read_csv(URL_DEBTS)
            debt_indices = [2, 0] 
            
            total_debt_now = 0
            total_debt_start_original = 0 
            valid_debts = []

            for idx in debt_indices:
                if idx < len(df_debts):
                    row = df_debts.iloc[idx]
                    asset_name = str(row.iloc[1])
                    d_val_now = clean_val(row.iloc[10]) # יתרה היום (K)
                    
                    # ערכי ברירת מחדל למקרה שהחיפוש ב-APP ייכשל
                    v_total_paid = 0
                    v_original_val = d_val_now if d_val_now > 0 else 0

                    # חיפוש בגיליון APP (df_s)
                    try:
                        if 'df_s' in locals() or 'df_s' in globals():
                            # חיפוש לפי המילה הראשונה בשם הנכס
                            first_word = asset_name.split()[0]
                            mask = df_s.iloc[:, 1].str.contains(first_word, na=False, case=False)
                            app_match = df_s[mask]
                            
                            if not app_match.empty:
                                v_total_paid = clean_val(app_match.iloc[0, 6])   # עמודה G
                                v_original_val = clean_val(app_match.iloc[0, 4]) # עמודה E
                    except:
                        pass

                    if d_val_now >= 0: # שיניתי ל >= כדי שיציג גם אם החוב אופס
                        total_debt_now += d_val_now
                        total_debt_start_original += v_original_val
                        valid_debts.append((row, d_val_now, v_total_paid, v_original_val))

            # --- חישוב כותרת בטוח (מחוץ ללולאת ה-for) ---
            total_paid_calc = total_debt_start_original - total_debt_now
            # הגנה מפני חלוקה באפס
            if total_debt_start_original > 0:
                debt_pct_progress = (total_paid_calc / total_debt_start_original * 100)
            else:
                debt_pct_progress = 0
            
            debt_header = f"ריכוז התחייבויות | יתרה: ₪{total_debt_now:,.0f} 🟢 ({debt_pct_progress:.1f}% שולם)"

            with st.expander(debt_header, expanded=True):
                for row, d_val, v_total_paid, v_original_val in valid_debts:
                    d_name = str(row.iloc[1])
                    # חישוב אחוזים בטוח
                    paid_pct = (v_total_paid / v_original_val * 100) if v_original_val > 0 else 0
                    remaining_pct = (d_val / v_original_val * 100) if v_original_val > 0 else 0
                    
                    debt_card_html = f"""
                        <div style='background: white; padding: 20px; border-radius: 20px; 
                                    box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 16px; 
                                    border-right: 8px solid #e11d48; direction: rtl; text-align: right;'>
                            <div style='display: flex; justify-content: space-between; align-items: start;'>
                                <div>
                                    <div style='font-size: 1.2rem; font-weight: 800; color: #1e293b;'>{d_name}</div>
                                    <div style='font-size: 0.85rem; color: #64748b;'>הלוואה מקורית: ₪{v_original_val:,.0f}</div>
                                </div>
                                <div style='text-align: left; direction: ltr;'>
                                    <div style='font-size: 1.5rem; font-weight: 900; color: #1e293b;'>₪{d_val:,.0f}</div>
                                    <div style='color: #4CAF50; font-size: 0.9rem; font-weight: 600; margin-top: 4px;'>
                                        הוחזר: ₪{v_total_paid:,.0f} ({paid_pct:.1f}%)
                                    </div>
                                </div>
                            </div>
                            <div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; direction: rtl;'>
                                <span style='font-size: 0.8rem; color: #64748b;'>📉 נותר לסילוק: <b>{remaining_pct:.1f}%</b> מהקרן</span>
                                <span style='font-size: 0.8rem; color: #e11d48;'>⏳ יתרה לתשלום</span>
                            </div>
                        </div>
                    """
                    st.markdown(debt_card_html, unsafe_allow_html=True)

        except Exception as e:
            st.info("ממתין לעדכון נתוני התחייבויות...")            

    # כאן מתחיל טאב 3 - שים לב שהוא באותה רמת הזחה (רווחים) כמו with tab2
    with tab3:
        # --- בלוק CSS מאוחד ---
        st.markdown("""
            <style>
                div[data-testid="stWidgetLabel"] p {
                    color: black !important;
                    font-weight: bold !important;
                    text-align: right;
                }
                div.stSuccess {
                    background-color: #f0fdf4;
                    color: #166534;
                    border: 1px solid #bbf7d0;
                    border-radius: 12px;
                    text-align: right;
                    direction: rtl;
                }
                .stExpander {
                    background-color: #ffffff !important;
                    border: 1px solid #e2e8f0 !important;
                    border-radius: 12px !important;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
                    margin-bottom: 1rem !important;
                }
                .stExpander details summary p {
                    color: black !important;
                    font-weight: 600 !important;
                }
                .stExpander details summary svg {
                    fill: black !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # --- 1. הגדרות וחישובי בסיס (חייבים להיות ראשונים) ---
        def to_num(val):
            try:
                if isinstance(val, (int, float)): return float(val)
                s = str(val).replace('₪', '').replace(',', '').replace('%', '').strip()
                return float(s) if s else 0.0
            except: return 0.0

        # חישוב הון מושקע
        try:
            target_categories = ["תיק השקעות ומסחר", "קרנות השתלמות", "קרנות פנסיה", "חיסכון הורים"]
            invested_net = 0
            for i, row in df_s.iterrows():
                category = str(row.iloc[8]).strip() 
                val = to_num(row.iloc[2])
                if category in target_categories:
                    invested_net += val
        except:
            invested_net = 0

        # נתוני הפקדות קבועים
        monthly_pension = 3228.65 + 2899.5
        monthly_hishtalmut = 1400 + 1500
        monthly_independent = 2700
        base_monthly_contribution = monthly_pension + monthly_hishtalmut + monthly_independent

        # שימוש ב-Session State כדי למנוע שגיאות הגדרה
        current_extra = st.session_state.get('extra_savings_sim', 0)
        current_desired_income = st.session_state.get('income_target_num', 25000)
        
        total_monthly_sim = base_monthly_contribution + current_extra
        # חישוב יעד הון (לפי הכלל שלכם: הכנסה פחות 4000 כפול 300)
        current_target_capital = max(current_desired_income - 4000, 0) * 12 * 25

        # --- 2. כותרת ראשית ---
        st.markdown("<h2 style='text-align: right; color: black;'>🚀 סימולציית עצמאות כלכלית</h2>", unsafe_allow_html=True)
        st.write("") 

        # --- 3. חלק עליון: קוביות סיכום (Metrics) ---
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 15px; border-right: 5px solid #3b82f6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: right;">
                    <p style="color: #64748b; margin: 0; font-size: 0.9rem;">הפקדה חודשית כוללת</p>
                    <h2 style="margin: 0; color: #1e293b; font-size: 1.8rem;">₪{total_monthly_sim:,.0f}</h2>
                </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 15px; border-right: 5px solid #10b981; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: right;">
                    <p style="color: #64748b; margin: 0; font-size: 0.9rem;">הון מושקע (ללא נדל"ן)</p>
                    <h2 style="margin: 0; color: #1e293b; font-size: 1.8rem;">₪{invested_net:,.0f}</h2>
                </div>
            """, unsafe_allow_html=True)

        # --- 4. שורת אחוז השלמת היעד ---
        progress_pct = (invested_net / current_target_capital * 100) if current_target_capital > 0 else 0
        
        st.write("")
        st.markdown(f"""
            <div style="direction: rtl; text-align: right; margin-bottom: 5px;">
                <span style="font-weight: bold; font-size: 1rem; color: black;">השלמתם {progress_pct:.1f}% מהדרך ליעד (הון מושקע):</span>
            </div>
        """, unsafe_allow_html=True)
        st.progress(min(progress_pct / 100, 1.0))
        
        st.markdown("---") 

        # --- 5. ממשק הגדרות סימולציה (Inputs) ---
        col_fire1, col_fire2 = st.columns(2)

        with col_fire1:
            st.markdown("<p style='font-weight: bold; text-align: right; margin-bottom: 5px; color: black;'>קצבה חודשית מבוקשת</p>", unsafe_allow_html=True)
            desired_income = st.number_input("", value=25000, step=1000, key="income_target_num", label_visibility="collapsed")
            # עדכון יעד ההון לפי הקלט בפועל
            target_capital = max(desired_income - 4000, 0) * 12 * 25 
            
        with col_fire2:
            st.markdown("<p style='font-weight: bold; text-align: right; margin-bottom: 5px; color: black;'>תשואה שנתית (%)</p>", unsafe_allow_html=True)
            expected_return_fire = st.selectbox("", [4,5,6,7,8,9,10], index=3, key="fire_ret_select", label_visibility="collapsed")

        st.markdown("<p style='font-weight: bold; text-align: right; margin-top: 15px; margin-bottom: 5px; color: black;'>תוספת הפקדה חודשית (₪)</p>", unsafe_allow_html=True)
        extra_savings = st.number_input("", value=0, step=500, key="extra_savings_sim", label_visibility="collapsed")

        # --- 6. חישוב סימולציה (מייצר נתונים לתיבה ולגרף) ---
        years_to_goal = 0
        fv = invested_net
        chart_data = []
        
        current_year_fv = invested_net
        total_invested_so_far = invested_net
        
        for y in range(51):  # חישוב ל-50 שנה קדימה
            chart_data.append({
                "שנה": y,
                "הון צבור": current_year_fv,
                "סך הפקדות": total_invested_so_far,
                "רווח מצטבר": max(0, current_year_fv - total_invested_so_far)
            })
            
            if current_year_fv >= target_capital and years_to_goal == 0:
                years_to_goal = y
            
            # צמיחה שנתית
            current_year_fv = (current_year_fv * (1 + expected_return_fire/100)) + (total_monthly_sim * 12)
            total_invested_so_far += (total_monthly_sim * 12)

        retirement_age = 48 + years_to_goal
        
        # --- 7. תצוגת התוצאה בתיבה השחורה ---
        st.markdown(f"""
            <div style="background-color: black; padding: 25px; border-radius: 16px; direction: rtl; text-align: right; margin-top: 20px; border-right: 8px solid #10b981;">
                <p style="color: white; font-size: 1.1rem; margin: 0;">
                    ליעד הכנסה של <span style="color: #10b981; font-weight: bold;">₪{desired_income:,.0f}</span> בחודש (הון נדרש: ₪{target_capital:,.0f})
                </p>
                <p style="color: white; font-size: 1.4rem; margin-top: 15px; margin-bottom: 0;">
                    בקצב הזה, תגיעו ליעד בעוד: <span style="color: #10b981; font-size: 1.8rem; font-weight: bold;">{years_to_goal} שנים</span>
                </p>
                <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 10px;">
                    הגיל המשוער שלכם יהיה: <span style="font-weight: bold; color: white;">{retirement_age}</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.write("") 

        # --- 8. פירוט הפקדות (Expander) ---
        with st.expander("🔍 פירוט הזרמת הכספים החודשית"):
            p_val = f"{monthly_pension:,.0f}"
            h_val = f"{monthly_hishtalmut:,.0f}"
            i_val = f"{monthly_independent:,.0f}"
            e_val = f"{extra_savings:,.0f}"
            t_val = f"{total_monthly_sim:,.0f}"

            # שים לב - בלי f-string על כל הבלוק, אלא שרשור פשוט כמו שעבד קודם
            html = '<div style="direction: rtl; text-align: right; font-family: sans-serif;">'
            html += '<p style="color: black;">💰 <b>פנסיות (זוגי):</b> ₪' + p_val + '</p>'
            html += '<p style="color: black;">📈 <b>קרנות השתלמות:</b> ₪' + h_val + '</p>'
            html += '<p style="color: black;">💎 <b>השקעה עצמאית:</b> ₪' + i_val + '</p>'
            
            if extra_savings > 0:
                html += '<p style="color: #10b981;">➕ <b>תוספת סימולציה:</b> ₪' + e_val + '</p>'
            
            html += '<hr style="border: none; border-top: 1px solid #eee; margin: 10px 0;">'
            html += '<p style="font-size: 1.1rem; font-weight: bold; color: black;">סה"כ חסכון חודשי: ₪' + t_val + '</p>'
            html += '</div>'

            st.markdown(html, unsafe_allow_html=True)
        
        # --- 9. קוביה ירוקה מסכמת ---
        st.markdown(f"""
            <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; border: 1px solid #bbf7d0; text-align: center; margin-top: 25px; direction: rtl;">
                <div style="font-size: 1rem; color: #166534; font-weight: bold;">קצבה חודשית ברוטו פוטנציאלית (כולל הכל):</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: #166534; margin: 10px 0;">₪{desired_income:,.0f}</div>
                <div style="font-size: 0.9rem; color: #166534;">
                    מבוסס על משיכה של 4% מההון + ₪4,000 קצבת זקנה משוערת לזוג
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- 10. גרף צמיחה ויזואלי מאוחד ---
        st.write("")
        st.markdown("<p style='font-weight: bold; text-align: right; color: black;'>📈 מסלול צמיחת ההון מול יעד המטרה</p>", unsafe_allow_html=True)
        
        import pandas as pd
        
        # הכנת הנתונים
        df_chart = pd.DataFrame(chart_data)
        df_chart["Target_Goal"] = target_capital
        
        # שינוי שמות לאנגלית כדי למנוע בעיות תצוגה במקרא
        df_chart = df_chart.rename(columns={
            "סך הפקדות": "Total_Invested",
            "רווח מצטבר": "Accumulated_Profit"
        }).set_index("שנה")
        
        display_years = min(years_to_goal + 5, 50)
        chart_subset = df_chart.head(display_years)

        # יצירת גרף מאוחד - נשתמש ב-st.area_chart עבור הכל
        # כדי שהקו יהיה בולט, נוסיף אותו כשכבה ב-area_chart אבל הוא ייראה כקו ישר
        st.area_chart(
            chart_subset[["Total_Invested", "Accumulated_Profit", "Target_Goal"]],
            color=["#3b82f6", "#10b981", "#ff4b4b"]
        )
        
        st.markdown(f"""
            <div style="direction: rtl; text-align: right; font-size: 0.85rem; color: #64748b;">
                <span style="color: #ff4b4b;">▬</span> <b>קו אדום:</b> יעד הון נדרש (₪{target_capital:,.0f}) | 
                <span style="color: #3b82f6;">■</span> <b>כחול:</b> סך הפקדות | 
                <span style="color: #10b981;">■</span> <b>ירוק:</b> רווח שנצבר
            </div>
        """, unsafe_allow_html=True)
                    
except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
