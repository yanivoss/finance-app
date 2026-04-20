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

# עיצוב CSS למראה אפליקטיבי וקומפקטי
st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .sub-card { 
        background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; 
        text-align: center; margin-bottom: 10px; min-height: 100px;
    }
    .main-val { font-size: 1.8rem; font-weight: 800; }
    .sub-val { font-size: 1.2rem; font-weight: 700; color: #333; margin-top: 5px; }
    .sub-label { font-size: 0.9rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 3px; }
    h1 { text-align: center; font-size: 1.8rem; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

try:
    # טעינת נתונים מגיליון ה-Summary
    df = pd.read_csv(URL_SUMMARY)

    # --- משיכת נתונים לפי הקורדינאטות מהתמונה ---
    # הון נטו
    net_now = clean_currency(df.iloc[14, 2])
    net_prev = clean_currency(df.iloc[14, 1])
    net_pct = ((net_now / net_prev) - 1) * 100 if net_prev != 0 else 0

    # התחייבויות (משכנתא C13 + הלוואה C14)
    mortgage = abs(clean_currency(df.iloc[12, 2]))
    loan = abs(clean_currency(df.iloc[13, 2]))
    debt_total = mortgage + loan
    
    prev_debt = abs(clean_currency(df.iloc[12, 1])) + abs(clean_currency(df.iloc[13, 1]))
    debt_pct = ((debt_total / prev_debt) - 1) * 100 if prev_debt != 0 else 0

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט מלא"])

    with tab1:
        # שורה ראשונה - כרטיסי סיכום ראשיים
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);">
                    <div style="font-size:0.9rem; opacity:0.8;">הון נטו</div>
                    <div class="main-val">₪{net_now:,.0f}</div>
                    <div style="background:white; color:#1E88E5; display:inline-block; padding:0 8px; border-radius:5px; font-size:0.8rem; font-weight:bold;">
                        {'+' if net_pct >= 0 else ''}{net_pct:.1f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);">
                    <div style="font-size:0.9rem; opacity:0.8;">התחייבויות</div>
                    <div class="main-val">₪{debt_total:,.0f}</div>
                    <div style="background:white; color:#FF5252; display:inline-block; padding:0 8px; border-radius:5px; font-size:0.8rem; font-weight:bold;">
                        {'+' if debt_pct >= 0 else ''}{debt_pct:.1f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # שורת אפיקים - כרטיסים קטנים
        st.markdown("### 📊 פילוח אפיקים")
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        # 1. פנסיות (C6, C8)
        p_yaniv = clean_currency(df.iloc[5, 2])
        p_michal = clean_currency(df.iloc[7, 2])
        with row1_col1:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">🏦 פנסיות</div>
                    <div class="sub-val">₪{p_yaniv + p_michal:,.0f}</div>
                    <div class="split-text">יניב: ₪{p_yaniv:,.0f} | מיכל: ₪{p_michal:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        # 2. השתלמות (C7, C9)
        s_yaniv = clean_currency(df.iloc[6, 2])
        s_michal = clean_currency(df.iloc[8, 2])
        with row1_col2:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">📈 השתלמות</div>
                    <div class="sub-val">₪{s_yaniv + s_michal:,.0f}</div>
                    <div class="split-text">יניב: ₪{s_yaniv:,.0f} | מיכל: ₪{s_michal:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        # 3. תיק מסחר (אקסלנס C3, אינטראקטיב C4)
        excellence = clean_currency(df.iloc[2, 2])
        interactive = clean_currency(df.iloc[3, 2])
        with row2_col1:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">💎 תיק מסחר</div>
                    <div class="sub-val">₪{excellence + interactive:,.0f}</div>
                    <div class="split-text">אקסלנס: ₪{excellence:,.0f} | אינטראקטיב: ₪{interactive:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        # 4. חסכונות (משותף C11 + ילדים C10)
        savings_joint = clean_currency(df.iloc[10, 2])
        savings_kids = clean_currency(df.iloc[9, 2])
        with row2_col2:
            st.markdown(f"""
                <div class="sub-card">
                    <div class="sub-label">💰 חסכונות</div>
                    <div class="sub-val">₪{savings_joint + savings_kids:,.0f}</div>
                    <div class="split-text">משותף: ₪{savings_joint:,.0f} | ילדים: ₪{savings_kids:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.write("נתונים גולמיים מתוך App_Summary:")
        st.dataframe(df.iloc[:, 0:3], use_container_width=True)

except Exception as e:
    st.error(f"שגיאה בעיבוד הנתונים: {e}")
