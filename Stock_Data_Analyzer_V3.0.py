import streamlit as st
import yfinance as yf
import pandas as pd
from urllib.error import HTTPError
import altair as alt
import ssl
import time
import json

ssl._create_default_https_context = ssl._create_unverified_context

def changeMonthType(quarter):
    x = quarter.split(" ")
    if len(x) < 2:
        return quarter
    month = x[0]
    year = x[1]

    if "jan" in month.lower():
        month = "01"
    elif "feb" in month.lower():
        month = "02"
    elif "mar" in month.lower():
        month = "03"
    elif "apr" in month.lower():
        month = "04"
    elif "may" in month.lower():
        month = "05"
    elif "jun" in month.lower():
        month = "06"
    elif "jul" in month.lower():
        month = "07"
    elif "aug" in month.lower():
        month = "08"
    elif "sep" in month.lower():
        month = "09"
    elif "oct" in month.lower():
        month = "10"
    elif "nov" in month.lower():
        month = "11"
    elif "dec" in month.lower():
        month = "12"

    return year + "/" + month

st.set_page_config('Stock Data Analyzer', page_icon="chart_with_upwards_trend", layout="wide")


col1, col2, col3 = st.columns((1, 2, 1))
col2.title('Analyze Stock/Index Data')

header = '''
<style>
    body{min-height: 100%}
    #MainMenu {visibility: hidden;}
    #analyze-stock-index-data {text-align: center;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .header
    {
        height: 70px;
        font-size: 10px;
        background-color: #071f45;
        position:fixed;
        top:0;
        width:100%;
        left:0;
        color:white;
    }

    ul {
      list-style-type: none;
      margin: 0;
    }

    li {
      float: left;
    }

    a:link {
      text-decoration: none;
      color: white;
    }

    a:visited {
      color: white;
    }

    a:hover {
      color: hotpink;
    }

    a:active {
      color: blue;
    }
</style>


<div class="header">
    <ul>
      <li style="padding: 6px 0px 0px 0px;"><h3 style="color: white;">STOCK DATA ANALYZER</h3></li>
      <li style="padding: 20px 60px 0px 0px; float: right;"><a href="#">About</a></li>
      <li style="padding: 20px 10px 0px 0px; float: right;"><a href="#">Contact</a></li>
      <li style="padding: 20px 10px 0px 0px; float: right;"><a target="_self" href="http://localhost:8501/">Home</a></li>
    </ul>
</div>

'''
st.markdown(header, unsafe_allow_html=True)

try:
    with open("india_company_data.txt", 'r', encoding='unicode_escape') as company_file:
        tickers = eval(company_file.read())
    with open("india_index_data.txt", 'r', encoding='unicode_escape') as index_file:
        tickers += eval(index_file.read())
except FileNotFoundError:
    st.error("Ticker data files (india_company_data.txt or india_index_data.txt) not found. Please ensure they are in the same directory as the script.")
    tickers = [] # Initialize as empty to prevent further errors
except Exception as e:
    st.error(f"Error reading ticker data files: {e}")
    tickers = []

stocks = ["Select.."]
for i in range(len(tickers)):
    stocks.append(tickers[i][1] + " : " + tickers[i][0])

selected_stock = col2.selectbox('Select Company/Index:', stocks, help="Select the stock/index name or type the stock/index name you want to search")

