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

# עיצוב CSS
st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 100px; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.2rem; font-weight: 700; color: #333; margin-top: 5px; }
    .sub-label { font-size: 0.9rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 3px; }
    h1 { text-align: center; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

try:
    df = pd.read_csv(URL_SUMMARY)

    # --- מיפוי תאים מחדש לפי הגיליון (Index = שורה באקסל פחות 2) ---
    
    # הון נטו - שורה 15 באקסל (אינדקס 13)
    net_now = clean_currency(df.iloc[13, 2])
    net_prev = clean_currency(df.iloc[13, 1])
    net_pct = ((net_now / net_prev) - 1) * 100 if net_prev != 0 else 0

    # התחייבויות - שורה 13 (משכנתא) ושורה 14 (הלוואה) באקסל (אינדקסים 11, 12)
    mortgage = abs(clean_currency(df.iloc[11, 2]))
    loan = abs(clean_currency(df.iloc[12, 2]))
    debt_total = mortgage + loan
    
    prev_debt = abs(clean_currency(df.iloc[11, 1])) + abs(clean_currency(df.iloc[12, 1]))
    debt_pct = ((debt_total / prev_debt) - 1) * 100 if prev_debt != 0 else 0

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        # שורה ראשונה
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div style="font-size:0.9rem; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div><div style="background:white; color:#1E88E5; display:inline-block; padding:0 8px; border-radius:5px; font-size:0.8rem; font-weight:bold;">{net_pct:+.1f}%</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div style="font-size:0.9rem; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_total:,.0f}</div><div style="background:white; color:#FF5252; display:inline-block; padding:0 8px; border-radius:5px; font-size:0.8rem; font-weight:bold;">{debt_pct:+.1f}%</div></div>', unsafe_allow_html=True)

        st.markdown("### 📊 פילוח אפיקים")
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)

        # 1. פנסיות - יניב שורה 6 (אינדקס 4), מיכל שורה 8 (אינדקס 6)
        p_y = clean_currency(df.iloc[4, 2])
        p_m = clean_currency(df.iloc[6, 2])
        with r1c1:
            st.markdown(f'<div class="sub-card"><div class="sub-label">🏦 פנסיות</div><div class="sub-val">₪{p_y + p_m:,.0f}</div><div class="split-text">יניב: ₪{p_y:,.0f} | מיכל: ₪{p_m:,.0f}</div></div>', unsafe_allow_html=True)

        # 2. השתלמות - יניב שורה 7 (אינדקס 5), מיכל שורה 9 (אינדקס 7)
        s_y = clean_currency(df.iloc[5, 2])
        s_m = clean_currency(df.iloc[7, 2])
        with r1c2:
            st.markdown(f'<div class="sub-card"><div class="sub-label">📈 השתלמות</div><div class="sub-val">₪{s_y + s_m:,.0f}</div><div class="split-text">יניב: ₪{s_y:,.0f} | מיכל: ₪{s_m:,.0f}</div></div>', unsafe_allow_html=True)

        # 3. תיק מסחר - אקסלנס שורה 3 (אינדקס 1), אינטראקטיב שורה 4 (אינדקס 2)
        exc = clean_currency(df.iloc[1, 2])
        int_inv = clean_currency(df.iloc[2, 2])
        with r2c1:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💎 תיק מסחר</div><div class="sub-val">₪{exc + int_inv:,.0f}</div><div class="split-text">אקסלנס: ₪{exc:,.0f} | אינטראקטיב: ₪{int_inv:,.0f}</div></div>', unsafe_allow_html=True)

        # 4. חסכונות - משותף שורה 2 (אינדקס 0), ילדים שורה 11 (אינדקס 9)
        # שים לב: לפי הגיליון C11 זה הדירה, אבל רשמת ש-C2 זה עו"ש. נשתמש ב-C2 כמשותף.
        joint = clean_currency(df.iloc[0, 2])
        kids = clean_currency(df.iloc[9, 2])
        with r2c2:
            st.markdown(f'<div class="sub-card"><div class="sub-label">💰 חסכונות</div><div class="sub-val">₪{joint + kids:,.0f}</div><div class="split-text">משותף: ₪{joint:,.0f} | ילדים: ₪{kids:,.0f}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
