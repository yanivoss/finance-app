import streamlit as st
import pandas as pd

# הגדרות עמוד
st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

# פונקציית ניקוי נתונים
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# לינקים (מעודכנים לפי מה שעבד)
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"

# עיצוב CSS מתקדם למראה אפליקטיבי
st.markdown("""
    <style>
    /* עיצוב כרטיס הון עצמי */
    .net-worth-card {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .net-worth-val { font-size: 3rem; font-weight: 800; margin: 10px 0; }
    .net-worth-label { font-size: 1.2rem; opacity: 0.9; }
    
    /* עיצוב כפתור התחייבויות */
    .debt-button {
        background-color: #FF5252;
        color: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        display: block;
        margin: 10px auto;
        width: 80%;
    }
    
    h1 { text-align: center; color: #333; margin-bottom: 30px; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    </style>
""", unsafe_allow_html=True)

try:
    # טעינת נתונים
    df_summary = pd.read_csv(URL_SUMMARY)
    
    # שליפת נתונים מ-App_Summary
    # C15 = נטו נוכחי | B15 = נטו קודם | C14 = סה"כ התחייבויות
    current_net = clean_currency(df_summary.iloc[13, 2])
    prev_net = clean_currency(df_summary.iloc[13, 1])
    total_debt = clean_currency(df_summary.iloc[12, 2]) # בהנחה ששורה 14 היא אינדקס 12

    # חישוב אחוז שינוי
    change_pct = ((current_net / prev_net) - 1) * 100 if prev_net != 0 else 0
    change_color = "#4CAF50" if change_pct >= 0 else "#FF5252"

    st.markdown("<h1>הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        # כרטיס הון עצמי מעוצב
        st.markdown(f"""
            <div class="net-worth-card">
                <div class="net-worth-label">סה"כ הון עצמי נטו</div>
                <div class="net-worth-val">₪{current_net:,.0f}</div>
                <div style="color: {change_color}; background: white; display: inline-block; padding: 2px 12px; border-radius: 10px; font-weight: bold;">
                    {'+' if change_pct >= 0 else ''}{change_pct:.1f}%
                </div>
            </div>
        """, unsafe_allow_html=True)

        # שורת מדדים נוספת (התחייבויות)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.metric("התחייבויות", f"₪{total_debt:,.0f}")
        with col2:
            st.metric("הון ברוטו", f"₪{current_net + total_debt:,.0f}")

        st.markdown("---")
        
        # כפתור מעוצב להתחייבויות (סתם כעיצוב בולט או לינק לגיליון)
        st.markdown(f'<div class="debt-button">סה"כ חובות: ₪{total_debt:,.0f}</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("מבנה תיק הנכסים")
        # כאן נציג את הטבלה מ-App_Summary או המעקב
        st.dataframe(df_summary.iloc[0:15, 0:3], use_container_width=True)

except Exception as e:
    st.error(f"שגיאה בעיבוד הנתונים: {e}")
