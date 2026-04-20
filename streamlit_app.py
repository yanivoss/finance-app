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

# שער דולר מעודכן (ניתן לעדכן ידנית או למשוך מהרשת, כרגע מוגדר כ-3.7)
USD_RATE = 3.7 

st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .sub-card { background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; min-height: 110px; }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.2rem; font-weight: 700; color: #333; margin-top: 5px; }
    .sub-label { font-size: 0.9rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 3px; }
    h1 { text-align: center; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

try:
    df = pd.read_csv(URL_SUMMARY)

    # --- נתונים ראשיים ---
    net_now = clean_currency(df.iloc[13, 2])
    mortgage = abs(clean_currency(df.iloc[11, 2]))
    loan = abs(clean_currency(df.iloc[12, 2]))
    debt_total = mortgage + loan

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    t1, t2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div style="font-size:0.9rem; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div style="font-size:0.9rem; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_total:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown("### 📊 פילוח אפיקים")
        col1, col2 = st.columns(2)

        # 1. תיק מסחר (המרת דולר לאינטראקטיב)
        excellence = clean_currency(df.iloc[1, 2])
        interactive_usd = clean_currency(df.iloc[2, 2])
        interactive_ils = interactive_usd * USD_RATE
        with col1:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">💎 תיק מסחר</div>
                    <div class="sub-val">₪{excellence + interactive_ils:,.0f}</div>
                    <div class="split-text">אקסלנס: ₪{excellence:,.0f} | אינטראקטיב: ${interactive_usd:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        # 2. חסכונות הורים
        savings_parents = clean_currency(df.iloc[0, 2]) # עו"ש/חיסכון משותף
        with col2:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">🏦 חסכונות הורים</div>
                    <div class="sub-val">₪{savings_parents:,.0f}</div>
                    <div class="split-text">יניב ומיכל</div>
                </div>
            """, unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        
        # 3. חיסכון ילדים (עמית ונועם)
        # נניח ש-C10 ו-C11 בשיטס הם הילדים (תקן את האינדקס אם הם בתאים אחרים)
        kid_amit = clean_currency(df.iloc[9, 2]) 
        kid_noam = clean_currency(df.iloc[9, 1]) # דוגמה לשליפה מעמודה אחרת או שורה סמוכה
        with col3:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">👧👦 חיסכון ילדים</div>
                    <div class="sub-val">₪{kid_amit + kid_noam:,.0f}</div>
                    <div class="split-text">עמית: ₪{kid_amit:,.0f} | נועם: ₪{kid_noam:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        # 4. נדל"ן ואופציות
        house_val = clean_currency(df.iloc[10, 2]) # תא ערך הבית
        ista_options = 0 # ניתן להוסיף תא ייעודי לאופציות איסתא
        with col4:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">🏠 נדל"ן ואופציות</div>
                    <div class="sub-val">₪{house_val:,.0f}</div>
                    <div class="split-text">ערך הבית | אופציות איסתא</div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
