import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import datetime

# Page config
st.set_page_config(
    page_title="Stock Price Prediction Dashboard", page_icon="📈", layout="wide"
)

# Define constants
STOCK_SYMBOLS = [
    "RELIANCE.BO",
    "TCS.BO",
    "INFY.BO",
    "HDFCBANK.BO",
    "HINDUNILVR.BO",
    "BAJFINANCE.BO",
    "ITC.BO",
    "ICICIBANK.BO",
    "KOTAKBANK.BO",
    "LT.BO",
    "ASIANPAINT.BO",
    "HCLTECH.BO",
    "WIPRO.BO",
    "SUNPHARMA.BO",
    "ONGC.BO",
    "ULTRACEMCO.BO",
    "MARUTI.BO",
    "POWERGRID.BO",
    "TITAN.BO",
    "NTPC.BO",
    "BHARTIARTL.BO",
    "SBIN.BO",
    "TATAMOTORS.BO",
]

# Create a mapping of stock symbols to company names for better display
STOCK_NAMES = {
    "RELIANCE.BO": "Reliance Industries",
    "TCS.BO": "Tata Consultancy Services",
    "INFY.BO": "Infosys",
    "HDFCBANK.BO": "HDFC Bank",
    "HINDUNILVR.BO": "Hindustan Unilever",
    "BAJFINANCE.BO": "Bajaj Finance",
    "ITC.BO": "ITC Limited",
    "ICICIBANK.BO": "ICICI Bank",
    "KOTAKBANK.BO": "Kotak Mahindra Bank",
    "LT.BO": "Larsen & Toubro",
    "ASIANPAINT.BO": "Asian Paints",
    "HCLTECH.BO": "HCL Technologies",
    "WIPRO.BO": "Wipro",
    "SUNPHARMA.BO": "Sun Pharmaceutical",
    "ONGC.BO": "Oil and Natural Gas Corporation",
    "ULTRACEMCO.BO": "UltraTech Cement",
    "MARUTI.BO": "Maruti Suzuki",
    "POWERGRID.BO": "Power Grid Corporation",
    "TITAN.BO": "Titan Company",
    "NTPC.BO": "National Thermal Power Corporation",
    "BHARTIARTL.BO": "Bharti Airtel",
    "SBIN.BO": "State Bank of India",
    "TATAMOTORS.BO": "Tata Motors",
}


# Function to load data
def load_stock_data(symbol):
    """Load historical and prediction data for a given stock symbol"""
    try:
        # Use the file structure provided - data/ for historical and predictions/ for predictions
        historical_file = os.path.join("data", f"{symbol}.csv")
        prediction_file = os.path.join("predictions", f"{symbol}.csv")

        historical_data = pd.read_csv(historical_file)
        prediction_data = pd.read_csv(prediction_file)

        # Convert Date columns to datetime
        historical_data["Date"] = pd.to_datetime(historical_data["Date"])
        prediction_data["Date"] = pd.to_datetime(prediction_data["Date"])

        return historical_data, prediction_data
    except Exception as e:
        st.error(f"Error loading data for {symbol}: {e}")
        return None, None


