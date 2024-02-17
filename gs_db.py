import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

@st.cache_resource(show_spinner=False)
def init_gs_conn():
    # Creates and returns a Google Sheets connection object
    gs_conn = st.connection("gsheets", type=GSheetsConnection)
    return gs_conn

def update_gs(row):
    # Converts the input row into a pandas DataFrame - necessary for data manipulation and appending
    chat_history_row = pd.DataFrame([row])
    # Ensuring rows that have a minimal set of required data
    if chat_history_row.iloc[0].count() > 2:
        # Initializes the Google Sheets connection
        gs_conn = init_gs_conn()
        # Reads data from a specific worksheet named "chat-history", `ttl=0` disables caching for this read operation
        data = gs_conn.read(worksheet="chat-history", usecols=[0, 1, 2], show_spinner=False, ttl=0).dropna()
        # Concatenates the existing data with the new chat history row (appending the new row to the dataset)
        data = pd.concat([data, chat_history_row])
        # Writes the updated dataset back to the Google Sheet.
        gs_conn.update(worksheet="chat-history", data=data)


