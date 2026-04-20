import streamlit as st
import pandas as pd

# הלינק שלך
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"

df = pd.read_csv(SHEET_URL)

st.title("בדיקת אינדקסים מדויקת")

# מציג את הטבלה עם מספרי השורות בצד
st.write("תסתכל על המספרים משמאל (האינדקסים) ותגיד לי באיזה מספר שורה מופיע הסכום הנכון:")
st.dataframe(df)

# מציג את שמות העמודות ומספרן
st.write("רשימת העמודות ומספרן (למציאת העמודה של 2025):")
for i, col in enumerate(df.columns):
    st.write(f"עמודה {i}: {col}")
