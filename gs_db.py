import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

@st.cache_resource(show_spinner=False)
def init_gs_conn():
    gs_conn = st.connection("gsheets", type=GSheetsConnection)
    return gs_conn

def update_gs(row):
    chat_history_row = pd.DataFrame([row])
    if chat_history_row.iloc[0].count() > 2:
        gs_conn = init_gs_conn()
        data = gs_conn.read(worksheet="chat-history", usecols=[0, 1, 2], show_spinner=False, ttl=0).dropna()
        data = pd.concat([data, chat_history_row])
        gs_conn.update(worksheet="chat-history", data=data)


