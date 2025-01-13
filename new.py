import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime

# Fetch data for commodities
def fetch_commodities_data(commodities, start_date=None, end_date=None):
    results = {}
    for name, ticker in commodities.items():
        try:
            commodity = yf.Ticker(ticker)
            if start_date and end_date:
                data = commodity.history(start=start_date, end=end_date)
            else:
                data = commodity.history(period="max")
            
            if not data.index.freq == 'D':
                data = data.resample('D').last()
            
            data = data.dropna(subset=['Open', 'High', 'Low', 'Close'], how='all')
            data['Commodity Name'] = name
            data['Ticker'] = ticker
            results[name] = data
        except Exception as e:
            print(f"Error fetching data for {name} ({ticker}): {e}")
    return results

# Commodity names and their corresponding tickers
COMMODITIES = {
# Precious Metals
    'Gold': 'GC=F',
    'Silver': 'SI=F',
    'Platinum': 'PL=F',
    'Palladium': 'PA=F',

    # Energy
    'Crude Oil WTI': 'CL=F',
    'Crude Oil Brent': 'BZ=F',
    'Natural Gas': 'NG=F',
    'Heating Oil': 'HO=F',
    'Ethanol': 'EH=F',

    # Industrial Metals
    'Copper': 'HG=F',
    'Aluminum': 'ALI=F',
    'Zinc': 'ZI=F',
    'Nickel': 'NI=F',
    'Lead': 'LL=F',
    'Tin': 'TIN=F',

    # Agriculture
    'Corn': 'ZC=F',
    'Soybeans': 'ZS=F',
    'Wheat': 'ZW=F',
    'Oats': 'ZO=F',
    'Rough Rice': 'ZR=F',
    'Canola': 'RS=F',
    'Cotton': 'CT=F',
    'Sugar': 'SB=F',
    'Cocoa': 'CC=F',
    'Coffee': 'KC=F',
    'Orange Juice': 'OJ=F',
    'Soybean Oil': 'BO=F',
    'Soybean Meal': 'SM=F',
    'Palm Oil': 'PAL=F',
    'Rapeseed': 'RAP=F',
    'Barley': 'BAR=F',
    'Sunflower Oil': 'SUN=F',

    # Livestock
    'Live Cattle': 'LE=F',
    'Lean Hogs': 'HE=F',
    'Feeder Cattle': 'GF=F',

    # Soft Commodities
    'Rubber': 'TRB=F',
    'Lumber': 'LB=F',

    # Dairy
    'Milk': 'DL=F',

    # Cryptocurrency Futures
    'Bitcoin Futures': 'BTC=F',
    'Ethereum Futures': 'ETH=F',

    # Miscellaneous
    'Uranium': 'UX=F',
    'Cobalt': 'COB=F',
    'Lithium': 'LIT=F'
}

# Streamlit app
st.title("Commodities Financial Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")
commodity = st.sidebar.selectbox("Select Commodity:", COMMODITIES.keys())
start_date = st.sidebar.date_input("Start Date", datetime(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now().date())

# Fetch data dynamically
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')
commodities_data = fetch_commodities_data(COMMODITIES, start_date_str, end_date_str)

# Combine data into a single DataFrame
if commodities_data:
    combined_data = pd.concat(commodities_data.values())
else:
    combined_data = pd.DataFrame()

# Filter data based on selected commodity
filtered_data = combined_data[combined_data["Commodity Name"] == commodity]

# Dashboard visualizations
if not filtered_data.empty:
    # Convert Date to datetime for consistency
    filtered_data = filtered_data.reset_index()
    filtered_data["Date"] = pd.to_datetime(filtered_data["Date"], utc=True)

    # Display filtered data
    st.subheader(f"Filtered Data for {commodity}")
    st.dataframe(filtered_data)

    # Candlestick Chart
    st.subheader(f"Candlestick Chart for {commodity}")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=filtered_data["Date"],
        open=filtered_data["Open"],
        high=filtered_data["High"],
        low=filtered_data["Low"],
        close=filtered_data["Close"],
        increasing_line_color='green',
        decreasing_line_color='red'
    ))
    fig.update_layout(title=f"Candlestick Chart for {commodity}", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    # Volume Bar Chart
    st.subheader(f"Trading Volume for {commodity}")
    fig_volume = px.bar(filtered_data, x='Date', y='Volume', title="Trading Volume")
    st.plotly_chart(fig_volume)

    # Daily Change
    st.subheader(f"Daily Percentage Change for {commodity}")
    filtered_data['Daily Change (%)'] = filtered_data['Close'].pct_change() * 100
    fig_change = px.bar(filtered_data, x='Date', y='Daily Change (%)', title="Daily Percentage Change")
    st.plotly_chart(fig_change)

    # Price Distribution
    st.subheader(f"Price Distribution for {commodity}")
    fig_hist = px.histogram(filtered_data, x='Close', nbins=20, title="Price Distribution")
    st.plotly_chart(fig_hist)

# Moving Averages Chart
st.subheader(f"Moving Averages (20, 50, 200 Days) for {commodity}")
if not filtered_data.empty:
    # Calculate moving averages
    filtered_data['MA_20'] = filtered_data['Close'].rolling(window=20).mean()
    filtered_data['MA_50'] = filtered_data['Close'].rolling(window=50).mean()
    filtered_data['MA_200'] = filtered_data['Close'].rolling(window=200).mean()

    # Plot the chart
    fig_ma = go.Figure()

    # Add Close price
    fig_ma.add_trace(go.Scatter(
        x=filtered_data['Date'], 
        y=filtered_data['Close'], 
        mode='lines', 
        name='Close Price', 
        line=dict(color='blue')
    ))

    # Add 20-day MA
    fig_ma.add_trace(go.Scatter(
        x=filtered_data['Date'], 
        y=filtered_data['MA_20'], 
        mode='lines', 
        name='20-Day MA', 
        line=dict(color='orange')
    ))

    # Add 50-day MA
    fig_ma.add_trace(go.Scatter(
        x=filtered_data['Date'], 
        y=filtered_data['MA_50'], 
        mode='lines', 
        name='50-Day MA', 
        line=dict(color='green')
    ))

    # Add 200-day MA
    fig_ma.add_trace(go.Scatter(
        x=filtered_data['Date'], 
        y=filtered_data['MA_200'], 
        mode='lines', 
        name='200-Day MA', 
        line=dict(color='red')
    ))

    # Customize layout
    fig_ma.update_layout(
        title=f"Moving Averages (20, 50, 200 Days) for {commodity}",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white"
    )

    # Display chart
    st.plotly_chart(fig_ma)
else:
    st.warning("Not enough data to calculate moving averages.")


    
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
    st.sidebar.warning("No data available for summary metrics.")

# Warning for empty dataset
if filtered_data.empty:
    st.warning("No data available for the selected filters.")