def load_data(ticker_full_string):
    """
    Output:
        info_data = Dict containing metrics such as PE, dividend yield, etc (from yfinance.Ticker().info)
        hist_data = pandas Dataframe containing historical data
        ticker_clean = The cleaned ticker symbol
        current_price = Latest closing price
    """
    ticker_clean = ticker_full_string.split(" : ")[1]
    print(f"Ticker is------: {ticker_clean}")
    
    info_data = {}
    hist_data = pd.DataFrame()
    current_price = None

    try:
        stock_ticker = yf.Ticker(ticker_clean)

        hist_data = stock_ticker.history(period="max", interval="1d")
        print("Hist_data------------", hist_data)
        hist_data = hist_data.reset_index()

        if hist_data.empty:
            st.error(f"No historical data found for {ticker_clean}. Please check the ticker symbol or try again later.")
            hist_data = pd.DataFrame()
        else:
            current_price = hist_data["Close"].iloc[-1]
            current_price = float(current_price)
        info_data = stock_ticker.info
        
        if not isinstance(info_data, dict) or not info_data:
            info_data = {}

    except Exception as e:
        st.error(f"Error loading data for {ticker_clean}: {e}")
        info_data = {}
        hist_data = pd.DataFrame()
        current_price = None

    return [info_data, hist_data, ticker_clean, current_price]

