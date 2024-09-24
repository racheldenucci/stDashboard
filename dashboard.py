import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title='Store Dashboard', page_icon=':bar-chart:', layout='wide')    #streamlit emoji shortcodes

st.title(":bar_chart: Store EDA")

fl = st.file_uploader(":file_folder: Upload file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\rache\Desktop\python streamlit\dashboard")
    df = pd.read_csv(r"Store.csv", encoding = "ISO-8859-1")
    