import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Store Dashboard", page_icon=":bar-chart:", layout="wide"
)  # streamlit emoji shortcodes

st.title(":bar_chart: Store EDA")

fl = st.file_uploader(":file_folder: Upload file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir(r"C:\Users\rache\Desktop\python streamlit\dashboard")
    df = pd.read_csv(r"Store.csv", encoding="ISO-8859-1")

# date filter
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# sidebar filters
st.sidebar.header("Filters: ")

# region
region = st.sidebar.multiselect("Region", df["Region"].unique())
if not region:
    df_region = df.copy()
else:
    df_region = df[df["Region"].isin(region)]  # df2

# state
state = st.sidebar.multiselect(
    "State", df_region["State"].unique()
)  # df2 was already filtered before
if not state:
    df_state = (
        df_region.copy()
    )  # if theres no state selected, it will show the filtered dataframe only by region
else:
    df_state = df_region[df_region["State"].isin(state)]  # df3

# city
city = st.sidebar.multiselect("City", df_state["City"].unique())
if not city:
    df_city = df_state.copy()
else:
    df_city = df_state[df_state["City"].isin(city)]  # df4

# filtering the data              !!!IMPOSSÍVEL ISSO AQUI SER O MELHOR JEITO DE FAZER ISSO!!!
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df_state[df["State"].isin(state) & df_state["City"].isin(city)]
elif region and city:
    filtered_df = df_state[df["Region"].isin(region) & df_state["City"].isin(city)]
elif region and state:
    filtered_df = df_state[df["Region"].isin(region) & df_state["State"].isin(state)]
elif city:
    filtered_df = df_state[df_state["City"].isin(city)]
else:
    filtered_df = df_state[
        df_state["Region"].isin(region)
        & df_state["State"].isin(state)
        & df_state["City"].isin(city)
    ]


category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Sales per Category")
    fig = px.bar(
        category_df,
        x="Category",
        y="Sales",
        text=["${:,.2f}".format(x) for x in category_df["Sales"]],
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Sales by Region")
    fig = px.pie(
        filtered_df, values="Sales", names="Region", hole=0.5, template="plotly_dark"
    )
    fig.update_traces(
        text=filtered_df["Region"],
        textposition="outside",
        marker=dict(colors=["#003f5c", "#bc5090", "#ff6361", "#ffa600"]),
    )  # textinfo='label+value',
    st.plotly_chart(fig, use_container_width=True)


cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="category.csv",
            mime="text/csv",
            help="Click to download CSV file",
        )

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="region.csv",
            mime="text/csv",
            help="Click to download CSV file",
        )

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period(
    "M"
)  # adds new column to df
st.subheader("Time Series Analysis")

line_chart = pd.DataFrame(
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
).reset_index()
fig2 = px.line(
    line_chart,
    x="month_year",
    y="Sales",
    labels={"Sales": "Amount"},
    height=500,
    width=1000,
    template="gridon",
)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Time Series Data: "):
    st.write(line_chart.T.style.background_gradient(cmap="Blues"))
    csv = line_chart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data", data=csv, file_name="Time Series.csv", mime="text/csv"
    )

# tree map view
st.subheader("Treemap Sales View")
fig3 = px.treemap(
    filtered_df,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    hover_data=["Sales"],
    color="Sub-Category",
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Sales by Segment")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)


with chart2:
    st.subheader("Sales by Category")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# see specific columns data
import plotly.figure_factory as ff

st.header(":point_right: Sub-Category Sales Monthly Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][
        ["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]
    ]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(
        data=filtered_df, values="Sales", index=["Sub-Category"], columns="month"
    )
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(
    title="Sales x Profit Relationship",
    titlefont=dict(size=20),
    xaxis=dict(title="Sales", titlefont=dict(size=18)),
    yaxis=dict(title="Profit", titlefont=dict(size=18)),
)

st.plotly_chart(data1, use_container_width=True)