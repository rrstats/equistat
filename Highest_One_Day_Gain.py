import datetime as dt
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import requests
import datetime as dt
import plotly.io as pio
import plotly.graph_objects as go
import streamlit as st


NIFTY_AUTO = ["ASHOKLEY.NS","BAJAJ-AUTO.NS","BALKRISIND.NS","BHARATFORG.NS","BOSCHLTD.NS","EICHERMOT.NS","HEROMOTOCO.NS","MRF.NS","M&M.NS","MARUTI.NS","MOTHERSON.NS","SONACOMS.NS","TVSMOTOR.NS","TATAMOTORS.NS","TIINDIA.NS"]
NIFTY_PHARMA = ["ABBOTINDIA.NS","ALKEM.NS","AUROPHARMA.NS","BIOCON.NS","CIPLA.NS","DIVISLAB.NS","DRREDDY.NS","GLAND.NS","GLAXO.NS","GLENMARK.NS","GRANULES.NS","IPCALAB.NS","LAURUSLABS.NS","LUPIN.NS","NATCOPHARM.NS","PFIZER.NS","SANOFI.NS","SUNPHARMA.NS","TORNTPHARM.NS","ZYDUSLIFE.NS"]
NIFTY_FMCG = ["BRITANNIA.NS","COLPAL.NS","DABUR.NS","EMAMILTD.NS","GODREJCP.NS","HINDUNILVR.NS","ITC.NS","MARICO.NS","NESTLEIND.NS","PGHH.NS","RADICO.NS","TATACONSUM.NS","UBL.NS","MCDOWELL-N.NS","VBL.NS"]
NIFTY_BANK = ["AUBANK.NS","AXISBANK.NS","BANDHANBNK.NS","BANKBARODA.NS","FEDERALBNK.NS","HDFCBANK.NS","ICICIBANK.NS","IDFCFIRSTB.NS","INDUSINDBK.NS","KOTAKBANK.NS","PNB.NS","SBIN.NS"]
NIFTY_IT = ["COFORGE.NS","HCLTECH.NS","INFY.NS","LTTS.NS","LTIM.NS","MPHASIS.NS","PERSISTENT.NS","TCS.NS","TECHM.NS","WIPRO.NS"]

############################################################

def date_format(date_str):
    #"2015-05-06"

    # Parse the date string to a datetime object
    date_obj = dt.datetime.strptime(str(date_str), "%Y-%m-%d  00:00:00")

    # Format the datetime object to the desired format
    formatted_date = date_obj.strftime("%b %d, '%y")

    return formatted_date  # Output: 06-May-15


def date_format2(date_str):
    # "2015-05-06"

    """  00:00:00 is not present"""
    # Parse the date string to a datetime object
    date_obj = dt.datetime.strptime(str(date_str), "%Y-%m-%d")


    # Format the datetime object to the desired format
    formatted_date = date_obj.strftime("%b %d, %Y")

    return formatted_date  # Output: 06-May-15

############################################################



st.set_page_config(
    page_title="Highest One-Day Gain",
    page_icon="👋",
)

# st.sidebar.success("Select a demo above.")


############################################################

st.title('Highest One-Day Gain')
st.write('The 52-week high is the highest price at which a stock has been traded in the past 52 weeks. ')
st.write('Charts below show smaller time intervals. ')

up_col1, up_col2 = st.columns(2)

with up_col1:
    number_of_months = st.radio(
        "Time Period",
         ('1 MONTH', '3 MONTHS', '6 MONTHS'),
        )

    number_of_months = int(number_of_months.split("MONTH")[0])

# with up_col2:
#     st.multiselect('Sectors', ["Automobiles", "Banking", "IT", "FMCG"],["Automobiles", "Banking", "IT", "FMCG"])

begin_date = dt.date.today() - dt.timedelta(number_of_months*365/12)

#############################################################