if selected_stock != "Select..":
    st.markdown("***")

    with st.spinner('Wait for it...'):
        data = load_data(selected_stock)
        metrics = data[0]
        df = data[1]
        ticker = data[2]
        current_price = data[3]

    col1, col2, col3, col4, col5, col6 = st.columns((1.3, 2.5, 2, 2, 2, 0.5))

    if current_price is None:
        col2.metric("Current Price", "₹ " + "N/A")
    else:
        col2.metric("Current Price", "₹ " + format(current_price, ".2f"))

    col3.metric("P/E", metrics.get('trailingPE', "N/A"))
    col4.metric("Day Low", "₹ " + str(metrics.get('dayLow', "N/A")))
    col5.metric("Day High", "₹ " + str(metrics.get('dayHigh', "N/A")))

    dividend = metrics.get('dividendYield', "N/A")
    if dividend != "N/A":
        dividend = f"{dividend*100:.2f}%" # Format as percentage
    col2.metric("Dividend(%)", dividend)
    col3.metric("Dividend Payout Ratio", metrics.get('payoutRatio', "N/A"))
    col4.metric("Volume", metrics.get('volume', "N/A"))
    col5.metric("Average Volume", metrics.get('averageVolume', "N/A"))

    col2.metric("Market Cap", "₹ " + str(metrics.get('marketCap', "N/A")))
    col3.metric("Beta", metrics.get('beta', "N/A"))
    col4.metric("52-Week Low", "₹ " + str(metrics.get('fiftyTwoWeekLow', "N/A")))
    col5.metric("52-Week High", "₹ " + str(metrics.get('fiftyTwoWeekHigh', "N/A")))

    st.markdown("##")

    if not df.empty:
        col1, col2, col3 = st.columns((1, 6, 1))
        col2.subheader("Price Chart")
        col2.line_chart(df.set_index('Date')['Close'], use_container_width=True)
        st.text(" ")
    else:
        col1, col2, col3 = st.columns((1, 6, 1))
        col2.subheader("Price Chart (No data available)")

    if not df.empty:
        col1, col2, col3 = st.columns((1, 6, 1))
        col2.subheader('Historical Data')
        col2.dataframe(df, use_container_width=True)
        st.text(" ")
    else:
        col1, col2, col3 = st.columns((1, 6, 1))
        col2.subheader('Historical Data (No data available)')
    
    ticker_for_screener = selected_stock.split(" : ")[1]
    ticker_for_screener = ticker_for_screener.split(".")[0]
    url = f"https://www.screener.in/company/{ticker_for_screener}/consolidated/"

    try:
        tables = pd.read_html(url)

        quarterly_financial_result_df = tables[0] if len(tables) > 0 else pd.DataFrame()
        yearly_financial_result_df = tables[1] if len(tables) > 1 else pd.DataFrame()
        balance_sheet_df = tables[6] if len(tables) > 1 else pd.DataFrame()
        shareholding_pattern_df = tables[9] if len(tables) > 1 else pd.DataFrame()

        if not quarterly_financial_result_df.empty:
            quarterly_financial_result_df.rename(columns={"Unnamed: 0": "Quarter"}, inplace=True)
            quarterly_financial_result_df.replace(r"\+", "", regex=True, inplace=True)
            if len(quarterly_financial_result_df) > 0: # Ensure there's a row to delete
                 quarterly_financial_result_df.drop(quarterly_financial_result_df.index[len(quarterly_financial_result_df) - 1], inplace=True)
            quarterly_financial_result_df.set_index("Quarter", inplace=True)

        if not yearly_financial_result_df.empty:
            yearly_financial_result_df.rename(columns={"Unnamed: 0": "Year"}, inplace=True)
            yearly_financial_result_df.replace(r"\+", "", regex=True, inplace=True)
            yearly_financial_result_df.set_index("Year", inplace=True)

        if not balance_sheet_df.empty:
            balance_sheet_df.rename(columns={"Unnamed: 0": "Year"}, inplace=True)
            balance_sheet_df.replace(r"\+", "", regex=True, inplace=True)
            balance_sheet_df.set_index("Year", inplace=True)

        if not shareholding_pattern_df.empty:
            shareholding_pattern_df.rename(columns={"Unnamed: 0": "Quarter"}, inplace=True)
            shareholding_pattern_df.replace(r"\+", "", regex=True, inplace=True)
            shareholding_pattern_df.set_index("Quarter", inplace=True)

        col1, col2, col3 = st.columns((1, 6, 1))
        quarterly_tab, yearly_tab, balance_sheet_tab, shareholding_tab = col2.tabs(["Quarterly Financial Results", "Yearly Financial Results", "Balance Sheet", "Shareholding Pattern"])

        with quarterly_tab:
            st.subheader("Quarterly Financial Results")
            st.caption('Figures in Rs. Crores')
            if not quarterly_financial_result_df.empty:
                st.dataframe(quarterly_financial_result_df, use_container_width=True)
                st.text(" ")
                
                if not quarterly_financial_result_df.columns.empty and not quarterly_financial_result_df.index.empty:
                    revenue_list = quarterly_financial_result_df.iloc[[0]].values.tolist()
                    quarter_list = quarterly_financial_result_df.columns.values.tolist()

                    linechart_revenue_df = pd.DataFrame({"Quarter": list(quarter_list), "Revenue": list(revenue_list[0])})
                    linechart_revenue_df['Revenue'] = linechart_revenue_df['Revenue'].astype(float)
                    linechart_revenue_df['Quarter'] = linechart_revenue_df['Quarter'].map(lambda quarter: changeMonthType(quarter))

                    profit_column_name = ""
                    for i in quarterly_financial_result_df.index:
                        if "net profit" in i.lower():
                            profit_column_name = i
                            break
                    if profit_column_name:
                        profit_column_data = quarterly_financial_result_df.loc[profit_column_name].values.tolist()
                        linechart_profit_df = pd.DataFrame({"Quarter": list(quarter_list), profit_column_name: list(profit_column_data)})
                        linechart_profit_df['Quarter'] = linechart_profit_df['Quarter'].map(lambda quarter: changeMonthType(quarter))
                        linechart_profit_df[profit_column_name] = linechart_profit_df[profit_column_name].astype(float)

                        st.subheader('Revenue/Sales Line Chart')
                        st.line_chart(linechart_revenue_df, x="Quarter", y="Revenue", use_container_width=True)
                        st.text(" ")
                        st.subheader('Net Profit Line Chart')
                        st.line_chart(linechart_profit_df, x="Quarter", y=profit_column_name, use_container_width=True)
                    else:
                        st.warning("Net Profit data column not found in Quarterly Financial Results.")
                else:
                    st.warning("Quarterly Financial Results DataFrame has no columns or index, skipping charts.")
            else:
                st.info("No Quarterly Financial Results data available.")

        with yearly_tab:
            st.subheader("Yearly Financial Results")
            st.caption('Figures in Rs. Crores')
            if not yearly_financial_result_df.empty:
                st.dataframe(yearly_financial_result_df, use_container_width=True)
                st.text(" ")
                
                if not yearly_financial_result_df.columns.empty and not yearly_financial_result_df.index.empty:
                    revenue_list = yearly_financial_result_df.iloc[[0]].values.tolist()
                    quarter_list = yearly_financial_result_df.columns.values.tolist()

                    linechart_revenue_df = pd.DataFrame({"Quarter": list(quarter_list), "Revenue": list(revenue_list[0])})
                    linechart_revenue_df['Revenue'] = linechart_revenue_df['Revenue'].astype(float)
                    linechart_revenue_df['Quarter'] = linechart_revenue_df['Quarter'].map(lambda quarter: changeMonthType(quarter))

                    profit_column_name = ""
                    for i in yearly_financial_result_df.index:
                        if "net profit" in i.lower():
                            profit_column_name = i
                            break
                    if profit_column_name:
                        profit_column_data = yearly_financial_result_df.loc[profit_column_name].values.tolist()
                        linechart_profit_df = pd.DataFrame({"Quarter": list(quarter_list), profit_column_name: list(profit_column_data)})
                        linechart_profit_df['Quarter'] = linechart_profit_df['Quarter'].map(lambda quarter: changeMonthType(quarter))
                        linechart_profit_df[profit_column_name] = linechart_profit_df[profit_column_name].astype(float)

                        linechart_revenue_df.rename(columns={'Quarter': 'Year'}, inplace=True)
                        linechart_profit_df.rename(columns={'Quarter': 'Year'}, inplace=True)

                        st.subheader('Revenue/Sales Line Chart')
                        st.line_chart(linechart_revenue_df, x="Year", y="Revenue", use_container_width=True)
                        st.text(" ")

                        st.subheader('Net Profit Line Chart')
                        st.line_chart(linechart_profit_df, x="Year", y=profit_column_name, use_container_width=True)
                    else:
                        st.warning("Net Profit data column not found in Yearly Financial Results.")
                else:
                    st.warning("Yearly Financial Results DataFrame has no columns or index, skipping charts.")
            else:
                st.info("No Yearly Financial Results data available.")

        with balance_sheet_tab:
            st.subheader("Balance Sheet")
            st.caption('Figures in Rs. Crores')
            if not balance_sheet_df.empty:
                st.dataframe(balance_sheet_df, use_container_width=True)
                st.text(" ")
                
                if not balance_sheet_df.columns.empty and not balance_sheet_df.index.empty:
                    quarter_list = balance_sheet_df.columns.values.tolist()

                    liability_column_name = ""
                    for i in balance_sheet_df.index:
                        if "total liabilities" in i.lower():
                            liability_column_name = i
                            break
                    if liability_column_name:
                        liability_column_data = balance_sheet_df.loc[liability_column_name].values.tolist()
                        linechart_liability_df = pd.DataFrame({"Quarter": list(quarter_list), liability_column_name + "/Total Asset": list(liability_column_data)})
                        linechart_liability_df['Quarter'] = linechart_liability_df['Quarter'].map(lambda quarter: changeMonthType(quarter))
                        linechart_liability_df[liability_column_name + "/Total Asset"] = linechart_liability_df[liability_column_name + "/Total Asset"].astype(float)

                        linechart_liability_df.rename(columns={'Quarter': 'Year'}, inplace=True)

                        st.subheader('Assets & Liabilities Line Chart')
                        st.line_chart(linechart_liability_df, x="Year", y=liability_column_name + "/Total Asset", use_container_width=True)
                        st.text(" ")
                    else:
                        st.warning("Total Liabilities data column not found in Balance Sheet.")
                else:
                    st.warning("Balance Sheet DataFrame has no columns or index, skipping charts.")
            else:
                st.info("No Balance Sheet data available.")


        with shareholding_tab:
            st.subheader("Shareholding Pattern(%)")
            st.caption('Numbers in percentages')
            if not shareholding_pattern_df.empty:
                st.dataframe(shareholding_pattern_df, use_container_width=True)
                st.text(" ")

                if not shareholding_pattern_df.columns.empty and not shareholding_pattern_df.index.empty:
                    shareholder_list = shareholding_pattern_df.index.values.tolist()
                    if not shareholding_pattern_df.columns.empty:
                        percentage_list = shareholding_pattern_df[shareholding_pattern_df.columns[-1]].values.tolist()
                    else:
                        percentage_list = []

                    source = pd.DataFrame({"holders": list(shareholder_list), "percentage_holding": list(percentage_list)})
                    source['percentage_holding'] = pd.to_numeric(source['percentage_holding'], errors='coerce').fillna(0)

                    if not source.empty and source['percentage_holding'].sum() > 0:
                        fig_category_percent = alt.Chart(source, title="Latest Share Holding Pattern").mark_arc().encode(
                            theta=alt.Theta(field="percentage_holding", type="quantitative"),
                            color=alt.Color(field="holders", type="nominal"))
                        st.altair_chart(fig_category_percent, use_container_width=True)
                    else:
                        st.info("No valid shareholding percentage data to display chart.")
                else:
                    st.warning("Shareholding Pattern DataFrame has no columns or index, skipping chart.")
            else:
                st.info("No Shareholding Pattern data available.")

    except HTTPError as err:
        if err.code == 404:
            col1, col2, col3 = st.columns((1, 6, 1))
            quarterly_tab, yearly_tab, balance_sheet_tab, shareholding_tab = col2.tabs(["Quarterly Financial Results", "Yearly Financial Results", "Balance Sheet", "Shareholding Pattern"])

            with quarterly_tab:
                st.subheader("Quarterly Financial Results data not found")
            with yearly_tab:
                st.subheader("Yearly Financial Results data not found")
            with balance_sheet_tab:
                st.subheader("Balance Sheet not found")
            with shareholding_tab:
                st.subheader("Shareholding Pattern not found")
        else:
            st.error(f"Error loading data from screener.in for {ticker_for_screener}: {err}")

