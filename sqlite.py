__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from streamlit import logger
import sqlite3

app_logger = logger.get_logger('SMI_APP')
app_logger.info(f"sqlite version :{sqlite3.sqlite_version}")
app_logger.info(f"sys version :{sys.version}")