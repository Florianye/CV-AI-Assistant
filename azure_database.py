import pyodbc as odbc
import os
import dotenv
import streamlit as st

#@st.cache_resource(hash_funcs={odbc.connect: id})
def conn_database(server_name, database, db_username, db_password, streamlit=False):
    if streamlit == False:
        dotenv.load_dotenv(".env", override=True)
    else:
        os.environ["SERVER_NAME"] = server_name
        os.environ["DATABASE"] = database
        os.environ["DB_USERNAME"] = db_username
        os.environ["DB_PASSWORD"] = db_password

    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:%s,1433;Database=%s;Uid=%s;Pwd={%s};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;' % (os.environ["SERVER_NAME"], os.environ["DATABASE"], os.environ["DB_USERNAME"], os.environ["DB_PASSWORD"])
    conn = odbc.connect(connection_string)
    
    return conn