def data_create(tickers):
    small_caps_data = yf.Tickers(tickers).history(period=f"{number_of_months}mo")["Close"]

    # We download data from 01-01-2014 to 01-01-2024
    # If the first row of the column is null, we drop the columns
    # Hence, all companies which do have data since 2014 are in new_tickers
    new_tickers = small_caps_data[:1].dropna(axis=1).columns

    old_small_caps_data = small_caps_data[new_tickers]
    old_small_caps = old_small_caps_data.pct_change()[1:] * 100

    highest_gains = old_small_caps.max().to_frame()
    highest_gains["Stock"] = highest_gains.index
    highest_gains["Date"] = old_small_caps.idxmax()
    highest_gains["Date"] = highest_gains["Date"].apply(date_format)
    highest_gains["Date_Value"] = highest_gains["Date"] + highest_gains[0].apply(
        lambda x: " | " + str(round(x, 1)) + "%")
    highest_gains = highest_gains.sort_values(by=0, ascending=True)

    repeats = highest_gains.groupby(['Date']).size().reset_index(name='count')
    highest_gains_new = pd.merge(highest_gains, repeats, on='Date').sort_values(by=0)[:10]
    return highest_gains_new

############################################################
if number_of_months == 1:
    dur = str(number_of_months) + ' MONTH'
else:
    dur = str(number_of_months) + ' MONTHS'

def barcharts(df):
    def get_color(value):
        if value >= 0:
            return "green"
        else:
            return "red"

    companies = df["Stock"]
    companies = [string.replace(".NS", " ") for string in companies]
    x = list(df.iloc[:, 0])
    y1 = companies

    dates = df["Date_Value"]
    repeats = df['count']
    max_repeat = df['count'].max()

    shades_of_green = ["#018749", "#006400"]

    color_condition1 = [shades_of_green[0] if value == max_repeat else "#DED93E" for value in repeats]
    #     color_condition2 = ["#DED93E" if value >= 0 else "red" for value in y2]
    #     color_condition3 = ["#59981A" if value >= 0 else "red" for value in y3]
    #     color_condition4 = ["#2F5233" if value >= 0 else "red" for value in y4]
    #     color_condition5 = ["black" if value >= 0 else "red" for value in y5]

    # Create the clustered bar chart
    fig = go.Figure(data=[
        go.Bar(x=x, y=y1, marker_color=color_condition1, orientation='h'),
        #         go.Bar(name=y2_label, x=x, y=y2, marker_color=color_condition2),
        #         go.Bar(name=y3_label, x=x, y=y3, marker_color=color_condition3 ),
        #         go.Bar(name=y4_label, x=x, y=y4, marker_color=color_condition4),
        #         go.Bar(name=y5_label, x=x, y=y5, marker_color=color_condition5)
    ])

    fig.update_layout(

        paper_bgcolor="white"  # Set background color to white

    )
    fig.update_layout(

        title_text=f"<b>HIGHEST ONE-DAY GAIN</b><br><sup><b>HIGHEST PRICE IN THE PAST {dur}</b>",
        # Title in capital letters
        title_x=0.5,  # Set horizontal position to the center
        title_xanchor="center",

        xaxis_title="<b>Change (in %)</b>",  # Label the x-axis
        # xaxis_tickangle=-90,
        yaxis_title="<b>STOCK</b>",  # Label the y-axis
        font_size=14,  # Set font size
        paper_bgcolor="white",  # Set background color to white
        plot_bgcolor="white",  # Set plot background color to white,

        font=dict(
            family="sans-serif",
            size=17,
            color="#05472A"
        )
    )
    # fig.add_hline(y=0)

    # Add text annotations for bar values
    fig.update_traces(
        text=dates,  # Use the deposit values as text
        textposition="auto",  # Position text outside the bars
        textfont_size=13,  # Set text font size
    )

    return fig
############################################################CHART CODE ENDS!




st.subheader("AUTOMOBILE SECTOR")
st.write(f"""Source: Historical data of the NIFTY Auto Index""")
df = data_create(NIFTY_AUTO)
st.plotly_chart(barcharts(df), use_container_width=True)


st.subheader("BANKING SECTOR")
st.write(f"""Source: Historical data of the NIFTY Bank Index""")
df = data_create(NIFTY_BANK)
st.plotly_chart(barcharts(df), use_container_width=True)


st.subheader("IT SECTOR")
st.write(f"""Source: Historical data of the NIFTY IT Index""")
df = data_create(NIFTY_IT)
st.plotly_chart(barcharts(df), use_container_width=True)


st.subheader("PHARMACEUTICAL SECTOR")
st.write(f"""Source: Historical data of the NIFTY PHARMA Index""")
df = data_create(NIFTY_PHARMA)
st.plotly_chart(barcharts(df), use_container_width=True)


st.subheader("FMCG SECTOR")
st.write(f"""Source: Historical data of the NIFTY FMCG Index""")

df = data_create(NIFTY_FMCG)
st.plotly_chart(barcharts(df), use_container_width=True)
