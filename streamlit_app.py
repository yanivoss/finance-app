import streamlit as st
import pandas as pd

# הגדרות עמוד למראה אפליקטיבי
st.set_page_config(page_title="Noodelman Finance", layout="wide", initial_sidebar_state="collapsed")

# פונקציית ניקוי נתונים
def clean_currency(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, str):
        clean_val = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_val) if clean_val else 0.0
    return float(value)

# לינקים (לפי ה-GID המנצח שלך)
URL_SUMMARY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?gid=1388477026&single=true&output=csv"

# עיצוב CSS מתקדם לשני כפתורים במקביל
st.markdown("""
    <style>
    .card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .net-card { background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); color: white; }
    .debt-card { background: linear-gradient(135deg, #FF5252 0%, #D32F2F 100%); color: white; }
    
    .card-val { font-size: 1.8rem; font-weight: 800; margin: 5px 0; }
    .card-label { font-size: 1rem; opacity: 0.9; font-weight: bold; }
    .pct-badge { 
        background: white; display: inline-block; padding: 1px 8px; 
        border-radius: 8px; font-size: 0.8rem; font-weight: bold; 
    }
    
    h1 { text-align: center; color: #333; font-size: 1.8rem; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    </style>
""", unsafe_allow_html=True)

try:
    df_summary = pd.read_csv(URL_SUMMARY)

    # --- שליפת נתונים מדויקת ---
    # הון נטו (שורה 15, עמודה C)
    current_net = clean_currency(df_summary.iloc[13, 2])
    prev_net = clean_currency(df_summary.iloc[13, 1])
    
    # התחייבויות (סכימה של הלוואה ומשכנתא - שורות 14-15 באקסל = אינדקסים 11 ו-12 ב-Dataframe)
    # שים לב: אנחנו מוודאים שהקוד לוקח את הערך המוחלט (חיובי) להצגה
    loan_val = abs(clean_currency(df_summary.iloc[11, 2]))
    mortgage_val = abs(clean_currency(df_summary.iloc[12, 2]))
    total_debt = loan_val + mortgage_val
    
    # אחוזי שינוי
    net_pct = ((current_net / prev_net) - 1) * 100 if prev_net != 0 else 0
    # אחוז שינוי התחייבויות (מול עמודה B)
    prev_debt = abs(clean_currency(df_summary.iloc[11, 1])) + abs(clean_currency(df_summary.iloc[12, 1]))
    debt_pct = ((total_debt / prev_debt) - 1) * 100 if prev_debt != 0 else 0

    st.markdown("<h1>💰 הון משפחת נודלמן</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 מבט על", "📋 פירוט"])

    with tab1:
        # שורה עם שני כפתורים במקביל
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div class="card net-card">
                    <div class="card-label">הון נטו</div>
                    <div class="card-val">₪{current_net:,.0f}</div>
                    <div class="pct-badge" style="color: #1E88E5;">{'+' if net_pct >= 0 else ''}{net_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="card debt-card">
                    <div class="card-label">התחייבויות</div>
                    <div class="card-val">₪{total_debt:,.0f}</div>
                    <div class="pct-badge" style="color: #FF5252;">{'+' if debt_pct >= 0 else ''}{debt_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # שורת מידע משלימה (הון ברוטו)
        total_gross = current_net + total_debt
        st.markdown(f"<p style='text-align:center; color:gray;'><b>הון ברוטו:</b> ₪{total_gross:,.0f}</p>", unsafe_allow_html=True)

    with tab2:
        st.subheader("מבנה הנכסים והתחייבויות")
        # מציג את הטבלה הרלוונטית מהסיכום
        st.dataframe(df_summary.iloc[0:15, 0:3], use_container_width=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