# Function to create interactive chart
def create_stock_chart(historical_data, prediction_data, symbol):
    """Create an interactive plotly chart with historical data and predictions"""
    if historical_data is None or prediction_data is None:
        return None

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add historical price trace
    fig.add_trace(
        go.Scatter(
            x=historical_data["Date"],
            y=historical_data["Close"],
            name="Historical Price",
            line=dict(color="blue"),
            hovertemplate="%{x}<br>Price: ₹%{y:.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Add prediction price trace
    fig.add_trace(
        go.Scatter(
            x=prediction_data["Date"],
            y=prediction_data["Close"],
            name="Predicted Price",
            line=dict(color="red", dash="dash"),
            hovertemplate="%{x}<br>Predicted: ₹%{y:.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Add volume as bar chart if available
    if "Volume" in historical_data.columns:
        fig.add_trace(
            go.Bar(
                x=historical_data["Date"],
                y=historical_data["Volume"],
                name="Volume",
                marker=dict(color="rgba(0, 128, 0, 0.3)"),
                hovertemplate="%{x}<br>Volume: %{y:,}<extra></extra>",
            ),
            secondary_y=True,
        )

    # Add vertical line to separate historical from prediction
    # Convert timestamp to Unix timestamp (milliseconds) for Plotly
    last_historical_date = historical_data["Date"].max().timestamp() * 1000

    fig.add_vline(
        x=last_historical_date,
        line_width=2,
        line_dash="dash",
        line_color="green",
        annotation_text="Prediction Starts",
        annotation_position="top right",
    )

    # Update layout
    fig.update_layout(
        title=f"{STOCK_NAMES.get(symbol, symbol)} Stock Price Analysis",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        template="plotly_white",
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Price (₹)", secondary_y=False)
    if "Volume" in historical_data.columns:
        fig.update_yaxes(title_text="Volume", secondary_y=True)

    return fig


# Function to calculate performance metrics
def calculate_metrics(historical_data, prediction_data):
    """Calculate key stock performance metrics"""
    if historical_data is None or len(historical_data) == 0:
        return {}

    metrics = {}

    # Current price and change
    latest_price = historical_data["Close"].iloc[-1]
    prev_price = historical_data["Close"].iloc[-2] if len(historical_data) > 1 else None

    metrics["latest_price"] = latest_price
    if prev_price:
        daily_change = (latest_price - prev_price) / prev_price * 100
        metrics["daily_change"] = daily_change

    # Weekly change (5 trading days)
    if len(historical_data) > 5:
        week_ago_price = historical_data["Close"].iloc[
            -6
        ]  # -6 because we include today
        weekly_change = (latest_price - week_ago_price) / week_ago_price * 100
        metrics["weekly_change"] = weekly_change

    # Monthly change (21 trading days)
    if len(historical_data) > 21:
        month_ago_price = historical_data["Close"].iloc[
            -22
        ]  # -22 because we include today
        monthly_change = (latest_price - month_ago_price) / month_ago_price * 100
        metrics["monthly_change"] = monthly_change

    # Prediction metrics
    if prediction_data is not None and len(prediction_data) > 0:
        future_price = prediction_data["Close"].iloc[-1]
        predicted_change = (future_price - latest_price) / latest_price * 100
        metrics["predicted_future_price"] = future_price
        metrics["predicted_change"] = predicted_change

    return metrics


# Main app layout
def main():
    st.title("📈 Stock Price Prediction Dashboard")

    # Sidebar for stock selection
    st.sidebar.header("Select Stock")

    # Create a dropdown with company names but store symbol values
    stock_options = {
        STOCK_NAMES.get(symbol, symbol): symbol for symbol in STOCK_SYMBOLS
    }
    selected_stock_name = st.sidebar.selectbox(
        "Choose a stock:", list(stock_options.keys())
    )
    selected_stock = stock_options[selected_stock_name]

    # Load data
    historical_data, prediction_data = load_stock_data(selected_stock)

    # If data loaded successfully
    if historical_data is not None and prediction_data is not None:
        # Display metrics in cards
        metrics = calculate_metrics(historical_data, prediction_data)

        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Price",
                f"₹{metrics.get('latest_price', 0):.2f}",
                (
                    f"{metrics.get('daily_change', 0):.2f}%"
                    if "daily_change" in metrics
                    else None
                ),
            )

        with col2:
            st.metric(
                "Weekly Change",
                (
                    f"{metrics.get('weekly_change', 0):.2f}%"
                    if "weekly_change" in metrics
                    else "N/A"
                ),
            )

        with col3:
            st.metric(
                "Monthly Change",
                (
                    f"{metrics.get('monthly_change', 0):.2f}%"
                    if "monthly_change" in metrics
                    else "N/A"
                ),
            )

        with col4:
            st.metric(
                "Predicted (End of Period)",
                f"₹{metrics.get('predicted_future_price', 0):.2f}",
                (
                    f"{metrics.get('predicted_change', 0):.2f}%"
                    if "predicted_change" in metrics
                    else None
                ),
            )

        # Date range selector
        st.sidebar.header("Date Range")

        # Get min and max dates from data - convert pandas Timestamp to Python datetime objects
        min_date = historical_data["Date"].min().to_pydatetime().date()
        max_pred_date = prediction_data["Date"].max().to_pydatetime().date()

        # Calculate default start date (30 days after min_date) using timedelta
        default_start_date = min(min_date + timedelta(days=30), max_pred_date)

        # Date inputs
        start_date = st.sidebar.date_input(
            "Start Date",
            default_start_date,
            min_value=min_date,
            max_value=max_pred_date,
        )

        end_date = st.sidebar.date_input(
            "End Date", max_pred_date, min_value=min_date, max_value=max_pred_date
        )

        # Create copies for filtering
        historical_copy = historical_data.copy()
        prediction_copy = prediction_data.copy()

        # Create date objects for filtering
        historical_copy["Date_filter"] = historical_copy["Date"].dt.date
        prediction_copy["Date_filter"] = prediction_copy["Date"].dt.date

        # Filter data based on date range
        filtered_hist = historical_copy[
            (historical_copy["Date_filter"] >= start_date)
            & (historical_copy["Date_filter"] <= end_date)
        ].drop("Date_filter", axis=1)

        filtered_pred = prediction_copy[
            (prediction_copy["Date_filter"] >= start_date)
            & (prediction_copy["Date_filter"] <= end_date)
        ].drop("Date_filter", axis=1)

        # Create chart
        fig = create_stock_chart(filtered_hist, filtered_pred, selected_stock)

        if fig:
            st.plotly_chart(fig, use_container_width=True)

            # Additional options
            with st.expander("Show Data Tables"):
                tab1, tab2 = st.tabs(["Historical Data", "Prediction Data"])
                with tab1:
                    st.dataframe(filtered_hist, use_container_width=True)
                with tab2:
                    st.dataframe(filtered_pred, use_container_width=True)
        else:
            st.error("Could not create chart. Please check your data files.")
    else:
        st.error(
            f"""
            Could not load data for {selected_stock}.
            
            Please ensure you have CSV files named:
            - data/{selected_stock}.csv (historical data)
            - predictions/{selected_stock}.csv (prediction data)
            
            Both files should contain at minimum columns for 'Date' and 'Close' price.
        """
        )

    # Add information about the app
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        This dashboard visualizes historical stock prices and predictions.
        
        **Data Sources:**
        - Historical data: data/[STOCK_SYMBOL].csv
        - Prediction data: predictions/[STOCK_SYMBOL].csv
    """
    )


if __name__ == "__main__":
    main()
