import streamlit as st
import pandas as pd

st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# לינקים
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=0&single=true&output=csv"

# עיצוב CSS מעודכן לקטגוריות קטנות
st.markdown("""
    <style>
    .main-card { padding: 15px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .sub-card { 
        background: #f8f9fa; border: 1px solid #e9ecef; padding: 12px; border-radius: 12px; 
        text-align: center; margin-bottom: 10px; height: 110px;
    }
    .main-val { font-size: 1.6rem; font-weight: 800; }
    .sub-val { font-size: 1.1rem; font-weight: 700; color: #333; margin-top: 5px; }
    .sub-label { font-size: 0.85rem; color: #666; font-weight: bold; }
    .split-text { font-size: 0.75rem; color: #888; margin-top: 3px; }
    h1 { text-align: center; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

try:
    df_summary = pd.read_csv(URL_SUMMARY)
    df_data = pd.read_csv(URL_DATA)

    # הכנת נתוני המעקב (עמודה 11 היא 2025)
    col_now = df_data.columns[11]
    df_data[col_now] = df_data[col_now].apply(clean_currency)
    
    # חישובים ראשיים
    net_now = clean_currency(df_summary.iloc[13, 2])
    debt_now = abs(clean_currency(df_summary.iloc[11, 2])) + abs(clean_currency(df_summary.iloc[12, 2]))

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    t1, t2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with t1:
        # שורה ראשונה - כרטיסים גדולים
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #1E88E5, #1565C0);"><div style="font-size:0.9rem; opacity:0.8;">הון נטו</div><div class="main-val">₪{net_now:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="background: linear-gradient(135deg, #FF5252, #D32F2F);"><div style="font-size:0.9rem; opacity:0.8;">התחייבויות</div><div class="main-val">₪{debt_now:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown("### 📊 סיכום לפי אפיקים")
        
        # פונקציית עזר לסיכום קטגוריות
        def get_cat_summary(keyword):
            sub = df_data[df_data[df_data.columns[1]].str.contains(keyword, na=False)]
            total = sub[col_now].sum()
            y = sub[df_data[df_data.columns[0]] == 'יניב'][col_now].sum()
            m = sub[df_data[df_data.columns[0]] == 'מיכל'][col_now].sum()
            return total, y, m

        # הגדרת הקטגוריות
        cats = {
            "🏦 פנסיות": "פנסיה",
            "📈 השתלמות": "השתלמות",
            "💎 תיק מסחר": "מסחר|Excellence|Interactive",
            "💰 חיסכון/מזומן": "עו\"ש|חיסכון"
        }

        cols = st.columns(2)
        for i, (label, key) in enumerate(cats.items()):
            total, y, m = get_cat_summary(key)
            with cols[i % 2]:
                st.markdown(f"""
                    <div class="sub-card">
                        <div class="sub-label">{label}</div>
                        <div class="sub-val">₪{total:,.0f}</div>
                        <div class="split-text">יניב: ₪{y:,.0f} | מיכל: ₪{m:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)

    with t2:
        st.dataframe(df_data.iloc[:, [0, 1, 11]], use_container_width=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
