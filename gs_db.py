import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def init_gs_conn():
    gs_conn = st.connection("gsheets", type=GSheetsConnection)
    return gs_conn