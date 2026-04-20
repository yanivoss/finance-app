import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="הלוח הפיננסי", layout="wide")

# הלינק המדויק שלך
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fRNQuq8hR-QlKwHp61p6uVcurL-DF5jUSNfg3OhRb8k/export?format=csv"

st.write("מנסה לטעון נתונים...")

# טעינה ישירה ללא הגנות כדי לראות איפה זה נתקע
df = pd.read_csv(SHEET_URL)

st.success("הנתונים נטענו בהצלחה!")
st.write("הנה 5 השורות הראשונות של הגיליון שלך:")
st.write(df.head())
