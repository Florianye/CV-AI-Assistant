import pysqlite3
import sys
import os
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')