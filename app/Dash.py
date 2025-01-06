# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NmtFLQFOvwob_TP9XrykDYTIXOMm65Si
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
import os


st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #ADD8E6; /* Light blue background */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white; /* White text */
    }

    /* Header */
    .main-header {
        font-size: 36px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        padding: 20px;
        border-radius: 10px;
        background-color: #3B82F6; /* Blue gradient */
    }

    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #1E40AF;
        color: white;
    }

    .sidebar .sidebar-content .css-1d391kg {
        color: #fff;
    }

    /* Metric cards */
    .stMetricValue {
        font-size: 28px;
        color: white !important; /* Ensuring white text for metric values */
        text-align: center;
    }

    /* Charts */
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        padding: 20px;
    }

    /* Streamlit's default metric color adjustment */
    .stMetric .stMetricValue {
        color: white !important;  /* Override default metric text color to white */
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():

    train_path = "DataSet/train.csv"
    store_path = "DataSet/store.csv"


    if not os.path.exists(train_path):
        raise FileNotFoundError(f"File not found: {train_path}")

    if not os.path.exists(store_path):
        raise FileNotFoundError(f"File not found: {store_path}")

    # Load the data
    train = pd.read_csv(train_path, parse_dates=['Date'], low_memory=False, index_col='Date')
    store = pd.read_csv(store_path, low_memory=False)

    # Data cleaning
    train = train[(train["Open"] != 0) & (train['Sales'] != 0)]
    store['CompetitionDistance'].fillna(store['CompetitionDistance'].median(), inplace=True)
    store.fillna(0, inplace=True)
    train['Year'] = train.index.year
    train['Month'] = train.index.month
    train['Day'] = train.index.day
    train['WeekOfYear'] = train.index.isocalendar().week
    train['SalePerCustomer'] = train['Sales'] / train['Customers']
    train.reset_index(inplace=True)


    train_store = pd.merge(train, store, how='inner', on='Store')

    return train_store, store

st.title("📊 Rossmann Sales Dashboard")

data, store_info = load_data()


st.sidebar.header("Data Filtering")
store_id = st.sidebar.selectbox("Select Store:", data['Store'].unique())

store_type = store_info.loc[store_info['Store'] == store_id, 'StoreType'].values[0]
selected_data = data[data['Store'] == store_id]
date_range = st.sidebar.date_input(
    "Date Range:",
    [selected_data['Date'].min(), selected_data['Date'].max()]
)
filtered_data = selected_data[
    (selected_data['Date'] >= pd.to_datetime(date_range[0])) &
    (selected_data['Date'] <= pd.to_datetime(date_range[1]))
]

# Main metrics
st.header(f"📈 Statistics for Store {store_id} (Type: {store_type})")
col1, col2, col3 = st.columns(3)
col1.metric("Average Sales", f"{filtered_data['Sales'].mean():,.2f} PLN")
col2.metric("Average Customers", f"{filtered_data['Customers'].mean():,.2f}")
col3.metric("Promotions", f"{filtered_data['Promo'].sum()} days")


st.subheader("📅 Sales Over Time")
fig_sales = px.line(
    filtered_data,
    x='Date',
    y='Sales',
    title=f"Sales Over Time for Store {store_id}",
    labels={'Date': 'Date', 'Sales': 'Sales'},
    template='plotly_dark',
    line_shape='spline'
)
fig_sales.update_traces(line=dict(color="#60A5FA"))
st.plotly_chart(fig_sales, use_container_width=True)

# Sales vs Customers correlation with animation
st.subheader("🛍️ Correlation: Sales vs Customers")
fig_corr = px.scatter(
    filtered_data,
    x='Customers',
    y='Sales',
    size='Sales',
    color='Promo',
    animation_frame='Month',
    title="Correlation: Sales vs Customers",
    labels={'Customers': 'Customers', 'Sales': 'Sales', 'Promo': 'Promotions'},
    template='plotly_dark'
)
st.plotly_chart(fig_corr, use_container_width=True)

# Sales forecast with dynamic chart
if st.sidebar.checkbox("Show Sales Forecast (6 months)"):
    st.subheader("🔮 Sales Forecast")
    sales = filtered_data[['Date', 'Sales']].rename(columns={'Date': 'ds', 'Sales': 'y'})
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(sales)
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    fig_forecast = px.line(
        forecast,
        x='ds',
        y=['yhat', 'yhat_lower', 'yhat_upper'],
        title="6-Month Sales Forecast",
        labels={'ds': 'Date', 'value': 'Forecast'},
        template='plotly_dark'
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

# Adding Databricks and Spark note
st.markdown("---")
st.markdown("### 🛠️ Technical Note:")

st.markdown("""
This project was originally implemented using **Apache Spark** on **Databricks**
to handle large datasets efficiently. Below is an overview of the workflow used in the Spark implementation:
""")

st.code("""
from pyspark.sql import SparkSession

# Initializing Spark Session
spark = SparkSession.builder.appName("Rossmann Sales Analysis").getOrCreate()

# Loading datasets
train = spark.read.csv("/dbfs/FileStore/train.csv", header=True, inferSchema=True)
store = spark.read.csv("/dbfs/FileStore/store.csv", header=True, inferSchema=True)

# Data cleaning and transformations
train = train.filter((train["Open"] != 0) & (train['Sales'] != 0))
store = store.fillna({'CompetitionDistance': store.agg({'CompetitionDistance': 'median'}).collect()[0][0]})
train = train.withColumn("SalePerCustomer", train["Sales"] / train["Customers"])

# Joining datasets
train_store = train.join(store, on="Store", how="inner")
train_store.show()
""", language="python")

# Short summary
st.markdown("""
This example showcases how **Spark** and **Databricks** were used for scalable and distributed data processing.
However, due to the high infrastructure costs associated with running **Databricks** and **Apache Spark**,
alongside the relatively smaller dataset size for this dashboard's use case,
the final implementation transitioned to using **Pandas** for cost efficiency and easier integration with Streamlit.
""")