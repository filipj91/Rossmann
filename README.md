# Rossmann Sales Forecasting

This repository contains a pipeline for forecasting sales based on Rossmann's data, using data processing techniques and time series modeling.

## Workflow

1. **Data Loading**
   - Load training and store data.
   - Data cleaning: removing closed stores and days with no sales, filling missing store data values.

2. **Feature Engineering**
   - Create time-related features (`Year`, `Month`, `Day`, `WeekOfYear`).
   - Calculate `SalePerCustomer`.

3. **Analysis and Visualization**
   - ECDF for `Sales`, `Customers`, `SalePerCustomer`.
   - Sales trends analysis by store type and promotion.

4. **Forecasting**
   - Time series modeling using the Prophet algorithm.
   - Sales forecast for the next 6 weeks for Store 1.

## Interactive Application

Explore the interactive Streamlit app 
[https://rossmann-project.streamlit.app](https://rossmann-project.streamlit.app)

## Apache Spark (Previous Implementation)

The project was initially implemented using **Apache Spark** on **Databricks** to efficiently handle large datasets.