header = '''
<style>
    body{min-height: 100%}
    #MainMenu {visibility: hidden;}
    #analyze-stock-index-data {text-align: center;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .header
    {
        height: 70px;
        font-size: 10px;
        background-color: #071f45;
        position:fixed;
        top:0;
        width:100%;
        left:0;
        color:white;
    }

    ul {
      list-style-type: none;
      margin: 0;
    }

    li {
      float: left;
    }

    a:link {
      text-decoration: none;
      color: white;
    }

    a:visited {
      color: white;
    }

    a:hover {
      color: hotpink;
    }

    a:active {
      color: blue;
    }
    
    /*.sticky { position: fixed; top: 0; width: 100%;}*/
</style>


<div class="header">
    <ul>
      <li style="padding: 6px 0px 0px 0px; color: white;"><h3 style="color: white;">STOCK DATA ANALYZER</h3></li>
      <li style="padding: 20px 60px 0px 0px; float: right;"><a href="#">About</a></li>
      <li style="padding: 20px 10px 0px 0px; float: right;"><a href="#">Contact</a></li>
      <li style="padding: 20px 10px 0px 0px; float: right;"><a target="_self" href="http://localhost:8501/">Home</a></li>
    </ul>
</div>

'''
st.markdown(header, unsafe_allow_html=True)

footer='''
<style>
    .footer
    {
        position:absolute;
        width:100%;
        height: 50px;
        left: 0;
        padding: 10px 0px 0px 0px;
        bottom: 0;
        background-color: #071f45;
        top:420px;
    }
</style>

<div class='footer'>
    <center><p style="color: white;">Created with  ❤  by Soumajit Chatterjee</p></center>
</div>
'''
st.markdown(footer, unsafe_allow_html=True)
