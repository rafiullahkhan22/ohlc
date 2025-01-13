import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load the data
file_path = r".\commodities_with_names_and_tickers_cleaned.csv"
data = pd.read_csv(file_path)

# Ensure the Date column is in datetime format and timezone-aware
data["Date"] = pd.to_datetime(data["Date"], utc=True)

# Title of the dashboard
st.title("Commodities Financial Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")

# Dropdown to select a commodity
commodity = st.sidebar.selectbox("Select Commodity:", data["Commodity Name"].unique())

# Date range filter
start_date = st.sidebar.date_input("Start Date", data["Date"].min().date())
end_date = st.sidebar.date_input("End Date", data["Date"].max().date())

# Convert start_date and end_date to timezone-aware datetime objects
start_date = pd.Timestamp(start_date).tz_localize("UTC")
end_date = pd.Timestamp(end_date).tz_localize("UTC")

# Filter data based on user input
filtered_data = data[(data["Commodity Name"] == commodity) &
                     (data["Date"] >= start_date) &
                     (data["Date"] <= end_date)]

# Display filtered data
st.subheader(f"Filtered Data for {commodity}")
st.dataframe(filtered_data)

# Enhanced Candlestick Chart with Clear Wicks
st.subheader(f"Enhanced Candlestick Chart with Wicks for {commodity}")
if not filtered_data.empty:
    # Compute SMA and EMA for overlay
    filtered_data['SMA'] = filtered_data['Close'].rolling(window=5).mean()
    filtered_data['EMA'] = filtered_data['Close'].ewm(span=5, adjust=False).mean()

    # Create the candlestick chart
    fig = go.Figure()

    # Add candlestick traces with wicks
    fig.add_trace(go.Candlestick(
        x=filtered_data["Date"],
        open=filtered_data["Open"],
        high=filtered_data["High"],
        low=filtered_data["Low"],
        close=filtered_data["Close"],
        increasing_line_color='green',  # Bullish candles
        decreasing_line_color='red',    # Bearish candles
        increasing_fillcolor='green',
        decreasing_fillcolor='red',
        whiskerwidth=0.4                # Emphasizes the horizontal line (wicks)
    ))

    # Overlay SMA and EMA
    fig.add_trace(go.Scatter(
        x=filtered_data["Date"],
        y=filtered_data["SMA"],
        mode='lines',
        name='SMA (5)',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=filtered_data["Date"],
        y=filtered_data["EMA"],
        mode='lines',
        name='EMA (5)',
        line=dict(color='orange', width=2, dash='dot')
    ))

    # Customize layout for aesthetics
    fig.update_layout(
        title=f"Enhanced Candlestick Chart with Moving Averages for {commodity}",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",  # Clean background
        xaxis_rangeslider_visible=False,  # Hide range slider for a cleaner look
        yaxis=dict(showgrid=True),
        xaxis=dict(showgrid=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Display the chart
    st.plotly_chart(fig)
else:
    st.warning("No data available for the selected filters.")

# Volume Bar Chart
st.subheader(f"Trading Volume for {commodity}")
if not filtered_data.empty:
    fig_volume = go.Figure(data=[go.Bar(
        x=filtered_data["Date"],
        y=filtered_data["Volume"],
        name="Volume"
    )])
    fig_volume.update_layout(
        title=f"Trading Volume for {commodity}",
        xaxis_title="Date",
        yaxis_title="Volume"
    )
    st.plotly_chart(fig_volume)
else:
    st.warning("No volume data available for the selected filters.")

# Moving Average
st.subheader(f"Moving Averages for {commodity}")
if not filtered_data.empty:
    filtered_data['SMA'] = filtered_data['Close'].rolling(window=5).mean()
    filtered_data['EMA'] = filtered_data['Close'].ewm(span=5, adjust=False).mean()

    fig_ma = px.line(filtered_data, x='Date', y=['Close', 'SMA', 'EMA'], 
                     labels={"value": "Price", "variable": "Type"},
                     title="Close Price with SMA and EMA")
    st.plotly_chart(fig_ma)
else:
    st.warning("Not enough data for moving averages.")

# Daily Percentage Change
st.subheader(f"Daily Percentage Change for {commodity}")
if not filtered_data.empty:
    filtered_data['Daily Change (%)'] = filtered_data['Close'].pct_change() * 100

    fig_change = px.bar(filtered_data, x='Date', y='Daily Change (%)',
                        title="Daily Percentage Change")
    st.plotly_chart(fig_change)
else:
    st.warning("Not enough data for daily change visualization.")

# Price Distribution
st.subheader(f"Price Distribution for {commodity}")
if not filtered_data.empty:
    fig_hist = px.histogram(filtered_data, x='Close', nbins=20, title="Price Distribution")
    st.plotly_chart(fig_hist)
else:
    st.warning("No data for price distribution.")

# Summary Metrics
st.sidebar.subheader("Summary Metrics")
if not filtered_data.empty:
    st.sidebar.metric("Total Days", len(filtered_data))
    st.sidebar.metric("Average Close Price", round(filtered_data["Close"].mean(), 2))
    st.sidebar.metric("Max High Price", round(filtered_data["High"].max(), 2))
    st.sidebar.metric("Min Low Price", round(filtered_data["Low"].min(), 2))
    st.sidebar.metric("Total Volume", int(filtered_data["Volume"].sum()))
    st.sidebar.metric("Volatility (Std Dev)", round(filtered_data["Close"].std(), 2))
else:
    st.sidebar.write("No data available for summary metrics.")
