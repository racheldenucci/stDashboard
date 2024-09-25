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
    
#date filter
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"]<= date2)].copy()

#sidebar filters
st.sidebar.header("Filters: ")

#region
region = st.sidebar.multiselect("Region", df["Region"].unique())
if not region:
    df_region = df.copy()
else:
    df_region = df[df["Region"].isin(region)] #df2

#state
state = st.sidebar.multiselect("State", df_region["State"].unique())   #df2 was already filtered before
if not state:
    df_state = df_region.copy()    #if theres no state selected, it will show the filtered dataframe only by region 
else:
    df_state = df_region[df_region["State"].isin(state)] #df3

#city
city = st.sidebar.multiselect("City", df_state["City"].unique())
if not city:
    df_city = df_state.copy()
else:
    df_city = df_state[df_state["City"].isin(city)] #df4

#filtering the data              IMPOSSÍVEL ISSO AQUI SER O MELHOR JEITO DE FAZER ISSO 
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df_state[df["State"].isin(region) & df_state["City"].isin(city)]
elif region and city:
    filtered_df = df_state[df["Region"].isin(state) & df_state["City"].isin(city)]
elif region and state:
    filtered_df = df_state[df["Region"].isin(region) & df_state["State"].isin(state)]
elif city:
    filtered_df = df_state[df_state["City"].isin(city)]
else:
    filtered_df = df_state[df_state["Region"].isin(region) & df_state["State"].isin(state) & df_state["City"].isin(city)]


category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Sales per Category")
    fig = px.bar(category_df, x = "Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True, height = 200)

with col2:
    st.subheader("Sales by Region")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5,  template="plotly_dark")
    fig.update_traces(text=filtered_df["Region"], textposition="outside",  marker=dict(colors=['#003f5c', '#bc5090', '#ff6361', '#ffa600'])) #textinfo='label+value',
    st.plotly_chart(fig, use_container_width=True)