import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות עמוד
st.set_page_config(page_title="הלוח הפיננסי של משפחת X", layout="wide")

# כותרת מעוצבת
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>מבט על: הון משפחתי</h1>", unsafe_allow_html=True)

# פונקציה למשיכת נתונים (כאן תשים את הלינק ל-CSV של הגיליון שלך)
# ב-Google Sheets: קובץ -> שיתוף -> פרסם באינטרנט -> בחר CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI6IIUbS6jdiE-M91t6dqPiGsZGpU2MSf5KZfBibJPOuWCwh1Bn_5bFnHgtWJdLQRWpBjdhU4927QK/pub?output=csv"
st.write(f"הלינק שלי הוא: {SHEET_URL}")
def load_data():
    # כאן אנחנו מושכים את הנתונים
    df = pd.read_csv(SHEET_URL)
    return df

try:
    df = load_data()
    
    # שליפת נתונים ספציפיים (לפי האינדקסים שאנחנו כבר מכירים)
    # נניח שורה 13 היא הון נקי, שורה 11 היא שווי בית, שורה 12 משכנתא
    hon_naki = df.iloc[13, 2]  # תא C13 (אינדקס מתחיל מ-0)
    bayit_val = df.iloc[14, 2]   # תא C11
    mashkanta = df.iloc[10, 2]  # תא C12
    achuz_bealut = ((bayit_val - mashkanta) / bayit_val) * 100

    # תצוגת "מבט על" בראש הדף - שלוש עמודות
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="הון עצמי נקי", value=f"₪ {hon_naki:,.0f}", delta="2.4% מהחודש שעבר")
        
    with col2:
        st.metric(label="אחוז בעלות בבית", value=f"{achuz_bealut:.1f}%")
        
    with col3:
        st.metric(label="יתרת משכנתא", value=f"₪ {mashkanta:,.0f}", delta="-0.5%", delta_color="normal")

    st.divider()

    # גרף עוגה של התפלגות נכסים
    st.subheader("איפה הכסף שלנו נמצא?")
    # נסנן רק את שורות הנכסים (נניח שורות 0 עד 9)
    assets_df = df.iloc[0:9]
    fig = px.pie(assets_df, values=assets_df.columns[2], names=assets_df.columns[1], 
                 hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("מחכה לחיבור הנתונים שלך...")
    st.info("כדי לראות את הדשבורד, צריך להדביק את לינק ה-CSV מהגיליון שלך בקוד.")
